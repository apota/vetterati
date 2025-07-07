using MathNet.Numerics.LinearAlgebra;
using Vetterati.Shared.Models;
using System.Linq;
using Vetterati.AhpService.Data;

namespace Vetterati.AhpService.Services;

public interface IAhpScoringService
{
    Task<decimal> CalculateOverallScoreAsync(Guid jobProfileId, Guid candidateId);
    Task<Dictionary<string, decimal>> CalculateDetailedScoreAsync(Guid jobProfileId, Guid candidateId);
    Task<Matrix<double>> CalculateConsistencyRatioAsync(Guid jobProfileId);
    Task<bool> ValidateAhpMatrixAsync(Guid jobProfileId);
}

public class AhpScoringService : IAhpScoringService
{
    private readonly IJobProfileService _jobProfileService;
    private readonly ILogger<AhpScoringService> _logger;

    public AhpScoringService(IJobProfileService jobProfileService, ILogger<AhpScoringService> logger)
    {
        _jobProfileService = jobProfileService;
        _logger = logger;
    }

    public async Task<decimal> CalculateOverallScoreAsync(Guid jobProfileId, Guid candidateId)
    {
        try
        {
            var jobProfile = await _jobProfileService.GetJobProfileAsync(jobProfileId);
            if (jobProfile == null)
            {
                throw new ArgumentException($"Job profile {jobProfileId} not found");
            }

            // Get AHP criteria and their weights
            var criteria = await _jobProfileService.GetAhpCriteriaAsync(jobProfileId);
            var weights = await CalculateCriteriaWeightsAsync(jobProfileId);

            // Calculate scores for each criterion
            var criterionScores = new Dictionary<string, decimal>();
            decimal overallScore = 0;

            foreach (var criterion in criteria)
            {
                var score = await CalculateCriterionScoreAsync(criterion, candidateId);
                criterionScores[criterion.Name] = score;
                
                var weight = weights.ContainsKey(criterion.Name) ? weights[criterion.Name] : 0;
                overallScore += score * weight;
            }

            return Math.Round(overallScore, 4);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calculating overall score for candidate {CandidateId} and job {JobProfileId}", 
                candidateId, jobProfileId);
            throw;
        }
    }

    public async Task<Dictionary<string, decimal>> CalculateDetailedScoreAsync(Guid jobProfileId, Guid candidateId)
    {
        try
        {
            var criteria = await _jobProfileService.GetAhpCriteriaAsync(jobProfileId);
            var weights = await CalculateCriteriaWeightsAsync(jobProfileId);
            var detailedScores = new Dictionary<string, decimal>();

            foreach (var criterion in criteria)
            {
                var score = await CalculateCriterionScoreAsync(criterion, candidateId);
                var weight = weights.ContainsKey(criterion.Name) ? weights[criterion.Name] : 0;
                
                detailedScores[criterion.Name] = score * weight; // Store the weighted score
            }

            return detailedScores;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calculating detailed score for candidate {CandidateId} and job {JobProfileId}", 
                candidateId, jobProfileId);
            throw;
        }
    }

    public async Task<Matrix<double>> CalculateConsistencyRatioAsync(Guid jobProfileId)
    {
        try
        {
            var comparisons = await _jobProfileService.GetAhpComparisonsAsync(jobProfileId);
            var criteria = await _jobProfileService.GetAhpCriteriaAsync(jobProfileId);
            
            var comparisonsList = comparisons.ToList();
            var criteriaList = criteria.ToList();
            
            var n = criteriaList.Count;
            var matrix = Matrix<double>.Build.Dense(n, n, 1.0);

            // Build comparison matrix
            for (int i = 0; i < n; i++)
            {
                for (int j = 0; j < n; j++)
                {
                    if (i != j)
                    {
                        AhpComparison? comparison = null;
                        foreach (var c in comparisonsList)
                        {
                            if ((c.CriterionAId == criteriaList[i].Id && c.CriterionBId == criteriaList[j].Id) ||
                                (c.CriterionAId == criteriaList[j].Id && c.CriterionBId == criteriaList[i].Id))
                            {
                                comparison = c;
                                break;
                            }
                        }

                        if (comparison != null)
                        {
                            if (comparison.CriterionAId == criteriaList[i].Id)
                            {
                                matrix[i, j] = (double)comparison.ComparisonValue;
                                matrix[j, i] = 1.0 / (double)comparison.ComparisonValue;
                            }
                            else
                            {
                                matrix[i, j] = 1.0 / (double)comparison.ComparisonValue;
                                matrix[j, i] = (double)comparison.ComparisonValue;
                            }
                        }
                    }
                }
            }

            return matrix;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calculating consistency ratio for job profile {JobProfileId}", jobProfileId);
            throw;
        }
    }

    public async Task<bool> ValidateAhpMatrixAsync(Guid jobProfileId)
    {
        try
        {
            var matrix = await CalculateConsistencyRatioAsync(jobProfileId);
            var consistencyRatio = CalculateConsistencyRatio(matrix);
            
            // Consistency ratio should be less than 0.1 for acceptable consistency
            return consistencyRatio < 0.1;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating AHP matrix for job profile {JobProfileId}", jobProfileId);
            return false;
        }
    }

    private async Task<Dictionary<string, decimal>> CalculateCriteriaWeightsAsync(Guid jobProfileId)
    {
        try
        {
            var matrix = await CalculateConsistencyRatioAsync(jobProfileId);
            var criteria = await _jobProfileService.GetAhpCriteriaAsync(jobProfileId);
            var criteriaList = criteria.ToList();
            
            // Calculate principal eigenvector (weights)
            var eigenDecomposition = matrix.Evd();
            var eigenValues = eigenDecomposition.EigenValues;
            var eigenVectors = eigenDecomposition.EigenVectors;
            
            // Find the largest eigenvalue and its corresponding eigenvector
            var maxEigenValueIndex = 0;
            var maxEigenValue = eigenValues[0].Real;
            
            for (int i = 1; i < eigenValues.Count; i++)
            {
                if (eigenValues[i].Real > maxEigenValue)
                {
                    maxEigenValue = eigenValues[i].Real;
                    maxEigenValueIndex = i;
                }
            }
            
            var principalEigenVector = eigenVectors.Column(maxEigenValueIndex);
            
            // Normalize weights
            var weightSum = 0.0;
            var vectorLength = principalEigenVector.Count;
            for (int i = 0; i < vectorLength; i++)
            {
                var complexValue = principalEigenVector[i];
                double realValue = ((System.Numerics.Complex)complexValue).Real;
                weightSum += System.Math.Abs(realValue);
            }
            var weights = new Dictionary<string, decimal>();
            
            for (int i = 0; i < criteriaList.Count; i++)
            {
                var eigenValueComplex = principalEigenVector[i];
                double eigenValue = ((System.Numerics.Complex)eigenValueComplex).Real;
                var absEigenValue = System.Math.Abs(eigenValue);
                weights[criteriaList[i].Name] = (decimal)(absEigenValue / weightSum);
            }
            
            return weights;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calculating criteria weights for job profile {JobProfileId}", jobProfileId);
            throw;
        }
    }

    private async Task<decimal> CalculateCriterionScoreAsync(AhpCriterion criterion, Guid candidateId)
    {
        // This is a simplified scoring logic - in reality, this would be more complex
        // and would involve analyzing candidate data against the criterion
        
        switch (criterion.Name.ToLower())
        {
            case "technical_skills":
                return await CalculateTechnicalSkillsScoreAsync(candidateId);
            case "experience":
                return await CalculateExperienceScoreAsync(candidateId);
            case "education":
                return await CalculateEducationScoreAsync(candidateId);
            case "soft_skills":
                return await CalculateSoftSkillsScoreAsync(candidateId);
            case "cultural_fit":
                return await CalculateCulturalFitScoreAsync(candidateId);
            default:
                return 0.5m; // Default neutral score
        }
    }

    private async Task<decimal> CalculateTechnicalSkillsScoreAsync(Guid candidateId)
    {
        // Placeholder implementation - would analyze candidate's technical skills
        // against job requirements
        await Task.Delay(1); // Simulate async operation
        return 0.8m;
    }

    private async Task<decimal> CalculateExperienceScoreAsync(Guid candidateId)
    {
        // Placeholder implementation - would analyze years of experience,
        // relevance of previous roles, etc.
        await Task.Delay(1);
        return 0.75m;
    }

    private async Task<decimal> CalculateEducationScoreAsync(Guid candidateId)
    {
        // Placeholder implementation - would analyze education level,
        // institution prestige, field relevance, etc.
        await Task.Delay(1);
        return 0.7m;
    }

    private async Task<decimal> CalculateSoftSkillsScoreAsync(Guid candidateId)
    {
        // Placeholder implementation - would analyze soft skills
        // from resume text, assessments, etc.
        await Task.Delay(1);
        return 0.65m;
    }

    private async Task<decimal> CalculateCulturalFitScoreAsync(Guid candidateId)
    {
        // Placeholder implementation - would analyze cultural fit
        // based on various factors
        await Task.Delay(1);
        return 0.6m;
    }

    private double CalculateConsistencyRatio(Matrix<double> matrix)
    {
        var n = matrix.RowCount;
        
        // Random Index values for different matrix sizes
        var randomIndex = new double[] { 0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49 };
        
        if (n <= 2 || n > randomIndex.Length)
        {
            return 0; // Perfect consistency for 2x2 matrices or invalid size
        }
        
        // Calculate eigenvalues
        var eigenDecomposition = matrix.Evd();
        var eigenValues = eigenDecomposition.EigenValues;
        
        // Find maximum eigenvalue
        double maxEigenValue = 0.0;
        foreach (var eigenValue in eigenValues)
        {
            if (eigenValue.Real > maxEigenValue)
            {
                maxEigenValue = eigenValue.Real;
            }
        }
        
        // Calculate Consistency Index
        var consistencyIndex = (maxEigenValue - n) / (n - 1);
        
        // Calculate Consistency Ratio
        var consistencyRatio = consistencyIndex / randomIndex[n - 1];
        
        return consistencyRatio;
    }
}

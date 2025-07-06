using Microsoft.EntityFrameworkCore;
using Vetterati.AhpService.Data;
using Vetterati.Shared.Models.Entities;

namespace Vetterati.AhpService.Services;

public interface IJobProfileService
{
    Task<JobProfile?> GetJobProfileAsync(Guid jobProfileId);
    Task<IEnumerable<AhpCriterion>> GetAhpCriteriaAsync(Guid jobProfileId);
    Task<IEnumerable<AhpComparison>> GetAhpComparisonsAsync(Guid jobProfileId);
    Task<JobProfile> CreateJobProfileAsync(JobProfile jobProfile);
    Task<JobProfile> UpdateJobProfileAsync(JobProfile jobProfile);
    Task<bool> DeleteJobProfileAsync(Guid jobProfileId);
    Task<AhpCriterion> CreateAhpCriterionAsync(AhpCriterion criterion);
    Task<AhpComparison> CreateAhpComparisonAsync(AhpComparison comparison);
    Task<bool> UpdateAhpComparisonAsync(Guid comparisonId, decimal value);
}

public class JobProfileService : IJobProfileService
{
    private readonly AhpDbContext _context;
    private readonly ILogger<JobProfileService> _logger;

    public JobProfileService(AhpDbContext context, ILogger<JobProfileService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<JobProfile?> GetJobProfileAsync(Guid jobProfileId)
    {
        return await _context.JobProfiles
            .FirstOrDefaultAsync(jp => jp.Id == jobProfileId);
    }

    public async Task<IEnumerable<AhpCriterion>> GetAhpCriteriaAsync(Guid jobProfileId)
    {
        return await _context.AhpCriteria
            .Where(c => c.JobProfileId == jobProfileId)
            .OrderBy(c => c.Name)
            .ToListAsync();
    }

    public async Task<IEnumerable<AhpComparison>> GetAhpComparisonsAsync(Guid jobProfileId)
    {
        return await _context.AhpComparisons
            .Include(c => c.CriterionA)
            .Include(c => c.CriterionB)
            .Where(c => c.JobProfileId == jobProfileId)
            .ToListAsync();
    }

    public async Task<JobProfile> CreateJobProfileAsync(JobProfile jobProfile)
    {
        try
        {
            _context.JobProfiles.Add(jobProfile);
            await _context.SaveChangesAsync();
            
            _logger.LogInformation("Created job profile {JobProfileId}", jobProfile.Id);
            return jobProfile;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating job profile");
            throw;
        }
    }

    public async Task<JobProfile> UpdateJobProfileAsync(JobProfile jobProfile)
    {
        try
        {
            _context.JobProfiles.Update(jobProfile);
            await _context.SaveChangesAsync();
            
            _logger.LogInformation("Updated job profile {JobProfileId}", jobProfile.Id);
            return jobProfile;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating job profile {JobProfileId}", jobProfile.Id);
            throw;
        }
    }

    public async Task<bool> DeleteJobProfileAsync(Guid jobProfileId)
    {
        try
        {
            var jobProfile = await _context.JobProfiles.FindAsync(jobProfileId);
            if (jobProfile == null)
            {
                return false;
            }

            _context.JobProfiles.Remove(jobProfile);
            await _context.SaveChangesAsync();
            
            _logger.LogInformation("Deleted job profile {JobProfileId}", jobProfileId);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting job profile {JobProfileId}", jobProfileId);
            throw;
        }
    }

    public async Task<AhpCriterion> CreateAhpCriterionAsync(AhpCriterion criterion)
    {
        try
        {
            _context.AhpCriteria.Add(criterion);
            await _context.SaveChangesAsync();
            
            _logger.LogInformation("Created AHP criterion {CriterionId} for job profile {JobProfileId}", 
                criterion.Id, criterion.JobProfileId);
            return criterion;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating AHP criterion for job profile {JobProfileId}", 
                criterion.JobProfileId);
            throw;
        }
    }

    public async Task<AhpComparison> CreateAhpComparisonAsync(AhpComparison comparison)
    {
        try
        {
            _context.AhpComparisons.Add(comparison);
            await _context.SaveChangesAsync();
            
            _logger.LogInformation("Created AHP comparison {ComparisonId} for job profile {JobProfileId}", 
                comparison.Id, comparison.JobProfileId);
            return comparison;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating AHP comparison for job profile {JobProfileId}", 
                comparison.JobProfileId);
            throw;
        }
    }

    public async Task<bool> UpdateAhpComparisonAsync(Guid comparisonId, decimal value)
    {
        try
        {
            var comparison = await _context.AhpComparisons.FindAsync(comparisonId);
            if (comparison == null)
            {
                return false;
            }

            comparison.ComparisonValue = value;
            comparison.UpdatedAt = DateTime.UtcNow;
            
            await _context.SaveChangesAsync();
            
            _logger.LogInformation("Updated AHP comparison {ComparisonId} with value {Value}", 
                comparisonId, value);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating AHP comparison {ComparisonId}", comparisonId);
            throw;
        }
    }
}

using Microsoft.AspNetCore.Mvc;
using Vetterati.AhpService.Services;
using Vetterati.Shared.Models;

namespace Vetterati.AhpService.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ScoringController : ControllerBase
{
    private readonly IAhpScoringService _scoringService;
    private readonly ICandidateMatchingService _matchingService;
    private readonly ILogger<ScoringController> _logger;

    public ScoringController(
        IAhpScoringService scoringService,
        ICandidateMatchingService matchingService,
        ILogger<ScoringController> logger)
    {
        _scoringService = scoringService;
        _matchingService = matchingService;
        _logger = logger;
    }

    [HttpPost("calculate")]
    public async Task<ActionResult<CandidateScoreResponse>> CalculateScore(
        [FromBody] CalculateScoreRequest request)
    {
        try
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var score = await _matchingService.ScoreCandidateAsync(request.JobProfileId, request.CandidateId);
            
            var response = new CandidateScoreResponse
            {
                Id = score.Id,
                JobProfileId = score.JobProfileId,
                CandidateId = score.CandidateId,
                OverallScore = score.OverallScore,
                ScoreBreakdown = score.ScoreBreakdown,
                ScoredAt = score.ScoredAt
            };

            return Ok(response);
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Invalid request for score calculation");
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calculating score for candidate {CandidateId} and job {JobProfileId}", 
                request.CandidateId, request.JobProfileId);
            return StatusCode(500, "An error occurred while calculating the score");
        }
    }

    [HttpGet("{jobProfileId}/candidates/{candidateId}")]
    public async Task<ActionResult<CandidateScoreResponse>> GetCandidateScore(
        Guid jobProfileId, 
        Guid candidateId)
    {
        try
        {
            var score = await _matchingService.GetCandidateScoreAsync(jobProfileId, candidateId);
            
            if (score == null)
            {
                return NotFound($"No score found for candidate {candidateId} and job profile {jobProfileId}");
            }

            var response = new CandidateScoreResponse
            {
                Id = score.Id,
                JobProfileId = score.JobProfileId,
                CandidateId = score.CandidateId,
                OverallScore = score.OverallScore,
                ScoreBreakdown = score.ScoreBreakdown,
                ScoredAt = score.ScoredAt
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting score for candidate {CandidateId} and job {JobProfileId}", 
                candidateId, jobProfileId);
            return StatusCode(500, "An error occurred while retrieving the score");
        }
    }

    [HttpGet("{jobProfileId}/top-candidates")]
    public async Task<ActionResult<IEnumerable<CandidateScoreResponse>>> GetTopCandidates(
        Guid jobProfileId,
        [FromQuery] int limit = 10)
    {
        try
        {
            if (limit <= 0 || limit > 100)
            {
                return BadRequest("Limit must be between 1 and 100");
            }

            var scores = await _matchingService.GetTopCandidatesAsync(jobProfileId, limit);
            
            var response = scores.Select(score => new CandidateScoreResponse
            {
                Id = score.Id,
                JobProfileId = score.JobProfileId,
                CandidateId = score.CandidateId,
                OverallScore = score.OverallScore,
                ScoreBreakdown = score.ScoreBreakdown,
                ScoredAt = score.ScoredAt
            });

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting top candidates for job profile {JobProfileId}", jobProfileId);
            return StatusCode(500, "An error occurred while retrieving top candidates");
        }
    }

    [HttpPost("{jobProfileId}/score-all")]
    public async Task<ActionResult<ScoreAllCandidatesResponse>> ScoreAllCandidates(Guid jobProfileId)
    {
        try
        {
            var scores = await _matchingService.ScoreAllCandidatesAsync(jobProfileId);
            
            var response = new ScoreAllCandidatesResponse
            {
                JobProfileId = jobProfileId,
                CandidatesScored = scores.Count(),
                AverageScore = scores.Any() ? scores.Average(s => s.OverallScore) : 0,
                ProcessedAt = DateTime.UtcNow
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error scoring all candidates for job profile {JobProfileId}", jobProfileId);
            return StatusCode(500, "An error occurred while scoring candidates");
        }
    }

    [HttpPost("{jobProfileId}/refresh-scores")]
    public async Task<ActionResult<RefreshScoresResponse>> RefreshScores(Guid jobProfileId)
    {
        try
        {
            var success = await _matchingService.RefreshScoresAsync(jobProfileId);
            
            var response = new RefreshScoresResponse
            {
                JobProfileId = jobProfileId,
                Success = success,
                RefreshedAt = DateTime.UtcNow
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refreshing scores for job profile {JobProfileId}", jobProfileId);
            return StatusCode(500, "An error occurred while refreshing scores");
        }
    }

    [HttpGet("{jobProfileId}/validate-matrix")]
    public async Task<ActionResult<ValidateMatrixResponse>> ValidateAhpMatrix(Guid jobProfileId)
    {
        try
        {
            var isValid = await _scoringService.ValidateAhpMatrixAsync(jobProfileId);
            
            var response = new ValidateMatrixResponse
            {
                JobProfileId = jobProfileId,
                IsValid = isValid,
                ValidatedAt = DateTime.UtcNow
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating AHP matrix for job profile {JobProfileId}", jobProfileId);
            return StatusCode(500, "An error occurred while validating the AHP matrix");
        }
    }
}

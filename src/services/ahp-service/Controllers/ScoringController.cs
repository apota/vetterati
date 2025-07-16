using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Vetterati.AhpService.Services;
using Vetterati.AhpService.Data;
using Vetterati.Shared.Models;
using System.Text.Json;

namespace Vetterati.AhpService.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ScoringController : ControllerBase
{
    private readonly IAhpScoringService _scoringService;
    private readonly ICandidateMatchingService _matchingService;
    private readonly AhpDbContext _context;
    private readonly ILogger<ScoringController> _logger;

    public ScoringController(
        IAhpScoringService scoringService,
        ICandidateMatchingService matchingService,
        AhpDbContext context,
        ILogger<ScoringController> logger)
    {
        _scoringService = scoringService;
        _matchingService = matchingService;
        _context = context;
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
                ScoreBreakdown = string.IsNullOrEmpty(score.ScoreBreakdown) 
                    ? new Dictionary<string, object>() 
                    : JsonSerializer.Deserialize<Dictionary<string, object>>(score.ScoreBreakdown) ?? new Dictionary<string, object>(),
                ScoredAt = score.ScoredAt,
                CalculatedAt = score.CalculatedAt,
                Methodology = score.Methodology ?? string.Empty
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
                ScoreBreakdown = string.IsNullOrEmpty(score.ScoreBreakdown) 
                    ? new Dictionary<string, object>() 
                    : JsonSerializer.Deserialize<Dictionary<string, object>>(score.ScoreBreakdown) ?? new Dictionary<string, object>(),
                ScoredAt = score.ScoredAt,
                CalculatedAt = score.CalculatedAt,
                Methodology = score.Methodology ?? string.Empty
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
                ScoreBreakdown = string.IsNullOrEmpty(score.ScoreBreakdown) 
                    ? new Dictionary<string, object>() 
                    : JsonSerializer.Deserialize<Dictionary<string, object>>(score.ScoreBreakdown) ?? new Dictionary<string, object>(),
                ScoredAt = score.ScoredAt,
                CalculatedAt = score.CalculatedAt,
                Methodology = score.Methodology ?? string.Empty
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

    [HttpGet("matches")]
    public async Task<ActionResult<PaginatedCandidateMatchesResponse>> GetAllCandidateMatches(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 10,
        [FromQuery] string sortBy = "score",
        [FromQuery] string sortOrder = "desc",
        [FromQuery] decimal? minScore = null,
        [FromQuery] decimal? maxScore = null,
        [FromQuery] List<Guid>? jobProfileIds = null,
        [FromQuery] List<Guid>? candidateIds = null,
        [FromQuery] DateTime? dateFrom = null,
        [FromQuery] DateTime? dateTo = null)
    {
        try
        {
            if (page < 1) page = 1;
            if (pageSize < 1) pageSize = 10;
            if (pageSize > 100) pageSize = 100;

            var query = _context.CandidateScores.AsQueryable();

            // Apply filters
            if (minScore.HasValue)
                query = query.Where(cs => cs.OverallScore >= minScore.Value);
            
            if (maxScore.HasValue)
                query = query.Where(cs => cs.OverallScore <= maxScore.Value);

            if (jobProfileIds != null && jobProfileIds.Any())
                query = query.Where(cs => jobProfileIds.Contains(cs.JobProfileId));

            if (candidateIds != null && candidateIds.Any())
                query = query.Where(cs => candidateIds.Contains(cs.CandidateId));

            if (dateFrom.HasValue)
                query = query.Where(cs => cs.CalculatedAt >= dateFrom.Value);

            if (dateTo.HasValue)
                query = query.Where(cs => cs.CalculatedAt <= dateTo.Value);

            // Apply sorting
            query = sortBy.ToLower() switch
            {
                "score" => sortOrder.ToLower() == "asc" 
                    ? query.OrderBy(cs => cs.OverallScore)
                    : query.OrderByDescending(cs => cs.OverallScore),
                "calculatedat" => sortOrder.ToLower() == "asc"
                    ? query.OrderBy(cs => cs.CalculatedAt)
                    : query.OrderByDescending(cs => cs.CalculatedAt),
                _ => query.OrderByDescending(cs => cs.OverallScore)
            };

            var totalCount = await query.CountAsync();
            var totalPages = (int)Math.Ceiling((double)totalCount / pageSize);

            var matches = await query
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToListAsync();

            var response = new PaginatedCandidateMatchesResponse
            {
                Matches = matches.Select(match => new CandidateMatchItem
                {
                    Id = match.Id,
                    CandidateId = match.CandidateId,
                    JobProfileId = match.JobProfileId,
                    CandidateName = $"Candidate {match.CandidateId.ToString().Substring(0, 8)}",
                    JobTitle = $"Position {match.JobProfileId.ToString().Substring(0, 8)}",
                    OverallScore = match.OverallScore,
                    MatchPercentage = (int)Math.Round(match.OverallScore * 100),
                    CriteriaScores = string.IsNullOrEmpty(match.ScoreBreakdown) 
                        ? new Dictionary<string, decimal>() 
                        : JsonSerializer.Deserialize<Dictionary<string, decimal>>(match.ScoreBreakdown) ?? new Dictionary<string, decimal>(),
                    ScoreBreakdown = string.IsNullOrEmpty(match.ScoreBreakdown) 
                        ? new Dictionary<string, object>() 
                        : JsonSerializer.Deserialize<Dictionary<string, object>>(match.ScoreBreakdown) ?? new Dictionary<string, object>(),
                    CalculatedAt = match.CalculatedAt,
                    ScoredAt = match.ScoredAt,
                    Methodology = match.Methodology ?? "AHP"
                }).ToList(),
                TotalCount = totalCount,
                CurrentPage = page,
                PageSize = pageSize,
                TotalPages = totalPages,
                HasNextPage = page < totalPages,
                HasPreviousPage = page > 1,
                Summary = new CandidateMatchSummaryResponse
                {
                    TotalMatches = totalCount,
                    AverageScore = matches.Any() ? matches.Average(m => m.OverallScore) : 0,
                    HighestScore = matches.Any() ? matches.Max(m => m.OverallScore) : 0,
                    LowestScore = matches.Any() ? matches.Min(m => m.OverallScore) : 0,
                    MatchedJobs = matches.Select(m => m.JobProfileId).Distinct().Count()
                }
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting candidate matches");
            return StatusCode(500, "An error occurred while retrieving candidate matches");
        }
    }
}

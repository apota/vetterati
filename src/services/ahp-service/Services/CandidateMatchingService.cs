using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Caching.Distributed;
using System.Text.Json;
using Vetterati.AhpService.Data;
using Vetterati.Shared.Models.Entities;

namespace Vetterati.AhpService.Services;

public interface ICandidateMatchingService
{
    Task<IEnumerable<CandidateScore>> GetTopCandidatesAsync(Guid jobProfileId, int limit = 10);
    Task<CandidateScore> ScoreCandidateAsync(Guid jobProfileId, Guid candidateId);
    Task<IEnumerable<CandidateScore>> ScoreAllCandidatesAsync(Guid jobProfileId);
    Task<CandidateScore?> GetCandidateScoreAsync(Guid jobProfileId, Guid candidateId);
    Task<bool> RefreshScoresAsync(Guid jobProfileId);
}

public class CandidateMatchingService : ICandidateMatchingService
{
    private readonly AhpDbContext _context;
    private readonly IAhpScoringService _scoringService;
    private readonly IDistributedCache _cache;
    private readonly ILogger<CandidateMatchingService> _logger;

    public CandidateMatchingService(
        AhpDbContext context,
        IAhpScoringService scoringService,
        IDistributedCache cache,
        ILogger<CandidateMatchingService> logger)
    {
        _context = context;
        _scoringService = scoringService;
        _cache = cache;
        _logger = logger;
    }

    public async Task<IEnumerable<CandidateScore>> GetTopCandidatesAsync(Guid jobProfileId, int limit = 10)
    {
        try
        {
            var cacheKey = $"top_candidates_{jobProfileId}_{limit}";
            var cachedResult = await _cache.GetStringAsync(cacheKey);
            
            if (!string.IsNullOrEmpty(cachedResult))
            {
                var cached = JsonSerializer.Deserialize<IEnumerable<CandidateScore>>(cachedResult);
                if (cached != null)
                {
                    _logger.LogInformation("Retrieved top candidates from cache for job profile {JobProfileId}", jobProfileId);
                    return cached;
                }
            }

            var topCandidates = await _context.CandidateScores
                .Where(cs => cs.JobProfileId == jobProfileId)
                .OrderByDescending(cs => cs.OverallScore)
                .Take(limit)
                .ToListAsync();

            // Cache for 30 minutes
            var cacheOptions = new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(30)
            };
            
            await _cache.SetStringAsync(cacheKey, JsonSerializer.Serialize(topCandidates), cacheOptions);
            
            _logger.LogInformation("Retrieved top {Count} candidates for job profile {JobProfileId}", 
                topCandidates.Count, jobProfileId);
            
            return topCandidates;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting top candidates for job profile {JobProfileId}", jobProfileId);
            throw;
        }
    }

    public async Task<CandidateScore> ScoreCandidateAsync(Guid jobProfileId, Guid candidateId)
    {
        try
        {
            // Check if score already exists
            var existingScore = await _context.CandidateScores
                .FirstOrDefaultAsync(cs => cs.JobProfileId == jobProfileId && cs.CandidateId == candidateId);

            // Calculate new scores
            var overallScore = await _scoringService.CalculateOverallScoreAsync(jobProfileId, candidateId);
            var detailedScores = await _scoringService.CalculateDetailedScoreAsync(jobProfileId, candidateId);

            if (existingScore != null)
            {
                // Update existing score
                existingScore.OverallScore = overallScore;
                existingScore.ScoreBreakdown = JsonSerializer.Serialize(detailedScores);
                existingScore.ScoredAt = DateTime.UtcNow;
                existingScore.UpdatedAt = DateTime.UtcNow;
                
                _context.CandidateScores.Update(existingScore);
            }
            else
            {
                // Create new score
                existingScore = new CandidateScore
                {
                    Id = Guid.NewGuid(),
                    JobProfileId = jobProfileId,
                    CandidateId = candidateId,
                    OverallScore = overallScore,
                    ScoreBreakdown = JsonSerializer.Serialize(detailedScores),
                    ScoredAt = DateTime.UtcNow,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                };
                
                _context.CandidateScores.Add(existingScore);
            }

            await _context.SaveChangesAsync();
            
            // Invalidate cache
            await InvalidateCacheAsync(jobProfileId);
            
            _logger.LogInformation("Scored candidate {CandidateId} for job profile {JobProfileId} with score {Score}", 
                candidateId, jobProfileId, overallScore);
            
            return existingScore;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error scoring candidate {CandidateId} for job profile {JobProfileId}", 
                candidateId, jobProfileId);
            throw;
        }
    }

    public async Task<IEnumerable<CandidateScore>> ScoreAllCandidatesAsync(Guid jobProfileId)
    {
        try
        {
            // Get all candidates that need scoring
            var candidatesNeedingScoring = await _context.CandidateProfiles
                .Where(cp => !_context.CandidateScores
                    .Any(cs => cs.JobProfileId == jobProfileId && cs.CandidateId == cp.Id))
                .ToListAsync();

            var scores = new List<CandidateScore>();

            foreach (var candidate in candidatesNeedingScoring)
            {
                try
                {
                    var score = await ScoreCandidateAsync(jobProfileId, candidate.Id);
                    scores.Add(score);
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Failed to score candidate {CandidateId} for job profile {JobProfileId}", 
                        candidate.Id, jobProfileId);
                }
            }

            _logger.LogInformation("Scored {Count} candidates for job profile {JobProfileId}", 
                scores.Count, jobProfileId);
            
            return scores;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error scoring all candidates for job profile {JobProfileId}", jobProfileId);
            throw;
        }
    }

    public async Task<CandidateScore?> GetCandidateScoreAsync(Guid jobProfileId, Guid candidateId)
    {
        try
        {
            var score = await _context.CandidateScores
                .FirstOrDefaultAsync(cs => cs.JobProfileId == jobProfileId && cs.CandidateId == candidateId);

            if (score == null)
            {
                _logger.LogInformation("No score found for candidate {CandidateId} and job profile {JobProfileId}", 
                    candidateId, jobProfileId);
            }

            return score;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting candidate score for {CandidateId} and job profile {JobProfileId}", 
                candidateId, jobProfileId);
            throw;
        }
    }

    public async Task<bool> RefreshScoresAsync(Guid jobProfileId)
    {
        try
        {
            // Get all existing scores for this job profile
            var existingScores = await _context.CandidateScores
                .Where(cs => cs.JobProfileId == jobProfileId)
                .ToListAsync();

            var refreshedCount = 0;

            foreach (var score in existingScores)
            {
                try
                {
                    await ScoreCandidateAsync(jobProfileId, score.CandidateId);
                    refreshedCount++;
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Failed to refresh score for candidate {CandidateId} and job profile {JobProfileId}", 
                        score.CandidateId, jobProfileId);
                }
            }

            _logger.LogInformation("Refreshed {Count} scores for job profile {JobProfileId}", 
                refreshedCount, jobProfileId);
            
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refreshing scores for job profile {JobProfileId}", jobProfileId);
            return false;
        }
    }

    private async Task InvalidateCacheAsync(Guid jobProfileId)
    {
        try
        {
            // Invalidate related cache entries
            var cacheKeys = new[]
            {
                $"top_candidates_{jobProfileId}_10",
                $"top_candidates_{jobProfileId}_20",
                $"top_candidates_{jobProfileId}_50"
            };

            foreach (var key in cacheKeys)
            {
                await _cache.RemoveAsync(key);
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error invalidating cache for job profile {JobProfileId}", jobProfileId);
        }
    }
}

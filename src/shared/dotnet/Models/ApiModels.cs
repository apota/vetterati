using System;
using System.Collections.Generic;

namespace Vetterati.Shared.Models;

public class ApiResponse<T>
{
    public T? Data { get; set; }
    public ApiMeta Meta { get; set; } = new();
    public ApiPagination? Pagination { get; set; }
    public ApiLinks? Links { get; set; }
}

public class ApiError
{
    public string Code { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public List<ApiErrorDetail> Details { get; set; } = new();
    public string RequestId { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public class ApiErrorDetail
{
    public string Field { get; set; } = string.Empty;
    public string Code { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
}

public class ApiMeta
{
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string Version { get; set; } = "1.0.0";
    public string RequestId { get; set; } = Guid.NewGuid().ToString();
}

public class ApiPagination
{
    public int Page { get; set; }
    public int PerPage { get; set; }
    public int Total { get; set; }
    public int TotalPages { get; set; }
}

public class ApiLinks
{
    public string? Self { get; set; }
    public string? Next { get; set; }
    public string? Previous { get; set; }
    public string? First { get; set; }
    public string? Last { get; set; }
}

// DTOs for API requests/responses
public class LoginRequest
{
    public string Provider { get; set; } = string.Empty;
    public string Code { get; set; } = string.Empty;
    public string RedirectUri { get; set; } = string.Empty;
}

public class LoginResponse
{
    public string AccessToken { get; set; } = string.Empty;
    public string RefreshToken { get; set; } = string.Empty;
    public int ExpiresIn { get; set; }
    public string TokenType { get; set; } = "Bearer";
    public User User { get; set; } = new();
}

public class RefreshTokenRequest
{
    public string RefreshToken { get; set; } = string.Empty;
}

public class CreateJobRequest
{
    public string Title { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? Department { get; set; }
    public string? Location { get; set; }
    public string? EmploymentType { get; set; }
    public string? JobLevel { get; set; }
    public Dictionary<string, object> Requirements { get; set; } = new();
    public Dictionary<string, object> Benefits { get; set; } = new();
}

public class CreateCandidateRequest
{
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string? Email { get; set; }
    public string? Phone { get; set; }
    public Dictionary<string, object> Location { get; set; } = new();
    public string? LinkedInUrl { get; set; }
    public string? PortfolioUrl { get; set; }
    public List<Dictionary<string, object>> Experience { get; set; } = new();
    public List<Dictionary<string, object>> Education { get; set; } = new();
    public Dictionary<string, object> Skills { get; set; } = new();
}

public class CandidateSearchRequest
{
    public string? Query { get; set; }
    public List<string> Skills { get; set; } = new();
    public string? Location { get; set; }
    public int? ExperienceMin { get; set; }
    public int? ExperienceMax { get; set; }
    public string? EducationLevel { get; set; }
    public string? Company { get; set; }
    public int Page { get; set; } = 1;
    public int PerPage { get; set; } = 20;
    public string SortBy { get; set; } = "relevance";
    public string SortOrder { get; set; } = "desc";
}

public class ScoreCandidateRequest
{
    public Guid JobId { get; set; }
    public Guid? AhpHierarchyId { get; set; }
    public bool ForceRecalculate { get; set; } = false;
}

// AHP Service API Models
public class CalculateScoreRequest
{
    public Guid CandidateId { get; set; }
    public Guid JobProfileId { get; set; }
    public Dictionary<string, object>? CandidateData { get; set; }
    public Dictionary<string, object>? Options { get; set; }
}

public class CandidateScoreResponse
{
    public Guid Id { get; set; }
    public Guid CandidateId { get; set; }
    public Guid JobProfileId { get; set; }
    public decimal OverallScore { get; set; }
    public Dictionary<string, decimal> CriteriaScores { get; set; } = new();
    public Dictionary<string, object> ScoreBreakdown { get; set; } = new();
    public string Methodology { get; set; } = string.Empty;
    public DateTime CalculatedAt { get; set; }
    public DateTime ScoredAt { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
}

public class CreateJobProfileRequest
{
    public Guid JobId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public List<CriterionRequest> Criteria { get; set; } = new();
}

public class CriterionRequest
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public decimal Weight { get; set; }
    public int Priority { get; set; }
    public string? Category { get; set; }
}

public class ComparisonRequest
{
    public Guid CriterionAId { get; set; }
    public Guid CriterionBId { get; set; }
    public decimal Value { get; set; }
    public string? Justification { get; set; }
}

public class CandidateMatchRequest
{
    public Guid JobProfileId { get; set; }
    public List<Guid>? CandidateIds { get; set; }
    public Dictionary<string, object>? Filters { get; set; }
    public Dictionary<string, object>? Options { get; set; }
}

public class CandidateMatchResponse
{
    public List<CandidateScoreResponse> Matches { get; set; } = new();
    public Dictionary<string, object> MatchStatistics { get; set; } = new();
    public DateTime MatchedAt { get; set; }
}

public class ScoreAllCandidatesResponse
{
    public Guid JobProfileId { get; set; }
    public int CandidatesScored { get; set; }
    public decimal AverageScore { get; set; }
    public DateTime ScoredAt { get; set; } = DateTime.UtcNow;
    public DateTime ProcessedAt { get; set; } = DateTime.UtcNow;
    public Dictionary<string, object>? Statistics { get; set; }
}

public class RefreshScoresResponse
{
    public Guid JobProfileId { get; set; }
    public bool Success { get; set; }
    public DateTime RefreshedAt { get; set; } = DateTime.UtcNow;
    public int CandidatesRefreshed { get; set; }
}

public class ValidateMatrixResponse
{
    public Guid JobProfileId { get; set; }
    public bool IsValid { get; set; }
    public DateTime ValidatedAt { get; set; } = DateTime.UtcNow;
    public List<string>? ValidationErrors { get; set; }
    public Dictionary<string, object>? MatrixMetrics { get; set; }
}

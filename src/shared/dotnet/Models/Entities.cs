using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Vetterati.Shared.Models;

public class BaseEntity
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}

public class User : BaseEntity
{
    public string Email { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? SsoProvider { get; set; }
    public string? SsoId { get; set; }
    public List<string> Roles { get; set; } = new();
    public bool IsActive { get; set; } = true;
    public DateTime? LastLoginAt { get; set; }
    public Dictionary<string, object> Preferences { get; set; } = new();
}

public class Organization : BaseEntity
{
    public string Name { get; set; } = string.Empty;
    public string? Domain { get; set; }
    public Dictionary<string, object> Settings { get; set; } = new();
}

public class Job : BaseEntity
{
    public Guid OrganizationId { get; set; }
    public string Title { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? Department { get; set; }
    public string? Location { get; set; }
    public string? JobLevel { get; set; }
    public string? EmploymentType { get; set; }
    public string Status { get; set; } = "draft";
    public Guid CreatedBy { get; set; }
    public DateTime? PostedAt { get; set; }
    public DateTime? ClosedAt { get; set; }
    public Dictionary<string, object> Requirements { get; set; } = new();
    public Dictionary<string, object> Benefits { get; set; } = new();
}

public class Candidate : BaseEntity
{
    public Guid OrganizationId { get; set; }
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
    public Dictionary<string, object> CareerMetrics { get; set; } = new();
    
    [JsonIgnore]
    public string FullName => $"{FirstName} {LastName}".Trim();
}

public class ResumeFile : BaseEntity
{
    public Guid CandidateId { get; set; }
    public string FileName { get; set; } = string.Empty;
    public string? FileType { get; set; }
    public long FileSize { get; set; }
    public string? StoragePath { get; set; }
    public string? UploadSource { get; set; }
    public DateTime UploadDate { get; set; } = DateTime.UtcNow;
    public string ProcessingStatus { get; set; } = "pending";
    public Dictionary<string, object> ParsingResults { get; set; } = new();
    public decimal? QualityScore { get; set; }
}

public class AhpHierarchy : BaseEntity
{
    public Guid JobId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public Dictionary<string, object> Hierarchy { get; set; } = new();
    public Dictionary<string, object> PairwiseMatrices { get; set; } = new();
    public Dictionary<string, object> ConsistencyRatios { get; set; } = new();
    public bool IsActive { get; set; } = true;
}

public class IdealCandidateProfile : BaseEntity
{
    public Guid JobId { get; set; }
    public Guid AhpHierarchyId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Archetype { get; set; }
    public int Weight { get; set; } = 100;
    public Dictionary<string, object> TargetValues { get; set; } = new();
    public Dictionary<string, object> Tolerances { get; set; } = new();
    public string? Description { get; set; }
    public bool IsActive { get; set; } = true;
}

// AHP-related entities
public class AhpCriterion : BaseEntity
{
    public Guid JobProfileId { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public decimal Weight { get; set; }
    public int Priority { get; set; }
}

public class AhpComparison : BaseEntity
{
    public Guid JobProfileId { get; set; }
    public Guid CriterionAId { get; set; }
    public Guid CriterionBId { get; set; }
    public decimal ComparisonValue { get; set; }
    
    // Navigation properties
    public AhpCriterion? CriterionA { get; set; }
    public AhpCriterion? CriterionB { get; set; }
}

public class CandidateScore : BaseEntity
{
    public Guid CandidateId { get; set; }
    public Guid JobId { get; set; }
    public Guid AhpHierarchyId { get; set; }
    public decimal OverallScore { get; set; }
    public List<Dictionary<string, object>> ProfileMatches { get; set; } = new();
    public List<Dictionary<string, object>> AttributeScores { get; set; } = new();
    public Dictionary<string, object> Explanation { get; set; } = new();
    public DateTime CalculatedAt { get; set; } = DateTime.UtcNow;
    public Dictionary<string, object> Metadata { get; set; } = new();
}

public class Interview : BaseEntity
{
    public Guid CandidateWorkflowId { get; set; }
    public Guid CandidateId { get; set; }
    public Guid JobId { get; set; }
    public string? StageId { get; set; }
    public string? Title { get; set; }
    public string? Description { get; set; }
    public string? Type { get; set; }
    public string Status { get; set; } = "scheduled";
    public Dictionary<string, object> Scheduling { get; set; } = new();
    public Dictionary<string, object> Participants { get; set; } = new();
    public Dictionary<string, object> Content { get; set; } = new();
    public Dictionary<string, object> Evaluation { get; set; } = new();
}

public class JobProfile : BaseEntity
{
    public Guid JobId { get; set; }
    public string Title { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? Department { get; set; }
    public string? Location { get; set; }
    public string? JobLevel { get; set; }
    public string? EmploymentType { get; set; }
    public string Status { get; set; } = "draft";
    public Guid CreatedBy { get; set; }
    public DateTime? PostedAt { get; set; }
    public DateTime? ClosedAt { get; set; }
    public string? RequiredSkills { get; set; } // JSON serialized
    public string? PreferredSkills { get; set; } // JSON serialized
    public string? JobResponsibilities { get; set; } // JSON serialized
    public string? AhpCriteria { get; set; } // JSON serialized AHP criteria weights
}

public class CandidateProfile : BaseEntity
{
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string? Email { get; set; }
    public string? Phone { get; set; }
    public string? Location { get; set; } // JSON serialized location data
    public string? LinkedInUrl { get; set; }
    public string? PortfolioUrl { get; set; }
    public string? Summary { get; set; }
    public string? Experience { get; set; } // JSON serialized experience array
    public string? Education { get; set; } // JSON serialized education array
    public string? Skills { get; set; } // JSON serialized skills object
    public decimal? TotalYearsExperience { get; set; }
    public decimal? AverageTenure { get; set; }
    public decimal? CareerProgressionScore { get; set; }
    public string? Source { get; set; }
    public string? SourceDetails { get; set; } // JSON serialized
    public decimal? ParsingConfidence { get; set; }
    public string? ParsingMetadata { get; set; } // JSON serialized
}

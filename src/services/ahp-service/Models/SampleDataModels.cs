using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Vetterati.AhpService.Models;

[Table("candidate_matches")]
public class CandidateMatch
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; }

    [Column("candidate_id")]
    public Guid CandidateId { get; set; }

    [Column("position_id")]
    public Guid PositionId { get; set; }

    [Column("overall_score")]
    public decimal OverallScore { get; set; }

    [Column("match_percentage")]
    public int MatchPercentage { get; set; }

    [Column("criteria_scores")]
    public string CriteriaScores { get; set; } = string.Empty;

    [Column("score_breakdown")]
    public string ScoreBreakdown { get; set; } = string.Empty;

    [Column("calculated_at")]
    public DateTime CalculatedAt { get; set; }

    [Column("methodology")]
    public string Methodology { get; set; } = "AHP";

    [Column("metadata")]
    public string? Metadata { get; set; }

    // Navigation properties (optional, based on your needs)
    [ForeignKey("CandidateId")]
    public virtual CandidateProfile? Candidate { get; set; }

    [ForeignKey("PositionId")]
    public virtual PositionProfile? Position { get; set; }
}

[Table("candidates")]
public class CandidateProfile
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; }

    [Column("first_name")]
    public string FirstName { get; set; } = string.Empty;

    [Column("last_name")]
    public string LastName { get; set; } = string.Empty;

    [Column("email")]
    public string Email { get; set; } = string.Empty;

    [Column("phone")]
    public string? Phone { get; set; }

    [Column("location")]
    public string? Location { get; set; }

    [Column("summary")]
    public string? Summary { get; set; }

    [Column("skills")]
    public string Skills { get; set; } = string.Empty;

    [Column("experience")]
    public string Experience { get; set; } = string.Empty;

    [Column("years_experience")]
    public int YearsExperience { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; }

    public virtual ICollection<CandidateMatch> Matches { get; set; } = new List<CandidateMatch>();
}

[Table("positions")]
public class PositionProfile
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; }

    [Column("title")]
    public string Title { get; set; } = string.Empty;

    [Column("company_name")]
    public string CompanyName { get; set; } = string.Empty;

    [Column("location")]
    public string? Location { get; set; }

    [Column("description")]
    public string? Description { get; set; }

    [Column("requirements")]
    public string Requirements { get; set; } = string.Empty;

    [Column("department")]
    public string? Department { get; set; }

    [Column("level")]
    public string? Level { get; set; }

    [Column("status")]
    public string Status { get; set; } = "Active";

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; }

    public virtual ICollection<CandidateMatch> Matches { get; set; } = new List<CandidateMatch>();
}

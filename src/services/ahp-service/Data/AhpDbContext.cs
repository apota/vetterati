using Microsoft.EntityFrameworkCore;
using Vetterati.Shared.Models;
using Vetterati.AhpService.Models;

namespace Vetterati.AhpService.Data;

public class AhpDbContext : DbContext
{
    public AhpDbContext(DbContextOptions<AhpDbContext> options) : base(options)
    {
    }

    public DbSet<JobProfile> JobProfiles { get; set; }
    public DbSet<Candidate> Candidates { get; set; }
    public DbSet<Vetterati.Shared.Models.CandidateProfile> CandidateProfiles { get; set; }
    public DbSet<AhpCriterion> AhpCriteria { get; set; }
    public DbSet<AhpComparison> AhpComparisons { get; set; }
    public DbSet<CandidateScore> CandidateScores { get; set; }
    
    // Sample data models
    public DbSet<CandidateMatch> CandidateMatches { get; set; }
    public DbSet<Vetterati.AhpService.Models.CandidateProfile> SampleCandidates { get; set; }
    public DbSet<PositionProfile> Positions { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // AHP Criterion configuration
        modelBuilder.Entity<AhpCriterion>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Weight).HasPrecision(10, 6);
            entity.HasIndex(e => new { e.JobProfileId, e.Name }).IsUnique();
        });

        // AHP Comparison configuration
        modelBuilder.Entity<AhpComparison>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Value).HasPrecision(10, 6);
            entity.Property(e => e.ComparisonValue).HasPrecision(10, 6);
            entity.HasIndex(e => new { e.JobProfileId, e.CriterionAId, e.CriterionBId }).IsUnique();
        });

        // Candidate Score configuration
        modelBuilder.Entity<CandidateScore>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.OverallScore).HasPrecision(10, 6);
            entity.Property(e => e.ScoreBreakdown).HasColumnType("jsonb");
            entity.HasIndex(e => new { e.JobProfileId, e.CandidateId }).IsUnique();
        });

        // Job Profile configuration
        modelBuilder.Entity<JobProfile>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Criteria).HasColumnType("jsonb");
            entity.Property(e => e.Weights).HasColumnType("jsonb");
            entity.Property(e => e.ComparisonMatrix).HasColumnType("jsonb");
        });

        // Candidate configuration
        modelBuilder.Entity<Candidate>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Location).HasColumnType("jsonb");
            entity.Property(e => e.Experience).HasColumnType("jsonb");
            entity.Property(e => e.Education).HasColumnType("jsonb");
            entity.Property(e => e.Skills).HasColumnType("jsonb");
            entity.Property(e => e.CareerMetrics).HasColumnType("jsonb");
            entity.Ignore(e => e.FullName); // Computed property
        });

        // Sample data model configurations
        modelBuilder.Entity<CandidateMatch>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.OverallScore).HasPrecision(5, 4);
            entity.Property(e => e.CriteriaScores).HasColumnType("jsonb");
            entity.Property(e => e.ScoreBreakdown).HasColumnType("jsonb");
            entity.Property(e => e.Metadata).HasColumnType("jsonb");
            entity.HasIndex(e => new { e.CandidateId, e.PositionId }).IsUnique();
        });

        modelBuilder.Entity<Vetterati.AhpService.Models.CandidateProfile>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Skills).HasColumnType("jsonb");
            entity.Property(e => e.Experience).HasColumnType("jsonb");
            entity.HasIndex(e => e.Email).IsUnique();
        });

        modelBuilder.Entity<PositionProfile>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Requirements).HasColumnType("jsonb");
        });
    }
}

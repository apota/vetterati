using Microsoft.EntityFrameworkCore;
using Vetterati.Shared.Models.Entities;

namespace Vetterati.AhpService.Data;

public class AhpDbContext : DbContext
{
    public AhpDbContext(DbContextOptions<AhpDbContext> options) : base(options)
    {
    }

    public DbSet<JobProfile> JobProfiles { get; set; }
    public DbSet<CandidateProfile> CandidateProfiles { get; set; }
    public DbSet<AhpCriterion> AhpCriteria { get; set; }
    public DbSet<AhpComparison> AhpComparisons { get; set; }
    public DbSet<CandidateScore> CandidateScores { get; set; }

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
            entity.Property(e => e.ComparisonValue).HasPrecision(10, 6);
            entity.HasIndex(e => new { e.JobProfileId, e.CriterionAId, e.CriterionBId }).IsUnique();
            
            entity.HasOne(e => e.CriterionA)
                .WithMany()
                .HasForeignKey(e => e.CriterionAId)
                .OnDelete(DeleteBehavior.Restrict);
                
            entity.HasOne(e => e.CriterionB)
                .WithMany()
                .HasForeignKey(e => e.CriterionBId)
                .OnDelete(DeleteBehavior.Restrict);
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
            entity.Property(e => e.Title).IsRequired().HasMaxLength(200);
            entity.Property(e => e.RequiredSkills).HasColumnType("jsonb");
            entity.Property(e => e.PreferredSkills).HasColumnType("jsonb");
            entity.Property(e => e.JobResponsibilities).HasColumnType("jsonb");
            entity.Property(e => e.AhpCriteria).HasColumnType("jsonb");
        });
    }
}

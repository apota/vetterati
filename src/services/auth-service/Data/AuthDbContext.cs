using Microsoft.EntityFrameworkCore;
using Vetterati.Shared.Models;
using System.Text.Json;

namespace AuthService.Data;

public class AuthDbContext : DbContext
{
    public AuthDbContext(DbContextOptions<AuthDbContext> options) : base(options) { }

    public DbSet<User> Users { get; set; }
    public DbSet<Organization> Organizations { get; set; }
    public DbSet<UserOrganization> UserOrganizations { get; set; }
    public DbSet<PasswordResetToken> PasswordResetTokens { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Configure schemas
        modelBuilder.Entity<User>().ToTable("users", "ats_core");
        modelBuilder.Entity<Organization>().ToTable("organizations", "ats_core");
        modelBuilder.Entity<UserOrganization>().ToTable("user_organizations", "ats_core");
        modelBuilder.Entity<PasswordResetToken>().ToTable("password_reset_tokens", "ats_core");

        // Configure User entity
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(255);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(255);
            entity.Property(e => e.SsoProvider).HasMaxLength(50);
            entity.Property(e => e.SsoId).HasMaxLength(255);
            entity.Property(e => e.IsActive).HasDefaultValue(true);
            
            // JSON column mappings
            entity.Property(e => e.Roles)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions?)null),
                    v => JsonSerializer.Deserialize<List<string>>(v, (JsonSerializerOptions?)null) ?? new List<string>()
                )
                .HasColumnType("jsonb");
                
            entity.Property(e => e.Preferences)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions?)null),
                    v => JsonSerializer.Deserialize<Dictionary<string, object>>(v, (JsonSerializerOptions?)null) ?? new Dictionary<string, object>()
                )
                .HasColumnType("jsonb");

            // Indexes
            entity.HasIndex(e => e.Email).IsUnique();
            entity.HasIndex(e => new { e.SsoProvider, e.SsoId });
        });

        // Configure Organization entity
        modelBuilder.Entity<Organization>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(255);
            entity.Property(e => e.Domain).HasMaxLength(255);
            
            entity.Property(e => e.Settings)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions?)null),
                    v => JsonSerializer.Deserialize<Dictionary<string, object>>(v, (JsonSerializerOptions?)null) ?? new Dictionary<string, object>()
                )
                .HasColumnType("jsonb");
        });

        // Configure UserOrganization entity
        modelBuilder.Entity<UserOrganization>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Role).IsRequired().HasMaxLength(100);
            entity.Property(e => e.IsActive).HasDefaultValue(true);
            
            // Explicit column mapping
            entity.Property(e => e.UserId).HasColumnName("user_id");
            entity.Property(e => e.OrganizationId).HasColumnName("organization_id");
            entity.Property(e => e.JoinedAt).HasColumnName("joined_at");
            
            entity.HasIndex(e => new { e.UserId, e.OrganizationId }).IsUnique();
            
            // Foreign key relationships
            entity.HasOne<User>()
                .WithMany()
                .HasForeignKey(e => e.UserId);
                
            entity.HasOne<Organization>()
                .WithMany()
                .HasForeignKey(e => e.OrganizationId);
        });

        // Configure PasswordResetToken entity
        modelBuilder.Entity<PasswordResetToken>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Token).IsRequired().HasMaxLength(255);
            entity.Property(e => e.ExpiresAt).IsRequired();
            entity.Property(e => e.IsUsed).HasDefaultValue(false);
            
            entity.HasIndex(e => e.Token).IsUnique();
            entity.HasIndex(e => e.UserId);
            entity.HasIndex(e => e.ExpiresAt);
            
            // Foreign key relationship
            entity.HasOne(e => e.User)
                .WithMany()
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        base.OnModelCreating(modelBuilder);
    }
}

public class UserOrganization : Vetterati.Shared.Models.BaseEntity
{
    public Guid UserId { get; set; }
    public User User { get; set; } = null!;
    public Guid OrganizationId { get; set; }
    public Organization Organization { get; set; } = null!;
    public string Role { get; set; } = string.Empty;
    public bool IsActive { get; set; } = true;
    public DateTime? JoinedAt { get; set; } = DateTime.UtcNow;
}

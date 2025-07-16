using Microsoft.EntityFrameworkCore;
using Vetterati.AhpService.Data;
using Vetterati.Shared.Models;

namespace Vetterati.AhpService.Extensions;

public static class DatabaseExtensions
{
    public static async Task<IServiceProvider> EnsureDatabaseCreatedAsync(this IServiceProvider serviceProvider)
    {
        using var scope = serviceProvider.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<AhpDbContext>();
        
        try
        {
            await context.Database.EnsureCreatedAsync();
            
            // Seed default AHP criteria if they don't exist
            if (!await context.AhpCriteria.AnyAsync())
            {
                var defaultJobProfile = await context.JobProfiles.FirstOrDefaultAsync();
                if (defaultJobProfile != null)
                {
                    var defaultCriteria = new[]
                    {
                        new AhpCriterion { JobProfileId = defaultJobProfile.Id, Name = "Experience", Weight = 0.35m, Description = "Years of relevant experience", Priority = 1 },
                        new AhpCriterion { JobProfileId = defaultJobProfile.Id, Name = "Skills", Weight = 0.30m, Description = "Technical skills matching", Priority = 2 },
                        new AhpCriterion { JobProfileId = defaultJobProfile.Id, Name = "Education", Weight = 0.20m, Description = "Educational background", Priority = 3 },
                        new AhpCriterion { JobProfileId = defaultJobProfile.Id, Name = "Culture Fit", Weight = 0.15m, Description = "Cultural fit assessment", Priority = 4 }
                    };
                    
                    await context.AhpCriteria.AddRangeAsync(defaultCriteria);
                    await context.SaveChangesAsync();
                }
            }
            
            // Create some sample candidate scores if none exist
            if (!await context.CandidateScores.AnyAsync())
            {
                var candidates = await context.Candidates.Take(10).ToListAsync();
                var jobs = await context.JobProfiles.Take(5).ToListAsync();
                
                if (candidates.Any() && jobs.Any())
                {
                    var sampleScores = new List<CandidateScore>();
                    var random = new Random();
                    
                    foreach (var candidate in candidates)
                    {
                        foreach (var job in jobs)
                        {
                            var score = new CandidateScore
                            {
                                Id = Guid.NewGuid(),
                                CandidateId = candidate.Id,
                                JobProfileId = job.Id,
                                OverallScore = (decimal)(random.NextDouble() * 0.4 + 0.6), // Score between 0.6 and 1.0
                                ScoreBreakdown = System.Text.Json.JsonSerializer.Serialize(new Dictionary<string, decimal>
                                {
                                    ["experience"] = (decimal)(random.NextDouble() * 0.3 + 0.7),
                                    ["skills"] = (decimal)(random.NextDouble() * 0.3 + 0.7),
                                    ["education"] = (decimal)(random.NextDouble() * 0.3 + 0.7),
                                    ["culture_fit"] = (decimal)(random.NextDouble() * 0.3 + 0.7)
                                }),
                                Methodology = "AHP",
                                CalculatedAt = DateTime.UtcNow,
                                ScoredAt = DateTime.UtcNow
                            };
                            
                            sampleScores.Add(score);
                        }
                    }
                    
                    await context.CandidateScores.AddRangeAsync(sampleScores);
                    await context.SaveChangesAsync();
                }
            }
        }
        catch (Exception ex)
        {
            // Log the error but don't fail the application startup
            Console.WriteLine($"Database initialization error: {ex.Message}");
        }
        
        return serviceProvider;
    }
}

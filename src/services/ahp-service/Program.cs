using Microsoft.EntityFrameworkCore;
using Serilog;
using StackExchange.Redis;
using Vetterati.AhpService.Data;
using Vetterati.AhpService.Services;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
builder.Host.UseSerilog((context, configuration) =>
    configuration.ReadFrom.Configuration(context.Configuration));

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { Title = "AHP Engine Service", Version = "v1" });
});

// Database
builder.Services.AddDbContext<AhpDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// Redis
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
});

// Register services
builder.Services.AddScoped<IAhpScoringService, AhpScoringService>();
builder.Services.AddScoped<ICandidateMatchingService, CandidateMatchingService>();
builder.Services.AddScoped<IJobProfileService, JobProfileService>();

// CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Health checks
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AhpDbContext>()
    .AddRedis(builder.Configuration.GetConnectionString("Redis") ?? "localhost");

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseSerilogRequestLogging();
app.UseRouting();
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.MapHealthChecks("/health");

// Ensure database is created
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<AhpDbContext>();
    await context.Database.EnsureCreatedAsync();
}

app.Run();

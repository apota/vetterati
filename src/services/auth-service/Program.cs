using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using System.Text.Json;
using AuthService.Data;
using AuthService.Services;
using Vetterati.Shared.Models;
using StackExchange.Redis;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .CreateLogger();

builder.Host.UseSerilog();

// Add services to the container
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
        options.JsonSerializerOptions.PropertyNameCaseInsensitive = true;
    });
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add Database
builder.Services.AddDbContext<AuthDbContext>(options =>
    options.UseInMemoryDatabase("VetteratiAuthTestDb"));

// Add Redis - Mock for testing
builder.Services.AddSingleton<IConnectionMultiplexer>(provider =>
{
    try
    {
        var configuration = new ConfigurationOptions
        {
            EndPoints = { "localhost:6379" },
            AbortOnConnectFail = false,
            ConnectTimeout = 500,
            ConnectRetry = 0
        };
        return ConnectionMultiplexer.Connect(configuration);
    }
    catch
    {
        Log.Warning("Redis not available, using mock connection for testing");
        return ConnectionMultiplexer.Connect("localhost:6379,abortConnect=false");
    }
});

// Add JWT Service
builder.Services.AddScoped<IJwtService, JwtService>();

// Add Email Service
builder.Services.AddScoped<IEmailService, EmailService>();

// Add Password Validation Service
builder.Services.AddScoped<IPasswordValidationService, PasswordValidationService>();

// Add User Management Service
builder.Services.AddScoped<IUserManagementService, UserManagementService>();

// Add Rate Limiting Service
builder.Services.AddScoped<IRateLimitingService, RateLimitingService>();

// Add JWT Authentication
var jwtSecretKey = builder.Configuration["Jwt:SecretKey"] ?? "your-super-secret-key-that-is-at-least-32-characters-long";
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"] ?? "vetterati-ats",
            ValidAudience = builder.Configuration["Jwt:Audience"] ?? "vetterati-ats",
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecretKey))
        };
    });

builder.Services.AddAuthorization();

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

var app = builder.Build();

// Ensure database is created and migrated
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<AuthDbContext>();
    try
    {
        context.Database.EnsureCreated();
        
        // Add test organization if not exists
        if (!context.Organizations.Any())
        {
            var testOrg = new Organization
            {
                Name = "Test Organization",
                Settings = new Dictionary<string, object>(),
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };
            context.Organizations.Add(testOrg);
            await context.SaveChangesAsync();
            Log.Information("Test organization created");
        }
        
        Log.Information("Database schema created successfully");
    }
    catch (Exception ex)
    {
        Log.Error(ex, "Failed to create database schema");
    }
}

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("AllowAll");

// Add rate limiting middleware
app.UseMiddleware<RateLimitMiddleware>();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

// Health check
app.MapGet("/health", () => new { status = "healthy", service = "auth-service", timestamp = DateTime.UtcNow });

app.Run();

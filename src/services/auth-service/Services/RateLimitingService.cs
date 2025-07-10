using StackExchange.Redis;
using System.Text.Json;

namespace AuthService.Services;

public interface IRateLimitingService
{
    Task<bool> IsRateLimitExceededAsync(string key, int maxRequests, TimeSpan window);
    Task<RateLimitInfo> GetRateLimitInfoAsync(string key, int maxRequests, TimeSpan window);
    Task ResetRateLimitAsync(string key);
}

public class RateLimitingService : IRateLimitingService
{
    private readonly IDatabase _redis;
    private readonly ILogger<RateLimitingService> _logger;

    public RateLimitingService(IConnectionMultiplexer redis, ILogger<RateLimitingService> logger)
    {
        _redis = redis.GetDatabase();
        _logger = logger;
    }

    public async Task<bool> IsRateLimitExceededAsync(string key, int maxRequests, TimeSpan window)
    {
        try
        {
            var rateLimitKey = $"rate_limit:{key}";
            var currentCount = await _redis.StringGetAsync(rateLimitKey);

            if (!currentCount.HasValue)
            {
                // First request - set counter with expiration
                await _redis.StringSetAsync(rateLimitKey, 1, window);
                return false;
            }

            var count = (int)currentCount;
            if (count >= maxRequests)
            {
                _logger.LogWarning("Rate limit exceeded for key: {Key}, Count: {Count}, Max: {Max}", 
                    key, count, maxRequests);
                return true;
            }

            // Increment counter
            await _redis.StringIncrementAsync(rateLimitKey);
            return false;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking rate limit for key: {Key}", key);
            // In case of Redis failure, allow the request (fail open)
            return false;
        }
    }

    public async Task<RateLimitInfo> GetRateLimitInfoAsync(string key, int maxRequests, TimeSpan window)
    {
        try
        {
            var rateLimitKey = $"rate_limit:{key}";
            var currentCount = await _redis.StringGetAsync(rateLimitKey);
            var ttl = await _redis.KeyTimeToLiveAsync(rateLimitKey);

            var count = currentCount.HasValue ? (int)currentCount : 0;
            var remaining = Math.Max(0, maxRequests - count);
            var resetTime = DateTime.UtcNow.Add(ttl ?? TimeSpan.Zero);

            return new RateLimitInfo
            {
                Limit = maxRequests,
                Remaining = remaining,
                ResetTime = resetTime,
                WindowSeconds = (int)window.TotalSeconds
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting rate limit info for key: {Key}", key);
            return new RateLimitInfo
            {
                Limit = maxRequests,
                Remaining = maxRequests,
                ResetTime = DateTime.UtcNow.Add(window),
                WindowSeconds = (int)window.TotalSeconds
            };
        }
    }

    public async Task ResetRateLimitAsync(string key)
    {
        try
        {
            var rateLimitKey = $"rate_limit:{key}";
            await _redis.KeyDeleteAsync(rateLimitKey);
            _logger.LogInformation("Rate limit reset for key: {Key}", key);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error resetting rate limit for key: {Key}", key);
        }
    }
}

public class RateLimitInfo
{
    public int Limit { get; set; }
    public int Remaining { get; set; }
    public DateTime ResetTime { get; set; }
    public int WindowSeconds { get; set; }
}

public class RateLimitMiddleware
{
    private readonly RequestDelegate _next;
    private readonly IRateLimitingService _rateLimiting;
    private readonly ILogger<RateLimitMiddleware> _logger;
    private readonly RateLimitOptions _options;

    public RateLimitMiddleware(
        RequestDelegate next,
        IRateLimitingService rateLimiting,
        ILogger<RateLimitMiddleware> logger,
        IConfiguration configuration)
    {
        _next = next;
        _rateLimiting = rateLimiting;
        _logger = logger;
        _options = configuration.GetSection("RateLimit").Get<RateLimitOptions>() ?? new RateLimitOptions();
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Skip rate limiting for health checks and internal endpoints
        var path = context.Request.Path.Value?.ToLower();
        if (path?.Contains("/health") == true || path?.Contains("/swagger") == true)
        {
            await _next(context);
            return;
        }

        // Get rate limit key (IP address for anonymous, user ID for authenticated)
        var rateLimitKey = GetRateLimitKey(context);
        var isAuthenticated = context.User.Identity?.IsAuthenticated == true;
        
        var maxRequests = isAuthenticated ? _options.AuthenticatedUserLimit : _options.AnonymousUserLimit;
        var window = TimeSpan.FromHours(1); // 1 hour window

        // Check rate limit
        var rateLimitInfo = await _rateLimiting.GetRateLimitInfoAsync(rateLimitKey, maxRequests, window);
        var isExceeded = await _rateLimiting.IsRateLimitExceededAsync(rateLimitKey, maxRequests, window);

        // Add rate limit headers
        context.Response.Headers["X-RateLimit-Limit"] = maxRequests.ToString();
        context.Response.Headers["X-RateLimit-Remaining"] = rateLimitInfo.Remaining.ToString();
        context.Response.Headers["X-RateLimit-Reset"] = ((DateTimeOffset)rateLimitInfo.ResetTime).ToUnixTimeSeconds().ToString();

        if (isExceeded)
        {
            context.Response.StatusCode = 429; // Too Many Requests
            context.Response.Headers["Retry-After"] = rateLimitInfo.WindowSeconds.ToString();
            
            var errorResponse = new
            {
                error = "Rate limit exceeded",
                message = $"Too many requests. Limit: {maxRequests} per hour. Try again later.",
                retryAfter = rateLimitInfo.WindowSeconds
            };

            await context.Response.WriteAsync(JsonSerializer.Serialize(errorResponse));
            return;
        }

        await _next(context);
    }

    private string GetRateLimitKey(HttpContext context)
    {
        // Use user ID for authenticated users, IP for anonymous
        if (context.User.Identity?.IsAuthenticated == true)
        {
            var userId = context.User.FindFirst("sub")?.Value;
            return $"user:{userId}";
        }

        // Use IP address for anonymous users
        var ipAddress = context.Connection.RemoteIpAddress?.ToString() ?? "unknown";
        return $"ip:{ipAddress}";
    }
}

public class RateLimitOptions
{
    public int AnonymousUserLimit { get; set; } = 100; // per hour
    public int AuthenticatedUserLimit { get; set; } = 1000; // per hour
    public int AdminUserLimit { get; set; } = 5000; // per hour
}

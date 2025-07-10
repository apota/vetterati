using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using System.Security.Claims;

namespace AuthService.Middleware;

public class JwtAuthenticationMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<JwtAuthenticationMiddleware> _logger;

    public JwtAuthenticationMiddleware(RequestDelegate next, ILogger<JwtAuthenticationMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Skip authentication for certain paths
        var path = context.Request.Path.Value?.ToLower();
        var skipAuth = path?.Contains("/health") == true ||
                      path?.Contains("/swagger") == true ||
                      path?.Contains("/api/v1/auth/login") == true ||
                      path?.Contains("/api/v1/auth/register") == true ||
                      path?.Contains("/api/v1/auth/forgot-password") == true ||
                      path?.Contains("/api/v1/auth/reset-password") == true ||
                      path?.Contains("/api/v1/auth/verify-reset-token") == true;

        if (skipAuth)
        {
            await _next(context);
            return;
        }

        // Check if endpoint requires authorization
        var endpoint = context.GetEndpoint();
        var hasAuthorizeAttribute = endpoint?.Metadata?.GetMetadata<AuthorizeAttribute>() != null;
        var hasAllowAnonymousAttribute = endpoint?.Metadata?.GetMetadata<AllowAnonymousAttribute>() != null;

        if (!hasAuthorizeAttribute || hasAllowAnonymousAttribute)
        {
            await _next(context);
            return;
        }

        // Validate JWT token
        var token = ExtractTokenFromHeader(context.Request);
        if (string.IsNullOrEmpty(token))
        {
            _logger.LogWarning("Missing JWT token for protected endpoint: {Path}", path);
            context.Response.StatusCode = 401;
            await context.Response.WriteAsync("Unauthorized: Missing token");
            return;
        }

        try
        {
            // Token validation is handled by the JWT middleware in Program.cs
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in JWT authentication middleware");
            context.Response.StatusCode = 500;
            await context.Response.WriteAsync("Internal server error");
        }
    }

    private static string? ExtractTokenFromHeader(HttpRequest request)
    {
        var authHeader = request.Headers["Authorization"].FirstOrDefault();
        if (authHeader != null && authHeader.StartsWith("Bearer "))
        {
            return authHeader.Substring("Bearer ".Length);
        }
        return null;
    }
}

[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class RequireRoleAttribute : Attribute, IAuthorizationFilter
{
    private readonly string[] _roles;

    public RequireRoleAttribute(params string[] roles)
    {
        _roles = roles;
    }

    public void OnAuthorization(AuthorizationFilterContext context)
    {
        var user = context.HttpContext.User;
        
        if (!user.Identity?.IsAuthenticated == true)
        {
            context.Result = new UnauthorizedResult();
            return;
        }

        var userRoles = user.FindAll(ClaimTypes.Role).Select(c => c.Value);
        var hasRequiredRole = _roles.Any(role => userRoles.Contains(role));

        if (!hasRequiredRole)
        {
            context.Result = new ForbidResult();
        }
    }
}

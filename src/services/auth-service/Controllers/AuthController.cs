using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using AuthService.Data;
using AuthService.Services;
using Vetterati.Shared.Models;
using StackExchange.Redis;
using System.Text.Json;
using BCrypt.Net;
using System.Security.Cryptography;

namespace AuthService.Controllers;

[ApiController]
[Route("api/v1/auth")]
public class AuthController : ControllerBase
{
    private readonly AuthDbContext _context;
    private readonly IJwtService _jwtService;
    private readonly IDatabase _redis;
    private readonly ILogger<AuthController> _logger;
    private readonly IEmailService _emailService;
    private readonly IPasswordValidationService _passwordValidation;
    private readonly IUserManagementService _userManagement;

    public AuthController(
        AuthDbContext context, 
        IJwtService jwtService, 
        IConnectionMultiplexer redis,
        ILogger<AuthController> logger,
        IEmailService emailService,
        IPasswordValidationService passwordValidation,
        IUserManagementService userManagement)
    {
        _context = context;
        _jwtService = jwtService;
        _redis = redis.GetDatabase();
        _logger = logger;
        _emailService = emailService;
        _passwordValidation = passwordValidation;
        _userManagement = userManagement;
    }

    [HttpPost("login")]
    public async Task<ActionResult<ApiResponse<LoginResponse>>> Login([FromBody] LoginRequest request)
    {
        try
        {
            // For demo purposes, we'll use email-based login
            // In production, this would integrate with actual SSO providers
            var user = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == request.Code && u.IsActive);

            if (user == null)
            {
                // Create a demo user if not exists
                user = new User
                {
                    Email = request.Code,
                    Name = request.Code.Split('@')[0],
                    SsoProvider = request.Provider,
                    SsoId = request.Code,
                    Roles = new List<string> { "recruiter" },
                    IsActive = true
                };

                _context.Users.Add(user);
                await _context.SaveChangesAsync();

                // Add to default organization
                var defaultOrg = await _context.Organizations.FirstAsync();
                var userOrg = new AuthService.Data.UserOrganization
                {
                    UserId = user.Id,
                    OrganizationId = defaultOrg.Id,
                    Role = "recruiter"
                };
                _context.UserOrganizations.Add(userOrg);
                await _context.SaveChangesAsync();
            }

            // Update last login
            user.LastLoginAt = DateTime.UtcNow;
            await _context.SaveChangesAsync();

            // Generate tokens
            var accessToken = _jwtService.GenerateAccessToken(user);
            var refreshToken = _jwtService.GenerateRefreshToken();

            // Store refresh token in Redis
            await _redis.StringSetAsync($"refresh_token:{user.Id}", refreshToken, TimeSpan.FromDays(30));

            var response = new ApiResponse<LoginResponse>
            {
                Data = new LoginResponse
                {
                    AccessToken = accessToken,
                    RefreshToken = refreshToken,
                    ExpiresIn = 3600,
                    User = user
                }
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during login");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred during login" 
            });
        }
    }

    [HttpPost("refresh")]
    public async Task<ActionResult<ApiResponse<LoginResponse>>> RefreshToken([FromBody] RefreshTokenRequest request)
    {
        try
        {
            // Find user by refresh token in Redis
            var keys = _redis.Multiplexer.GetServer(_redis.Multiplexer.GetEndPoints().First())
                .Keys(pattern: "refresh_token:*");

            string? userId = null;
            foreach (var key in keys)
            {
                var storedToken = await _redis.StringGetAsync(key);
                if (storedToken == request.RefreshToken)
                {
                    userId = key.ToString().Split(':')[1];
                    break;
                }
            }

            if (userId == null)
            {
                return Unauthorized(new ApiError 
                { 
                    Code = "INVALID_REFRESH_TOKEN", 
                    Message = "Invalid refresh token" 
                });
            }

            var user = await _context.Users.FindAsync(Guid.Parse(userId));
            if (user == null || !user.IsActive)
            {
                return Unauthorized(new ApiError 
                { 
                    Code = "USER_NOT_FOUND", 
                    Message = "User not found or inactive" 
                });
            }

            // Generate new tokens
            var accessToken = _jwtService.GenerateAccessToken(user);
            var newRefreshToken = _jwtService.GenerateRefreshToken();

            // Update refresh token in Redis
            await _redis.KeyDeleteAsync($"refresh_token:{userId}");
            await _redis.StringSetAsync($"refresh_token:{userId}", newRefreshToken, TimeSpan.FromDays(30));

            var response = new ApiResponse<LoginResponse>
            {
                Data = new LoginResponse
                {
                    AccessToken = accessToken,
                    RefreshToken = newRefreshToken,
                    ExpiresIn = 3600,
                    User = user
                }
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during token refresh");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred during token refresh" 
            });
        }
    }

    [HttpPost("logout")]
    public async Task<ActionResult<ApiResponse<object>>> Logout()
    {
        try
        {
            var userIdClaim = User.FindFirst("sub")?.Value;
            if (userIdClaim != null)
            {
                // Remove refresh token from Redis
                await _redis.KeyDeleteAsync($"refresh_token:{userIdClaim}");
            }

            return Ok(new ApiResponse<object> 
            { 
                Data = new { message = "Logged out successfully" } 
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during logout");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred during logout" 
            });
        }
    }

    [HttpGet("me")]
    public async Task<ActionResult<ApiResponse<User>>> GetCurrentUser()
    {
        try
        {
            var userIdClaim = User.FindFirst("sub")?.Value;
            if (userIdClaim == null)
            {
                return Unauthorized(new ApiError 
                { 
                    Code = "UNAUTHORIZED", 
                    Message = "User not authenticated" 
                });
            }

            var user = await _context.Users.FindAsync(Guid.Parse(userIdClaim));
            if (user == null)
            {
                return NotFound(new ApiError 
                { 
                    Code = "USER_NOT_FOUND", 
                    Message = "User not found" 
                });
            }

            return Ok(new ApiResponse<User> { Data = user });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting current user");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred while fetching user" 
            });
        }
    }

    [HttpPost("register")]
    public async Task<ActionResult<ApiResponse<LoginResponse>>> Register([FromBody] RegisterRequest request)
    {
        try
        {
            // Validate email doesn't already exist
            var existingUser = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == request.Email);
            
            if (existingUser != null)
            {
                return BadRequest(new ApiError 
                { 
                    Code = "EMAIL_EXISTS", 
                    Message = "A user with this email already exists" 
                });
            }

            // Create new user
            var user = new User
            {
                Email = request.Email,
                FirstName = request.FirstName,
                LastName = request.LastName,
                Name = $"{request.FirstName} {request.LastName}",
                Company = request.Company,
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.Password),
                Roles = new List<string> { request.Role },
                IsActive = true
            };

            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            // Create or find organization
            var organization = await _context.Organizations
                .FirstOrDefaultAsync(o => o.Name == request.Company);
            
            if (organization == null)
            {
                organization = new Organization
                {
                    Name = request.Company,
                    Settings = new Dictionary<string, object>()
                };
                _context.Organizations.Add(organization);
                await _context.SaveChangesAsync();
            }

            // Add user to organization
            var userOrg = new AuthService.Data.UserOrganization
            {
                UserId = user.Id,
                OrganizationId = organization.Id,
                Role = request.Role
            };
            _context.UserOrganizations.Add(userOrg);
            await _context.SaveChangesAsync();

            // Generate tokens
            var accessToken = _jwtService.GenerateAccessToken(user);
            var refreshToken = _jwtService.GenerateRefreshToken();

            // Store refresh token in Redis
            await _redis.StringSetAsync($"refresh_token:{user.Id}", refreshToken, TimeSpan.FromDays(30));

            var response = new ApiResponse<LoginResponse>
            {
                Data = new LoginResponse
                {
                    AccessToken = accessToken,
                    RefreshToken = refreshToken,
                    ExpiresIn = 3600,
                    User = user
                }
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during registration");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred during registration" 
            });
        }
    }

    [HttpPost("email-login")]
    public async Task<ActionResult<ApiResponse<LoginResponse>>> EmailLogin([FromBody] EmailLoginRequest request)
    {
        try
        {
            // Find user by email
            var user = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == request.Email && u.IsActive);

            if (user == null || user.PasswordHash == null)
            {
                return Unauthorized(new ApiError 
                { 
                    Code = "INVALID_CREDENTIALS", 
                    Message = "Invalid email or password" 
                });
            }

            // Verify password
            if (!BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash))
            {
                return Unauthorized(new ApiError 
                { 
                    Code = "INVALID_CREDENTIALS", 
                    Message = "Invalid email or password" 
                });
            }

            // Update last login
            user.LastLoginAt = DateTime.UtcNow;
            await _context.SaveChangesAsync();

            // Generate tokens
            var accessToken = _jwtService.GenerateAccessToken(user);
            var refreshToken = _jwtService.GenerateRefreshToken();

            // Store refresh token in Redis
            await _redis.StringSetAsync($"refresh_token:{user.Id}", refreshToken, TimeSpan.FromDays(30));

            var response = new ApiResponse<LoginResponse>
            {
                Data = new LoginResponse
                {
                    AccessToken = accessToken,
                    RefreshToken = refreshToken,
                    ExpiresIn = 3600,
                    User = user
                }
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during email login");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred during login" 
            });
        }
    }

    [HttpPost("forgot-password")]
    public async Task<ActionResult<ApiResponse<object>>> ForgotPassword([FromBody] ForgotPasswordRequest request)
    {
        try
        {
            // Find user by email
            var user = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == request.Email && u.IsActive);

            // Always return success to prevent email enumeration attacks
            // but only send email if user exists
            if (user != null)
            {
                // Generate secure reset token
                var resetToken = GenerateSecureToken();
                
                // Store reset token in database
                var passwordResetToken = new PasswordResetToken
                {
                    UserId = user.Id,
                    Token = resetToken,
                    ExpiresAt = DateTime.UtcNow.AddHours(1), // 1 hour expiry
                    IsUsed = false
                };

                _context.PasswordResetTokens.Add(passwordResetToken);
                await _context.SaveChangesAsync();

                // Send reset email
                await _emailService.SendPasswordResetEmailAsync(user.Email, resetToken, user.Name);
            }

            return Ok(new ApiResponse<object> 
            { 
                Data = new { message = "If an account with that email exists, we've sent a password reset link." } 
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during forgot password request");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred while processing your request" 
            });
        }
    }

    [HttpPost("verify-reset-token")]
    public async Task<ActionResult<ApiResponse<object>>> VerifyResetToken([FromBody] VerifyResetTokenRequest request)
    {
        try
        {
            var resetToken = await _context.PasswordResetTokens
                .Include(rt => rt.User)
                .FirstOrDefaultAsync(rt => rt.Token == request.Token && 
                                          !rt.IsUsed && 
                                          rt.ExpiresAt > DateTime.UtcNow);

            if (resetToken == null)
            {
                return BadRequest(new ApiError 
                { 
                    Code = "INVALID_TOKEN", 
                    Message = "Invalid or expired reset token" 
                });
            }

            return Ok(new ApiResponse<object> 
            { 
                Data = new { message = "Token is valid" } 
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during token verification");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred while verifying the token" 
            });
        }
    }

    [HttpPost("reset-password")]
    public async Task<ActionResult<ApiResponse<object>>> ResetPassword([FromBody] ResetPasswordRequest request)
    {
        try
        {
            // Validate passwords match
            if (request.NewPassword != request.ConfirmPassword)
            {
                return BadRequest(new ApiError 
                { 
                    Code = "PASSWORD_MISMATCH", 
                    Message = "Passwords do not match" 
                });
            }

            // Validate password strength
            if (request.NewPassword.Length < 8)
            {
                return BadRequest(new ApiError 
                { 
                    Code = "WEAK_PASSWORD", 
                    Message = "Password must be at least 8 characters long" 
                });
            }

            // Find and validate reset token
            var resetToken = await _context.PasswordResetTokens
                .Include(rt => rt.User)
                .FirstOrDefaultAsync(rt => rt.Token == request.Token && 
                                          !rt.IsUsed && 
                                          rt.ExpiresAt > DateTime.UtcNow);

            if (resetToken == null)
            {
                return BadRequest(new ApiError 
                { 
                    Code = "INVALID_TOKEN", 
                    Message = "Invalid or expired reset token" 
                });
            }

            // Update user's password
            var user = resetToken.User;
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.NewPassword);
            user.UpdatedAt = DateTime.UtcNow;

            // Mark token as used
            resetToken.IsUsed = true;
            resetToken.UsedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            // Invalidate all existing refresh tokens for security
            var keys = _redis.Multiplexer.GetServer(_redis.Multiplexer.GetEndPoints().First())
                .Keys(pattern: $"refresh_token:{user.Id}");
            
            foreach (var key in keys)
            {
                await _redis.KeyDeleteAsync(key);
            }

            return Ok(new ApiResponse<object> 
            { 
                Data = new { message = "Password has been reset successfully" } 
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during password reset");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred while resetting your password" 
            });
        }
    }

    private string GenerateSecureToken()
    {
        using var rng = RandomNumberGenerator.Create();
        var bytes = new byte[32];
        rng.GetBytes(bytes);
        return Convert.ToBase64String(bytes).Replace("+", "-").Replace("/", "_").Replace("=", "");
    }
}

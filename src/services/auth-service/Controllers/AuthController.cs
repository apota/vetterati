using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using AuthService.Data;
using AuthService.Services;
using Vetterati.Shared.Models;
using StackExchange.Redis;
using System.Text.Json;
using BCrypt.Net;
using System.Security.Cryptography;
using Microsoft.AspNetCore.Authorization;
using System.Security.Claims;

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
    private readonly IConfiguration _configuration;

    public AuthController(
        AuthDbContext context, 
        IJwtService jwtService, 
        IConnectionMultiplexer redis,
        ILogger<AuthController> logger,
        IEmailService emailService,
        IPasswordValidationService passwordValidation,
        IUserManagementService userManagement,
        IConfiguration configuration)
    {
        _context = context;
        _jwtService = jwtService;
        _redis = redis.GetDatabase();
        _logger = logger;
        _emailService = emailService;
        _passwordValidation = passwordValidation;
        _userManagement = userManagement;
        _configuration = configuration;
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
    public ActionResult<ApiResponse<User>> GetCurrentUser()
    {
        try
        {
            // Extract JWT token from Authorization header
            var authHeader = Request.Headers["Authorization"].FirstOrDefault();
            if (authHeader != null && authHeader.StartsWith("Bearer "))
            {
                var token = authHeader.Substring("Bearer ".Length).Trim();
                
                try
                {
                    // Validate and decode JWT token
                    var principal = _jwtService.GetPrincipalFromExpiredToken(token);
                    
                    if (principal != null)
                    {
                        // Get user ID from token claims
                        var userIdClaim = principal.FindFirst("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier");
                        if (userIdClaim != null && Guid.TryParse(userIdClaim.Value, out var userId))
                        {
                            // Get user from database
                            var user = _context.Users.FirstOrDefault(u => u.Id == userId);
                            if (user != null)
                            {
                                return Ok(new ApiResponse<User> { Data = user });
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Invalid JWT token provided");
                }
            }
            
            // If no valid token, return unauthorized
            return Unauthorized(new ApiError 
            { 
                Code = "UNAUTHORIZED", 
                Message = "Authentication required" 
            });
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

    [HttpPut("me")]
    // [Authorize] // Temporarily removed for debugging
    public async Task<ActionResult<ApiResponse<User>>> UpdateProfile([FromBody] UpdateProfileRequest request)
    {
        try
        {
            Console.WriteLine("=== PROFILE UPDATE STARTED ===");
            _logger.LogInformation("=== PROFILE UPDATE STARTED ===");
            _logger.LogInformation("UpdateProfile called with request: {Request}", JsonSerializer.Serialize(request));

            // Get the current user ID from JWT token
            var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            _logger.LogInformation("User ID from JWT: {UserId}", userIdClaim);

            if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
            {
                _logger.LogWarning("Invalid or missing user token. UserIdClaim: {UserIdClaim}", userIdClaim);
                return Unauthorized(new ApiError 
                { 
                    Code = "UNAUTHORIZED", 
                    Message = "Invalid or missing user token" 
                });
            }

            // Find the user in the database
            var user = await _context.Users.FindAsync(userId);
            if (user == null)
            {
                _logger.LogWarning("User not found in database with ID: {UserId}", userId);
                return NotFound(new ApiError 
                { 
                    Code = "USER_NOT_FOUND", 
                    Message = "User not found" 
                });
            }

            _logger.LogInformation("Found user: {UserId}, Current: {FirstName} {LastName} - {Company}", 
                userId, user.FirstName, user.LastName, user.Company);

            // Update user properties
            if (!string.IsNullOrEmpty(request.FirstName))
            {
                _logger.LogInformation("Updating FirstName from {Old} to {New}", user.FirstName, request.FirstName);
                user.FirstName = request.FirstName;
            }
            
            if (!string.IsNullOrEmpty(request.LastName))
            {
                _logger.LogInformation("Updating LastName from {Old} to {New}", user.LastName, request.LastName);
                user.LastName = request.LastName;
            }
            
            if (!string.IsNullOrEmpty(request.Company))
            {
                _logger.LogInformation("Updating Company from {Old} to {New}", user.Company, request.Company);
                user.Company = request.Company;
            }
            
            if (request.Preferences != null)
            {
                _logger.LogInformation("Updating Preferences");
                user.Preferences = request.Preferences;
            }

            // Update the Name field based on FirstName and LastName
            if (!string.IsNullOrEmpty(request.FirstName) || !string.IsNullOrEmpty(request.LastName))
            {
                var newName = $"{user.FirstName} {user.LastName}".Trim();
                _logger.LogInformation("Updating Name from {Old} to {New}", user.Name, newName);
                user.Name = newName;
            }

            // Update the UpdatedAt timestamp
            user.UpdatedAt = DateTime.UtcNow;

            // Save changes to database
            _logger.LogInformation("Saving changes to database...");
            var changeCount = await _context.SaveChangesAsync();
            _logger.LogInformation("Database changes saved. Changes made: {ChangeCount}", changeCount);

            _logger.LogInformation("User profile updated successfully for user {UserId}", userId);

            return Ok(new ApiResponse<User> { Data = user });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating user profile");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred while updating profile" 
            });
        }
    }

    private List<User> GetDemoUserProfiles()
    {
        return new List<User>
        {
            new User
            {
                Id = Guid.Parse("8dfeb904-6902-4097-948a-1c1d4d058013"),
                Email = "recruiter@company.com",
                Name = "Jane Recruiter",
                FirstName = "Jane",
                LastName = "Recruiter",
                Company = "TechCorp",
                Roles = new List<string> { "recruiter" },
                IsActive = true,
                CreatedAt = DateTime.UtcNow.AddDays(-30),
                UpdatedAt = DateTime.UtcNow,
                Preferences = new Dictionary<string, object>
                {
                    { "timezone", "UTC" },
                    { "emailNotifications", true },
                    { "pushNotifications", true },
                    { "marketingEmails", false }
                }
            },
            new User
            {
                Id = Guid.Parse("a1b2c3d4-5678-9012-3456-789012345678"),
                Email = "admin@vetterati.com",
                Name = "Admin User",
                FirstName = "Admin",
                LastName = "User",
                Company = "Vetterati",
                Roles = new List<string> { "admin", "recruiter" },
                IsActive = true,
                CreatedAt = DateTime.UtcNow.AddDays(-60),
                UpdatedAt = DateTime.UtcNow,
                Preferences = new Dictionary<string, object>
                {
                    { "timezone", "UTC" },
                    { "emailNotifications", true },
                    { "pushNotifications", true },
                    { "marketingEmails", true }
                }
            },
            new User
            {
                Id = Guid.Parse("b2c3d4e5-6789-0123-4567-890123456789"),
                Email = "manager@company.com",
                Name = "John Manager",
                FirstName = "John",
                LastName = "Manager",
                Company = "TechCorp",
                Roles = new List<string> { "hiring_manager" },
                IsActive = true,
                CreatedAt = DateTime.UtcNow.AddDays(-45),
                UpdatedAt = DateTime.UtcNow,
                Preferences = new Dictionary<string, object>
                {
                    { "timezone", "America/New_York" },
                    { "emailNotifications", true },
                    { "pushNotifications", false },
                    { "marketingEmails", false }
                }
            }
        };
    }

    [HttpPost("register")]
    public async Task<ActionResult<ApiResponse<LoginResponse>>> Register([FromBody] RegisterRequest? request)
    {
        try
        {
            _logger.LogInformation("Register endpoint called");
            
            // Check if request is null
            if (request == null)
            {
                _logger.LogWarning("Register request is null");
                return BadRequest(new ApiError 
                { 
                    Code = "INVALID_REQUEST", 
                    Message = "Request body is required" 
                });
            }

            // Validate required fields
            if (string.IsNullOrWhiteSpace(request.Email))
            {
                return BadRequest(new ApiError 
                { 
                    Code = "VALIDATION_ERROR", 
                    Message = "Email is required" 
                });
            }

            if (string.IsNullOrWhiteSpace(request.Password))
            {
                return BadRequest(new ApiError 
                { 
                    Code = "VALIDATION_ERROR", 
                    Message = "Password is required" 
                });
            }

            if (string.IsNullOrWhiteSpace(request.FirstName))
            {
                return BadRequest(new ApiError 
                { 
                    Code = "VALIDATION_ERROR", 
                    Message = "First name is required" 
                });
            }

            if (string.IsNullOrWhiteSpace(request.LastName))
            {
                return BadRequest(new ApiError 
                { 
                    Code = "VALIDATION_ERROR", 
                    Message = "Last name is required" 
                });
            }

            if (string.IsNullOrWhiteSpace(request.Role))
            {
                return BadRequest(new ApiError 
                { 
                    Code = "VALIDATION_ERROR", 
                    Message = "Role is required" 
                });
            }

            _logger.LogInformation("Registration attempt for email: {Email}, name: {FirstName} {LastName}, role: {Role}", 
                request.Email, request.FirstName, request.LastName, request.Role);

            // Validate password
            var passwordValidation = _passwordValidation?.ValidatePassword(request.Password);
            if (passwordValidation != null && !passwordValidation.IsValid)
            {
                return BadRequest(new ApiError 
                { 
                    Code = "INVALID_PASSWORD", 
                    Message = string.Join("; ", passwordValidation.Errors)
                });
            }

            // Basic password validation if service is not available
            if (passwordValidation == null && request.Password.Length < 6)
            {
                return BadRequest(new ApiError 
                { 
                    Code = "INVALID_PASSWORD", 
                    Message = "Password must be at least 6 characters long" 
                });
            }

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
                Company = request.Company ?? "Default Company",
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.Password),
                Roles = new List<string> { request.Role },
                IsActive = true,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            _logger.LogInformation("User created successfully with ID: {UserId}", user.Id);

            // Create or find organization
            var organizationName = !string.IsNullOrWhiteSpace(request.Company) ? request.Company : "Default Company";
            var organization = await _context.Organizations
                .FirstOrDefaultAsync(o => o.Name == organizationName);
            
            if (organization == null)
            {
                organization = new Organization
                {
                    Name = organizationName,
                    Settings = new Dictionary<string, object>(),
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow
                };
                _context.Organizations.Add(organization);
                await _context.SaveChangesAsync();
                
                _logger.LogInformation("Organization created: {OrganizationName} with ID: {OrganizationId}", 
                    organizationName, organization.Id);
            }

            // Add user to organization
            var userOrg = new AuthService.Data.UserOrganization
            {
                UserId = user.Id,
                OrganizationId = organization.Id,
                Role = request.Role,
                IsActive = true,
                JoinedAt = DateTime.UtcNow,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };
            _context.UserOrganizations.Add(userOrg);
            await _context.SaveChangesAsync();

            _logger.LogInformation("User added to organization successfully");

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

            _logger.LogInformation("Registration completed successfully for user: {Email}", request.Email);
            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during registration for email: {Email}. Error: {ErrorMessage}. StackTrace: {StackTrace}", 
                request?.Email ?? "unknown", ex.Message, ex.StackTrace);
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred during registration. Please try again." 
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
            _logger.LogInformation("Forgot password request for email: {Email}", request.Email);
            
            // Find user by email
            var user = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == request.Email && u.IsActive);

            _logger.LogInformation("User found: {Found}, User ID: {UserId}", user != null, user?.Id);

            string? resetUrl = null;
            
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
                
                // For demo purposes, also return the reset URL
                var frontendUrl = _configuration["Frontend:BaseUrl"] ?? "DEFAULT-FALLBACK-URL";
                _logger.LogInformation("Frontend URL from config: {FrontendUrl}", frontendUrl);
                resetUrl = $"{frontendUrl}/reset-password?token={resetToken}";
                
                // Log the reset URL for demo purposes
                _logger.LogInformation("DEMO: Reset URL for {Email}: {ResetUrl}", user.Email, resetUrl);
            }

            // For demo purposes, include the reset URL in response
            object responseData;
            if (resetUrl != null)
            {
                responseData = new { 
                    message = "If an account with that email exists, we've sent a password reset link.",
                    resetUrl = resetUrl // Demo: actual reset URL
                };
            }
            else
            {
                responseData = new { 
                    message = "If an account with that email exists, we've sent a password reset link." 
                };
            }

            return Ok(new ApiResponse<object> 
            { 
                Data = responseData 
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

    /// <summary>
    /// <summary>
    /// Demo login endpoint for quick access with predefined users.
    /// Available roles: admin, recruiter, hiring-manager, candidate, interviewer, hr
    /// POST /api/v1/auth/demo-login with { "role": "admin" }
    /// </summary>
    [HttpPost("demo-login")]
    public async Task<ActionResult<ApiResponse<LoginResponse>>> DemoLogin([FromBody] DemoLoginRequest? request = null)
    {
        try
        {
            _logger.LogInformation("=== DEMO LOGIN ENDPOINT CALLED ===");
            _logger.LogInformation("Request object: {Request}", request);
            _logger.LogInformation("Request Role: {Role}", request?.Role ?? "NULL");
            _logger.LogInformation("ModelState IsValid: {IsValid}", ModelState.IsValid);
            
            if (!ModelState.IsValid)
            {
                _logger.LogWarning("ModelState validation failed:");
                foreach (var error in ModelState)
                {
                    _logger.LogWarning("  {Key}: {Errors}", error.Key, string.Join(", ", error.Value?.Errors.Select(e => e.ErrorMessage) ?? new string[0]));
                }
                return BadRequest(new ApiError 
                { 
                    Code = "VALIDATION_ERROR", 
                    Message = "Model validation failed"
                });
            }
            
            if (request == null)
            {
                _logger.LogWarning("Demo login request is NULL");
                return BadRequest(new ApiError 
                { 
                    Code = "INVALID_REQUEST", 
                    Message = "Request body is null" 
                });
            }
            
            if (string.IsNullOrWhiteSpace(request.Role))
            {
                _logger.LogWarning("Demo login request has null/empty role. Role value: '{Role}'", request.Role);
                return BadRequest(new ApiError 
                { 
                    Code = "INVALID_REQUEST", 
                    Message = "Role is required" 
                });
            }

            // Define demo users for different roles
            var demoUsers = new Dictionary<string, (string email, string name, List<string> roles, string company)>
            {
                ["admin"] = ("admin@vetterati.com", "Admin User", new List<string> { "admin", "recruiter" }, "Vetterati"),
                ["recruiter"] = ("recruiter@company.com", "Jane Recruiter", new List<string> { "recruiter" }, "TechCorp"),
                ["hiring-manager"] = ("manager@company.com", "John Manager", new List<string> { "hiring_manager" }, "TechCorp"),
                ["candidate"] = ("candidate@email.com", "Alice Candidate", new List<string> { "candidate" }, ""),
                ["interviewer"] = ("interviewer@company.com", "Bob Interviewer", new List<string> { "interviewer" }, "TechCorp"),
                ["hr"] = ("hr@company.com", "Carol HR", new List<string> { "hr", "recruiter" }, "TechCorp")
            };

            if (!demoUsers.ContainsKey(request.Role.ToLower()))
            {
                return BadRequest(new ApiError 
                { 
                    Code = "INVALID_DEMO_ROLE", 
                    Message = $"Invalid demo role. Available roles: {string.Join(", ", demoUsers.Keys)}" 
                });
            }

            var (email, name, roles, company) = demoUsers[request.Role.ToLower()];

            // Check if demo user already exists in database
            var user = await _context.Users
                .FirstOrDefaultAsync(u => u.Email == email);

            if (user == null)
            {
                // Create demo user in database
                user = new User
                {
                    Email = email,
                    Name = name,
                    FirstName = name.Split(' ')[0],
                    LastName = name.Split(' ').Length > 1 ? name.Split(' ')[1] : "",
                    Company = company,
                    SsoProvider = "demo",
                    SsoId = $"demo_{request.Role.ToLower()}",
                    Roles = roles,
                    IsActive = true,
                    CreatedAt = DateTime.UtcNow,
                    UpdatedAt = DateTime.UtcNow,
                    Preferences = new Dictionary<string, object>
                    {
                        { "timezone", "UTC" },
                        { "emailNotifications", true },
                        { "pushNotifications", true },
                        { "marketingEmails", false }
                    }
                };

                _context.Users.Add(user);
                await _context.SaveChangesAsync();

                _logger.LogInformation("Created new demo user: {Email} with role: {Role}", email, request.Role);
            }
            else
            {
                // Ensure existing demo users have preferences
                if (user.Preferences == null || !user.Preferences.Any())
                {
                    user.Preferences = new Dictionary<string, object>
                    {
                        { "timezone", "UTC" },
                        { "emailNotifications", true },
                        { "pushNotifications", true },
                        { "marketingEmails", false }
                    };
                    _context.Users.Update(user);
                    await _context.SaveChangesAsync();
                }
            }

            // Update last login
            user.LastLoginAt = DateTime.UtcNow;
            _context.Users.Update(user);
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

            _logger.LogInformation("Demo login successful for role: {Role}, email: {Email}", request.Role, email);
            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during demo login for role: {Role}", request?.Role ?? "null");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred during demo login" 
            });
        }
    }

    /// <summary>
    /// Get list of available demo users for quick access.
    /// GET /api/v1/auth/demo-users
    /// </summary>
    [HttpGet("demo-users")]
    public ActionResult<ApiResponse<List<DemoUserInfo>>> GetDemoUsers()
    {
        try
        {
            var demoUsers = new List<DemoUserInfo>
            {
                new() { Role = "admin", Name = "Admin User", Email = "admin@vetterati.com", Description = "Full system administrator with all permissions" },
                new() { Role = "recruiter", Name = "Jane Recruiter", Email = "recruiter@company.com", Description = "Recruiter who can manage candidates and jobs" },
                new() { Role = "hiring-manager", Name = "John Manager", Email = "manager@company.com", Description = "Hiring manager who can review candidates and make decisions" },
                new() { Role = "candidate", Name = "Alice Candidate", Email = "candidate@email.com", Description = "Job candidate applying for positions" },
                new() { Role = "interviewer", Name = "Bob Interviewer", Email = "interviewer@company.com", Description = "Technical interviewer who conducts interviews" },
                new() { Role = "hr", Name = "Carol HR", Email = "hr@company.com", Description = "HR representative with recruiting capabilities" }
            };

            return Ok(new ApiResponse<List<DemoUserInfo>> 
            { 
                Data = demoUsers 
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting demo users list");
            return StatusCode(500, new ApiError 
            { 
                Code = "INTERNAL_ERROR", 
                Message = "An error occurred while fetching demo users" 
            });
        }    }

    private string GenerateSecureToken()
    {
        using var rng = RandomNumberGenerator.Create();
        var bytes = new byte[32];
        rng.GetBytes(bytes);
        return Convert.ToBase64String(bytes).Replace("+", "-").Replace("/", "_").Replace("=", "");
    }


}

using AuthService.Data;
using Microsoft.EntityFrameworkCore;
using Vetterati.Shared.Models;
using BCrypt.Net;

namespace AuthService.Services;

public interface IUserManagementService
{
    Task<User?> GetUserByIdAsync(Guid userId);
    Task<User?> GetUserByEmailAsync(string email);
    Task<bool> CreateUserAsync(User user, string password);
    Task<bool> UpdateUserAsync(User user);
    Task<bool> DeleteUserAsync(Guid userId);
    Task<bool> ChangePasswordAsync(Guid userId, string currentPassword, string newPassword);
    Task<bool> ResetPasswordAsync(Guid userId, string newPassword);
    Task<bool> ActivateUserAsync(Guid userId);
    Task<bool> DeactivateUserAsync(Guid userId);
    Task<List<User>> GetUsersAsync(int page = 1, int pageSize = 50);
    Task<bool> AddUserToOrganizationAsync(Guid userId, Guid organizationId, string role);
    Task<bool> RemoveUserFromOrganizationAsync(Guid userId, Guid organizationId);
    Task<List<Organization>> GetUserOrganizationsAsync(Guid userId);
}

public class UserManagementService : IUserManagementService
{
    private readonly AuthDbContext _context;
    private readonly IPasswordValidationService _passwordValidation;
    private readonly ILogger<UserManagementService> _logger;

    public UserManagementService(
        AuthDbContext context,
        IPasswordValidationService passwordValidation,
        ILogger<UserManagementService> logger)
    {
        _context = context;
        _passwordValidation = passwordValidation;
        _logger = logger;
    }

    public async Task<User?> GetUserByIdAsync(Guid userId)
    {
        try
        {
            return await _context.Users
                .FirstOrDefaultAsync(u => u.Id == userId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user by ID: {UserId}", userId);
            return null;
        }
    }

    public async Task<User?> GetUserByEmailAsync(string email)
    {
        try
        {
            return await _context.Users
                .FirstOrDefaultAsync(u => u.Email.ToLower() == email.ToLower());
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user by email: {Email}", email);
            return null;
        }
    }

    public async Task<bool> CreateUserAsync(User user, string password)
    {
        try
        {
            // Validate password
            var passwordValidation = _passwordValidation.ValidatePassword(password);
            if (!passwordValidation.IsValid)
            {
                _logger.LogWarning("Password validation failed for user: {Email}", user.Email);
                return false;
            }

            // Check if user already exists
            var existingUser = await GetUserByEmailAsync(user.Email);
            if (existingUser != null)
            {
                _logger.LogWarning("User already exists with email: {Email}", user.Email);
                return false;
            }

            // Hash password
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(password);
            user.CreatedAt = DateTime.UtcNow;
            user.UpdatedAt = DateTime.UtcNow;

            _context.Users.Add(user);
            await _context.SaveChangesAsync();

            _logger.LogInformation("User created successfully: {UserId}", user.Id);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating user: {Email}", user.Email);
            return false;
        }
    }

    public async Task<bool> UpdateUserAsync(User user)
    {
        try
        {
            var existingUser = await GetUserByIdAsync(user.Id);
            if (existingUser == null)
            {
                _logger.LogWarning("User not found for update: {UserId}", user.Id);
                return false;
            }

            // Update fields (except password and sensitive data)
            existingUser.Name = user.Name;
            existingUser.FirstName = user.FirstName;
            existingUser.LastName = user.LastName;
            existingUser.Company = user.Company;
            existingUser.Roles = user.Roles;
            existingUser.Preferences = user.Preferences;
            existingUser.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            _logger.LogInformation("User updated successfully: {UserId}", user.Id);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating user: {UserId}", user.Id);
            return false;
        }
    }

    public async Task<bool> DeleteUserAsync(Guid userId)
    {
        try
        {
            var user = await GetUserByIdAsync(userId);
            if (user == null)
            {
                _logger.LogWarning("User not found for deletion: {UserId}", userId);
                return false;
            }

            // Soft delete by deactivating
            user.IsActive = false;
            user.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            _logger.LogInformation("User deleted (deactivated): {UserId}", userId);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting user: {UserId}", userId);
            return false;
        }
    }

    public async Task<bool> ChangePasswordAsync(Guid userId, string currentPassword, string newPassword)
    {
        try
        {
            var user = await GetUserByIdAsync(userId);
            if (user == null || user.PasswordHash == null)
            {
                _logger.LogWarning("User not found or no password set: {UserId}", userId);
                return false;
            }

            // Verify current password
            if (!BCrypt.Net.BCrypt.Verify(currentPassword, user.PasswordHash))
            {
                _logger.LogWarning("Current password verification failed for user: {UserId}", userId);
                return false;
            }

            // Validate new password
            var passwordValidation = _passwordValidation.ValidatePassword(newPassword);
            if (!passwordValidation.IsValid)
            {
                _logger.LogWarning("New password validation failed for user: {UserId}", userId);
                return false;
            }

            // Update password
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(newPassword);
            user.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            _logger.LogInformation("Password changed successfully for user: {UserId}", userId);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error changing password for user: {UserId}", userId);
            return false;
        }
    }

    public async Task<bool> ResetPasswordAsync(Guid userId, string newPassword)
    {
        try
        {
            var user = await GetUserByIdAsync(userId);
            if (user == null)
            {
                _logger.LogWarning("User not found for password reset: {UserId}", userId);
                return false;
            }

            // Validate new password
            var passwordValidation = _passwordValidation.ValidatePassword(newPassword);
            if (!passwordValidation.IsValid)
            {
                _logger.LogWarning("New password validation failed for user: {UserId}", userId);
                return false;
            }

            // Update password
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(newPassword);
            user.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            _logger.LogInformation("Password reset successfully for user: {UserId}", userId);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error resetting password for user: {UserId}", userId);
            return false;
        }
    }

    public async Task<bool> ActivateUserAsync(Guid userId)
    {
        try
        {
            var user = await GetUserByIdAsync(userId);
            if (user == null)
            {
                _logger.LogWarning("User not found for activation: {UserId}", userId);
                return false;
            }

            user.IsActive = true;
            user.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            _logger.LogInformation("User activated: {UserId}", userId);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error activating user: {UserId}", userId);
            return false;
        }
    }

    public async Task<bool> DeactivateUserAsync(Guid userId)
    {
        try
        {
            var user = await GetUserByIdAsync(userId);
            if (user == null)
            {
                _logger.LogWarning("User not found for deactivation: {UserId}", userId);
                return false;
            }

            user.IsActive = false;
            user.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            _logger.LogInformation("User deactivated: {UserId}", userId);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deactivating user: {UserId}", userId);
            return false;
        }
    }

    public async Task<List<User>> GetUsersAsync(int page = 1, int pageSize = 50)
    {
        try
        {
            return await _context.Users
                .OrderBy(u => u.Email)
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting users list");
            return new List<User>();
        }
    }

    public async Task<bool> AddUserToOrganizationAsync(Guid userId, Guid organizationId, string role)
    {
        try
        {
            var existingAssociation = await _context.UserOrganizations
                .FirstOrDefaultAsync(uo => uo.UserId == userId && uo.OrganizationId == organizationId);

            if (existingAssociation != null)
            {
                // Update existing role
                existingAssociation.Role = role;
                existingAssociation.IsActive = true;
                existingAssociation.UpdatedAt = DateTime.UtcNow;
            }
            else
            {
                // Create new association
                var userOrg = new UserOrganization
                {
                    UserId = userId,
                    OrganizationId = organizationId,
                    Role = role,
                    IsActive = true,
                    JoinedAt = DateTime.UtcNow
                };

                _context.UserOrganizations.Add(userOrg);
            }

            await _context.SaveChangesAsync();

            _logger.LogInformation("User {UserId} added to organization {OrganizationId} with role {Role}", 
                userId, organizationId, role);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding user to organization: {UserId}, {OrganizationId}", 
                userId, organizationId);
            return false;
        }
    }

    public async Task<bool> RemoveUserFromOrganizationAsync(Guid userId, Guid organizationId)
    {
        try
        {
            var userOrg = await _context.UserOrganizations
                .FirstOrDefaultAsync(uo => uo.UserId == userId && uo.OrganizationId == organizationId);

            if (userOrg == null)
            {
                _logger.LogWarning("User organization association not found: {UserId}, {OrganizationId}", 
                    userId, organizationId);
                return false;
            }

            userOrg.IsActive = false;
            userOrg.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            _logger.LogInformation("User {UserId} removed from organization {OrganizationId}", 
                userId, organizationId);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error removing user from organization: {UserId}, {OrganizationId}", 
                userId, organizationId);
            return false;
        }
    }

    public async Task<List<Organization>> GetUserOrganizationsAsync(Guid userId)
    {
        try
        {
            return await _context.UserOrganizations
                .Where(uo => uo.UserId == userId && uo.IsActive)
                .Include(uo => uo.Organization)
                .Select(uo => uo.Organization)
                .ToListAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user organizations: {UserId}", userId);
            return new List<Organization>();
        }
    }
}

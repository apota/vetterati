using System.Text.RegularExpressions;

namespace AuthService.Services;

public interface IPasswordValidationService
{
    PasswordValidationResult ValidatePassword(string password);
    bool IsPasswordStrong(string password);
}

public class PasswordValidationService : IPasswordValidationService
{
    private readonly ILogger<PasswordValidationService> _logger;
    private readonly PasswordPolicy _policy;

    public PasswordValidationService(ILogger<PasswordValidationService> logger, IConfiguration configuration)
    {
        _logger = logger;
        _policy = configuration.GetSection("PasswordPolicy").Get<PasswordPolicy>() ?? new PasswordPolicy();
    }

    public PasswordValidationResult ValidatePassword(string password)
    {
        var result = new PasswordValidationResult();

        if (string.IsNullOrEmpty(password))
        {
            result.AddError("Password is required");
            return result;
        }

        // Check minimum length
        if (password.Length < _policy.MinLength)
        {
            result.AddError($"Password must be at least {_policy.MinLength} characters long");
        }

        // Check maximum length
        if (password.Length > _policy.MaxLength)
        {
            result.AddError($"Password must not exceed {_policy.MaxLength} characters");
        }

        // Check for uppercase letter
        if (_policy.RequireUppercase && !Regex.IsMatch(password, @"[A-Z]"))
        {
            result.AddError("Password must contain at least one uppercase letter");
        }

        // Check for lowercase letter
        if (_policy.RequireLowercase && !Regex.IsMatch(password, @"[a-z]"))
        {
            result.AddError("Password must contain at least one lowercase letter");
        }

        // Check for digit
        if (_policy.RequireDigit && !Regex.IsMatch(password, @"\d"))
        {
            result.AddError("Password must contain at least one digit");
        }

        // Check for special character
        if (_policy.RequireSpecialChar && !Regex.IsMatch(password, @"[!@#$%^&*()_+\-=\[\]{};':""\\|,.<>\/?]"))
        {
            result.AddError("Password must contain at least one special character");
        }

        // Check for common weak patterns
        if (IsCommonWeakPassword(password))
        {
            result.AddError("Password is too common or weak");
        }

        // Check for sequential characters
        if (HasSequentialCharacters(password))
        {
            result.AddError("Password cannot contain sequential characters (e.g., '123', 'abc')");
        }

        return result;
    }

    public bool IsPasswordStrong(string password)
    {
        return ValidatePassword(password).IsValid;
    }

    private bool IsCommonWeakPassword(string password)
    {
        var commonWeakPasswords = new[]
        {
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master",
            "password1", "123456789", "12345678", "12345"
        };

        return commonWeakPasswords.Contains(password.ToLower());
    }

    private bool HasSequentialCharacters(string password)
    {
        // Check for sequential numbers (123, 456, etc.)
        for (int i = 0; i < password.Length - 2; i++)
        {
            if (char.IsDigit(password[i]) && char.IsDigit(password[i + 1]) && char.IsDigit(password[i + 2]))
            {
                var num1 = password[i] - '0';
                var num2 = password[i + 1] - '0';
                var num3 = password[i + 2] - '0';

                if (num2 == num1 + 1 && num3 == num2 + 1)
                    return true;
            }
        }

        // Check for sequential letters (abc, def, etc.)
        for (int i = 0; i < password.Length - 2; i++)
        {
            if (char.IsLetter(password[i]) && char.IsLetter(password[i + 1]) && char.IsLetter(password[i + 2]))
            {
                var char1 = char.ToLower(password[i]);
                var char2 = char.ToLower(password[i + 1]);
                var char3 = char.ToLower(password[i + 2]);

                if (char2 == char1 + 1 && char3 == char2 + 1)
                    return true;
            }
        }

        return false;
    }
}

public class PasswordValidationResult
{
    public List<string> Errors { get; } = new();
    public bool IsValid => Errors.Count == 0;

    public void AddError(string error)
    {
        Errors.Add(error);
    }
}

public class PasswordPolicy
{
    public int MinLength { get; set; } = 8;
    public int MaxLength { get; set; } = 128;
    public bool RequireUppercase { get; set; } = true;
    public bool RequireLowercase { get; set; } = true;
    public bool RequireDigit { get; set; } = true;
    public bool RequireSpecialChar { get; set; } = true;
    public int MaxFailedAttempts { get; set; } = 5;
    public TimeSpan LockoutDuration { get; set; } = TimeSpan.FromMinutes(15);
}

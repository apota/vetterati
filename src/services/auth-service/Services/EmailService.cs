using System;
using System.IO;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace AuthService.Services;

public interface IEmailService
{
    Task SendPasswordResetEmailAsync(string toEmail, string resetToken, string userName);
    Task SendWelcomeEmailAsync(string toEmail, string userName);
}

public class EmailService : IEmailService
{
    private readonly ILogger<EmailService> _logger;
    private readonly IConfiguration _configuration;

    public EmailService(ILogger<EmailService> logger, IConfiguration configuration)
    {
        _logger = logger;
        _configuration = configuration;
    }

    public async Task SendPasswordResetEmailAsync(string toEmail, string resetToken, string userName)
    {
        try
        {
            var frontendUrl = _configuration["Frontend:BaseUrl"] ?? "EMAIL-SERVICE-FALLBACK";
            var resetUrl = $"{frontendUrl}/reset-password?token={resetToken}";
            
            var emailBody = GeneratePasswordResetEmailBody(userName, resetUrl);
            
            _logger.LogInformation("Password reset email would be sent to {Email}", toEmail);
            _logger.LogInformation("Reset URL: {ResetUrl}", resetUrl);
            
            // Save email to file for demo purposes
            await SaveEmailToFileAsync(toEmail, "Password Reset - Vetterati ATS", emailBody);
            
            // TODO: For production, implement actual email sending:
            // - SendGrid: await SendGridSendAsync(toEmail, "Password Reset", emailBody);
            // - SMTP: await SmtpSendAsync(toEmail, "Password Reset", emailBody);
            
            await Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send password reset email to {Email}", toEmail);
            throw;
        }
    }

    public async Task SendWelcomeEmailAsync(string toEmail, string userName)
    {
        try
        {
            var emailBody = GenerateWelcomeEmailBody(userName);
            
            _logger.LogInformation("Welcome email would be sent to {Email}", toEmail);
            
            // Save email to file for demo purposes
            await SaveEmailToFileAsync(toEmail, "Welcome to Vetterati ATS", emailBody);
            
            // TODO: For production, implement actual email sending
            
            await Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send welcome email to {Email}", toEmail);
            throw;
        }
    }

    private string GeneratePasswordResetEmailBody(string userName, string resetUrl)
    {
        return $@"
<!DOCTYPE html>
<html>
<head>
    <meta charset=""utf-8"">
    <title>Password Reset - Vetterati ATS</title>
</head>
<body style=""font-family: Arial, sans-serif; line-height: 1.6; color: #333;"">
    <div style=""max-width: 600px; margin: 0 auto; padding: 20px;"">
        <h1 style=""color: #1976d2; text-align: center;"">Vetterati ATS</h1>
        
        <h2>Password Reset Request</h2>
        
        <p>Hello {userName},</p>
        
        <p>We received a request to reset your password for your Vetterati ATS account. If you made this request, please click the button below to reset your password:</p>
        
        <div style=""text-align: center; margin: 30px 0;"">
            <a href=""{resetUrl}"" style=""background-color: #1976d2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;"">Reset Your Password</a>
        </div>
        
        <p>Or copy and paste this link into your browser:</p>
        <p style=""word-break: break-all; color: #1976d2;"">{resetUrl}</p>
        
        <p><strong>This link will expire in 1 hour</strong> for security reasons.</p>
        
        <p>If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.</p>
        
        <hr style=""margin: 30px 0; border: none; border-top: 1px solid #eee;"">
        
        <p style=""font-size: 12px; color: #666;"">
            This email was sent from Vetterati ATS. If you have any questions, please contact our support team.
        </p>
    </div>
</body>
</html>";
    }

    private string GenerateWelcomeEmailBody(string userName)
    {
        return $@"
<!DOCTYPE html>
<html>
<head>
    <meta charset=""utf-8"">
    <title>Welcome to Vetterati ATS</title>
</head>
<body style=""font-family: Arial, sans-serif; line-height: 1.6; color: #333;"">
    <div style=""max-width: 600px; margin: 0 auto; padding: 20px;"">
        <h1 style=""color: #1976d2; text-align: center;"">Welcome to Vetterati ATS</h1>
        
        <p>Hello {userName},</p>
        
        <p>Welcome to Vetterati ATS! Your account has been successfully created and you're ready to start managing your recruitment process.</p>
        
        <p>Here are some things you can do to get started:</p>
        
        <ul>
            <li>Set up your organization profile</li>
            <li>Create your first job posting</li>
            <li>Invite team members to collaborate</li>
            <li>Explore our analytics dashboard</li>
        </ul>
        
        <div style=""text-align: center; margin: 30px 0;"">
            <a href=""http://localhost:3000/dashboard"" style=""background-color: #1976d2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;"">Get Started</a>
        </div>
        
        <p>If you have any questions or need help getting started, don't hesitate to reach out to our support team.</p>
        
        <p>Thank you for choosing Vetterati ATS!</p>
        
        <hr style=""margin: 30px 0; border: none; border-top: 1px solid #eee;"">
        
        <p style=""font-size: 12px; color: #666;"">
            This email was sent from Vetterati ATS. If you have any questions, please contact our support team.
        </p>
    </div>
</body>
</html>";
    }

    private async Task SaveEmailToFileAsync(string toEmail, string subject, string body)
    {
        try
        {
            // Create emails directory if it doesn't exist
            var emailsDir = Path.Combine(Directory.GetCurrentDirectory(), "emails");
            if (!Directory.Exists(emailsDir))
            {
                Directory.CreateDirectory(emailsDir);
            }
            
            // Generate filename with timestamp
            var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            var safeEmail = toEmail.Replace("@", "_at_").Replace(".", "_");
            var filename = $"{timestamp}_{safeEmail}_password_reset.html";
            var filePath = Path.Combine(emailsDir, filename);
            
            // Create email content with headers
            var emailContent = $@"
TO: {toEmail}
SUBJECT: {subject}
DATE: {DateTime.Now:yyyy-MM-dd HH:mm:ss}
==========================================

{body}";
            
            await File.WriteAllTextAsync(filePath, emailContent);
            _logger.LogInformation("Email saved to file: {FilePath}", filePath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save email to file for {Email}", toEmail);
            // Don't throw here as this is just for demo purposes
        }
    }
}

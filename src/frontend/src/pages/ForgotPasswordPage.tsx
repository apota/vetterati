import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Container,
  Paper,
  Link,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { authService, ForgotPasswordRequest } from '../services/authService';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const ForgotPasswordPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resetUrl, setResetUrl] = useState<string | null>(null);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues,
  } = useForm<ForgotPasswordRequest>();

  const onSubmit = async (data: ForgotPasswordRequest) => {
    setIsLoading(true);
    setError(null);
    setResetUrl(null);

    try {
      const response = await authService.forgotPassword(data);
      console.log('Forgot password response:', response);
      setSuccess(true);
      
      // Check if response contains resetUrl for demo purposes
      if (response && (response as any).resetUrl) {
        console.log('Reset URL found:', (response as any).resetUrl);
        setResetUrl((response as any).resetUrl);
      } else {
        console.log('No reset URL in response:', response);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.message || 
        'Failed to send password reset email. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <Container component="main" maxWidth="sm">
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            minHeight: '100vh',
          }}
        >
          <Paper
            elevation={6}
            sx={{
              padding: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              width: '100%',
              maxWidth: 400,
              mt: 8,
            }}
          >
            <Typography component="h1" variant="h4" gutterBottom>
              Check Your Email
            </Typography>
            
            <Alert severity="success" sx={{ width: '100%', mb: 3 }}>
              We've sent a password reset link to <strong>{getValues('email')}</strong>
            </Alert>

            {resetUrl && (
              <Alert severity="info" sx={{ width: '100%', mb: 3 }}>
                <Typography variant="body2" component="div">
                  <strong>Demo Mode:</strong> Here's your reset link:
                </Typography>
                <Typography variant="body2" component="div" sx={{ mt: 1, wordBreak: 'break-all' }}>
                  <a href={resetUrl} target="_blank" rel="noopener noreferrer" style={{ color: '#1976d2' }}>
                    {resetUrl}
                  </a>
                </Typography>
              </Alert>
            )}

            <Typography variant="body1" color="text.secondary" sx={{ mb: 3, textAlign: 'center' }}>
              Please check your email and click the link to reset your password. 
              The link will expire in 1 hour.
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: '100%' }}>
              <Button
                variant="outlined"
                onClick={() => onSubmit(getValues())}
                disabled={isLoading}
                fullWidth
              >
                {isLoading ? 'Resending...' : 'Resend Email'}
              </Button>

              <Button
                variant="text"
                onClick={() => navigate('/login')}
                startIcon={<ArrowBackIcon />}
                fullWidth
              >
                Back to Login
              </Button>
            </Box>
          </Paper>
        </Box>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <Paper
          elevation={6}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
            maxWidth: 400,
            mt: 8,
          }}
        >
          <Typography component="h1" variant="h4" gutterBottom>
            Forgot Password
          </Typography>
          
          <Typography component="h2" variant="h6" color="text.secondary" gutterBottom sx={{ textAlign: 'center' }}>
            Enter your email address and we'll send you a link to reset your password
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 1, width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              autoComplete="email"
              autoFocus
              error={!!errors.email}
              helperText={errors.email?.message}
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address',
                },
              })}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading}
            >
              {isLoading ? 'Sending...' : 'Send Reset Link'}
            </Button>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Link
                component="button"
                variant="body2"
                onClick={() => navigate('/login')}
                sx={{ textDecoration: 'none' }}
              >
                <ArrowBackIcon sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
                Back to Login
              </Link>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default ForgotPasswordPage;

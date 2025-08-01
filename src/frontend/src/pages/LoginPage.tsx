import React, { useState, useEffect } from 'react';
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
  Divider,
  Chip,
  Grid,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

interface LoginFormData {
  email: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const { login, demoLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<LoginFormData>();

  // Handle pre-filled credentials from registration
  useEffect(() => {
    const state = location.state as any;
    if (state?.fromRegistration && state?.email && state?.password) {
      setValue('email', state.email);
      setValue('password', state.password);
      setShowSuccessMessage(true);
      // Clear the navigation state to prevent showing the message on refresh
      window.history.replaceState({}, document.title);
    }
  }, [location.state, setValue]);

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await login(data.email, data.password);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Demo users for quick login
  const demoUsers = [
    { role: 'admin', name: 'Admin User', description: 'Full system administrator', color: 'error' as const },
    { role: 'recruiter', name: 'Jane Recruiter', description: 'Recruiter role', color: 'primary' as const },
    { role: 'hiring-manager', name: 'John Manager', description: 'Hiring manager', color: 'secondary' as const },
    { role: 'candidate', name: 'Alice Candidate', description: 'Job candidate', color: 'success' as const },
    { role: 'interviewer', name: 'Bob Interviewer', description: 'Technical interviewer', color: 'info' as const },
    { role: 'hr', name: 'Carol HR', description: 'HR representative', color: 'warning' as const },
  ];

  const handleDemoLogin = async (role: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log(`Attempting demo login for role: ${role}`);
      await demoLogin(role);
      console.log('Demo login successful, navigating to dashboard...');
      // Force navigation to dashboard in case automatic redirect doesn't work
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Demo login error:', err);
      
      // More detailed error messages
      let errorMessage = `Demo login failed for ${role}.`;
      
      if (err.response) {
        // Server responded with an error
        const status = err.response.status;
        const data = err.response.data;
        
        if (status === 404) {
          errorMessage = `Demo login endpoint not found. Is the auth service running?`;
        } else if (status === 500) {
          errorMessage = `Server error during demo login. ${data?.message || 'Please try again.'}`;
        } else if (data?.message) {
          errorMessage = data.message;
        } else {
          errorMessage = `HTTP ${status}: ${err.response.statusText}`;
        }
      } else if (err.request) {
        // Network error
        errorMessage = `Cannot connect to auth service. Please check if the backend is running.`;
      } else {
        // Other error
        errorMessage = err.message || `Unknown error during demo login for ${role}`;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

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
            Vetterati ATS
          </Typography>
          <Typography component="h2" variant="h6" color="text.secondary" gutterBottom>
            Sign in to your account
          </Typography>
          
          {showSuccessMessage && (
            <Alert severity="success" sx={{ width: '100%', mb: 2 }}>
              Account created successfully! Your credentials have been pre-filled below.
            </Alert>
          )}
          
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
            <TextField
              margin="normal"
              required
              fullWidth
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              error={!!errors.password}
              helperText={errors.password?.message}
              {...register('password', {
                required: 'Password is required',
                minLength: {
                  value: 6,
                  message: 'Password must be at least 6 characters',
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
              {isLoading ? 'Signing In...' : 'Sign In'}
            </Button>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Link
                component="button"
                variant="body2"
                onClick={() => navigate('/forgot-password')}
                sx={{ textDecoration: 'none', mb: 2, display: 'block' }}
              >
                Forgot your password?
              </Link>
              
              <Typography variant="body2">
                Don't have an account?{' '}
                <Link
                  component="button"
                  variant="body2"
                  onClick={() => navigate('/register')}
                  sx={{ textDecoration: 'none' }}
                >
                  Create account here
                </Link>
              </Typography>
            </Box>

            <Divider sx={{ my: 3 }}>
              <Typography variant="body2" color="text.secondary">
                Quick Demo Login
              </Typography>
            </Divider>

            <Typography variant="body2" color="text.secondary" sx={{ mb: 2, textAlign: 'center' }}>
              Click any role below to instantly log in as a demo user
            </Typography>

            <Grid container spacing={1}>
              {demoUsers.map((user) => (
                <Grid item xs={6} key={user.role}>
                  <Chip
                    label={isLoading ? 'Loading...' : user.name}
                    variant="outlined"
                    color={user.color}
                    onClick={() => handleDemoLogin(user.role)}
                    disabled={isLoading}
                    sx={{ 
                      width: '100%', 
                      cursor: isLoading ? 'default' : 'pointer',
                      '&:hover': {
                        backgroundColor: (theme) => 
                          isLoading ? 'transparent' : theme.palette[user.color].main + '20'
                      }
                    }}
                  />
                </Grid>
              ))}
            </Grid>

            <Typography variant="caption" color="text.secondary" sx={{ mt: 2, textAlign: 'center', display: 'block' }}>
              Demo users are for testing purposes only
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;

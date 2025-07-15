import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Grid,
  Paper,
  Avatar,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Stack,
  CircularProgress
} from '@mui/material';
import { Edit, Save, Cancel, Person, Business, Settings } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';

const ProfilePage: React.FC = () => {
  const { user, refreshUser, isAuthenticated } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [profileData, setProfileData] = useState<any>(null);
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    company: '',
    preferences: {
      timezone: 'UTC',
      emailNotifications: true,
      pushNotifications: true,
      marketingEmails: false
    }
  });

  // Fetch profile data
  useEffect(() => {
    const fetchProfile = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        console.log('ProfilePage: Fetching profile data...');
        console.log('ProfilePage: isAuthenticated:', isAuthenticated);
        console.log('ProfilePage: user from context:', user);
        
        if (isAuthenticated) {
          // Use user from context if available, otherwise fetch from API
          if (user) {
            console.log('ProfilePage: Using user from context');
            setProfileData(user);
          } else {
            console.log('ProfilePage: Fetching from API...');
            const userInfo = await authService.getUserInfo();
            console.log('ProfilePage: Profile data received:', userInfo);
            setProfileData(userInfo);
          }
        } else {
          console.log('ProfilePage: User not authenticated');
          setError('Please log in to view your profile');
        }
      } catch (err) {
        console.error('ProfilePage: Error fetching profile:', err);
        setError('Failed to load profile data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [isAuthenticated, user]); // Re-fetch when authentication state or user changes

  const currentUser = user || profileData;

  useEffect(() => {
    if (currentUser) {
      setFormData({
        firstName: currentUser.firstName || '',
        lastName: currentUser.lastName || '',
        email: currentUser.email || '',
        company: currentUser.company || '',
        preferences: {
          timezone: currentUser.preferences?.timezone || 'UTC',
          emailNotifications: currentUser.preferences?.emailNotifications ?? true,
          pushNotifications: currentUser.preferences?.pushNotifications ?? true,
          marketingEmails: currentUser.preferences?.marketingEmails ?? false
        }
      });
    }
  }, [currentUser]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePreferenceChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [field]: value
      }
    }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await authService.updateProfile({
        firstName: formData.firstName,
        lastName: formData.lastName,
        company: formData.company,
        preferences: formData.preferences
      });

      await refreshUser();
      setIsEditing(false);
      setSuccess('Profile updated successfully');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    if (currentUser) {
      setFormData({
        firstName: currentUser.firstName || '',
        lastName: currentUser.lastName || '',
        email: currentUser.email || '',
        company: currentUser.company || '',
        preferences: {
          timezone: currentUser.preferences?.timezone || 'UTC',
          emailNotifications: currentUser.preferences?.emailNotifications ?? true,
          pushNotifications: currentUser.preferences?.pushNotifications ?? true,
          marketingEmails: currentUser.preferences?.marketingEmails ?? false
        }
      });
    }
    setIsEditing(false);
    setError(null);
    setSuccess(null);
  };

  const timezones = [
    'UTC',
    'America/New_York',
    'America/Los_Angeles',
    'America/Chicago',
    'America/Denver',
    'Europe/London',
    'Europe/Paris',
    'Europe/Berlin',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Asia/Kolkata',
    'Australia/Sydney'
  ];

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  if (!currentUser) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>No profile data available</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Profile Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your account settings and preferences
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Profile Information */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Person sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6">Personal Information</Typography>
                <Box sx={{ ml: 'auto' }}>
                  {!isEditing ? (
                    <Button
                      startIcon={<Edit />}
                      variant="outlined"
                      onClick={() => setIsEditing(true)}
                    >
                      Edit
                    </Button>
                  ) : (
                    <Stack direction="row" spacing={1}>
                      <Button
                        startIcon={<Save />}
                        variant="contained"
                        onClick={handleSave}
                        disabled={isLoading}
                      >
                        {isLoading ? 'Saving...' : 'Save'}
                      </Button>
                      <Button
                        startIcon={<Cancel />}
                        variant="outlined"
                        onClick={handleCancel}
                        disabled={isLoading}
                      >
                        Cancel
                      </Button>
                    </Stack>
                  )}
                </Box>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="First Name"
                    value={formData.firstName}
                    onChange={(e) => handleInputChange('firstName', e.target.value)}
                    disabled={!isEditing}
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    value={formData.lastName}
                    onChange={(e) => handleInputChange('lastName', e.target.value)}
                    disabled={!isEditing}
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email"
                    value={formData.email}
                    disabled
                    variant="outlined"
                    helperText="Email cannot be changed"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Company"
                    value={formData.company}
                    onChange={(e) => handleInputChange('company', e.target.value)}
                    disabled={!isEditing}
                    variant="outlined"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Profile Avatar */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar
                sx={{ 
                  width: 120, 
                  height: 120, 
                  mx: 'auto', 
                  mb: 2,
                  fontSize: '3rem'
                }}
              >
                {currentUser.firstName?.[0] || currentUser.name?.[0] || currentUser.email[0]}
              </Avatar>
              <Typography variant="h6" gutterBottom>
                {currentUser.firstName && currentUser.lastName 
                  ? `${currentUser.firstName} ${currentUser.lastName}`
                  : currentUser.name || currentUser.email
                }
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {currentUser.email}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Chip 
                  label={currentUser.roles?.[0] || 'User'} 
                  size="small" 
                  color="primary"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Preferences */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Settings sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6">Preferences</Typography>
              </Box>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Timezone</InputLabel>
                    <Select
                      value={formData.preferences.timezone}
                      onChange={(e) => handlePreferenceChange('timezone', e.target.value)}
                      disabled={!isEditing}
                      label="Timezone"
                    >
                      {timezones.map((tz) => (
                        <MenuItem key={tz} value={tz}>
                          {tz}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Notification Settings
                    </Typography>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formData.preferences.emailNotifications}
                          onChange={(e) => handlePreferenceChange('emailNotifications', e.target.checked)}
                          disabled={!isEditing}
                        />
                      }
                      label="Email Notifications"
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formData.preferences.pushNotifications}
                          onChange={(e) => handlePreferenceChange('pushNotifications', e.target.checked)}
                          disabled={!isEditing}
                        />
                      }
                      label="Push Notifications"
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formData.preferences.marketingEmails}
                          onChange={(e) => handlePreferenceChange('marketingEmails', e.target.checked)}
                          disabled={!isEditing}
                        />
                      }
                      label="Marketing Emails"
                    />
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProfilePage;
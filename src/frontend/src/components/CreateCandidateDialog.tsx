import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Box,
  Typography,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
  Divider,
  Stack
} from '@mui/material';
import { Close as CloseIcon, Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { CandidateDetails, CandidateCreateRequest } from '../types/candidate';
import { CandidateService } from '../services/candidateService';

interface CreateCandidateDialogProps {
  open: boolean;
  onClose: () => void;
  onCreated: (candidate: CandidateDetails) => void;
}

const CreateCandidateDialog: React.FC<CreateCandidateDialogProps> = ({
  open,
  onClose,
  onCreated
}) => {
  const [formData, setFormData] = useState<CandidateCreateRequest>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    location_city: '',
    location_state: '',
    location_country: '',
    linkedin_url: '',
    portfolio_url: '',
    github_url: '',
    total_years_experience: 0,
    career_level: 'entry',
    current_salary: 0,
    expected_salary: 0,
    summary: '',
    status: 'active',
    source: '',
    skills: []
  });

  const [newSkill, setNewSkill] = useState({
    name: '',
    proficiency_level: 'intermediate' as 'beginner' | 'intermediate' | 'advanced' | 'expert',
    years_experience: 0
  });

  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof CandidateCreateRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAddSkill = () => {
    if (newSkill.name.trim()) {
      setFormData(prev => ({
        ...prev,
        skills: [...(prev.skills || []), newSkill]
      }));
      setNewSkill({
        name: '',
        proficiency_level: 'intermediate',
        years_experience: 0
      });
    }
  };

  const handleRemoveSkill = (index: number) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills?.filter((_, i) => i !== index) || []
    }));
  };

  const handleCreate = async () => {
    if (!formData.first_name || !formData.last_name || !formData.email) {
      setError('Please fill in all required fields');
      return;
    }

    setCreating(true);
    setError(null);

    try {
      const newCandidate = await CandidateService.createCandidate(formData);
      onCreated(newCandidate);
      handleClose();
    } catch (err: any) {
      console.error('Error creating candidate:', err);
      setError(err.response?.data?.message || err.message || 'Failed to create candidate');
    } finally {
      setCreating(false);
    }
  };

  const handleClose = () => {
    setError(null);
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      location_city: '',
      location_state: '',
      location_country: '',
      linkedin_url: '',
      portfolio_url: '',
      github_url: '',
      total_years_experience: 0,
      career_level: 'entry',
      current_salary: 0,
      expected_salary: 0,
      summary: '',
      status: 'active',
      source: '',
      skills: []
    });
    setNewSkill({
      name: '',
      proficiency_level: 'intermediate',
      years_experience: 0
    });
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Create New Candidate</Typography>
          <IconButton onClick={handleClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Personal Information */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Personal Information
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="First Name"
              value={formData.first_name}
              onChange={(e) => handleInputChange('first_name', e.target.value)}
              required
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Last Name"
              value={formData.last_name}
              onChange={(e) => handleInputChange('last_name', e.target.value)}
              required
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              required
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Phone"
              value={formData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
            />
          </Grid>

          {/* Location */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
              Location
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="City"
              value={formData.location_city}
              onChange={(e) => handleInputChange('location_city', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="State"
              value={formData.location_state}
              onChange={(e) => handleInputChange('location_state', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Country"
              value={formData.location_country}
              onChange={(e) => handleInputChange('location_country', e.target.value)}
            />
          </Grid>

          {/* Career Information */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
              Career Information
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Career Level</InputLabel>
              <Select
                value={formData.career_level}
                onChange={(e) => handleInputChange('career_level', e.target.value)}
                label="Career Level"
              >
                <MenuItem value="entry">Entry Level</MenuItem>
                <MenuItem value="mid">Mid Level</MenuItem>
                <MenuItem value="senior">Senior Level</MenuItem>
                <MenuItem value="executive">Executive</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Years of Experience"
              type="number"
              value={formData.total_years_experience}
              onChange={(e) => handleInputChange('total_years_experience', parseInt(e.target.value) || 0)}
              inputProps={{ min: 0 }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Current Salary"
              type="number"
              value={formData.current_salary}
              onChange={(e) => handleInputChange('current_salary', parseInt(e.target.value) || 0)}
              inputProps={{ min: 0 }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Expected Salary"
              type="number"
              value={formData.expected_salary}
              onChange={(e) => handleInputChange('expected_salary', parseInt(e.target.value) || 0)}
              inputProps={{ min: 0 }}
            />
          </Grid>

          {/* Status and Source */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                onChange={(e) => handleInputChange('status', e.target.value)}
                label="Status"
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="hired">Hired</MenuItem>
                <MenuItem value="rejected">Rejected</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Source"
              value={formData.source}
              onChange={(e) => handleInputChange('source', e.target.value)}
            />
          </Grid>

          {/* Social Links */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
              Social Links
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="LinkedIn URL"
              value={formData.linkedin_url}
              onChange={(e) => handleInputChange('linkedin_url', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Portfolio URL"
              value={formData.portfolio_url}
              onChange={(e) => handleInputChange('portfolio_url', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="GitHub URL"
              value={formData.github_url}
              onChange={(e) => handleInputChange('github_url', e.target.value)}
            />
          </Grid>

          {/* Summary */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Summary"
              multiline
              rows={4}
              value={formData.summary}
              onChange={(e) => handleInputChange('summary', e.target.value)}
            />
          </Grid>

          {/* Skills */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
              Skills
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" gap={2} alignItems="center" mb={2}>
              <TextField
                label="Skill Name"
                value={newSkill.name}
                onChange={(e) => setNewSkill(prev => ({ ...prev, name: e.target.value }))}
                size="small"
              />
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Proficiency</InputLabel>
                <Select
                  value={newSkill.proficiency_level}
                  onChange={(e) => setNewSkill(prev => ({ ...prev, proficiency_level: e.target.value as any }))}
                  label="Proficiency"
                >
                  <MenuItem value="beginner">Beginner</MenuItem>
                  <MenuItem value="intermediate">Intermediate</MenuItem>
                  <MenuItem value="advanced">Advanced</MenuItem>
                  <MenuItem value="expert">Expert</MenuItem>
                </Select>
              </FormControl>
              <TextField
                label="Years"
                type="number"
                value={newSkill.years_experience}
                onChange={(e) => setNewSkill(prev => ({ ...prev, years_experience: parseInt(e.target.value) || 0 }))}
                size="small"
                inputProps={{ min: 0 }}
              />
              <IconButton onClick={handleAddSkill} color="primary">
                <AddIcon />
              </IconButton>
            </Box>

            <Stack direction="row" spacing={1} flexWrap="wrap">
              {formData.skills?.map((skill, index) => (
                <Chip
                  key={index}
                  label={`${skill.name} (${skill.proficiency_level})`}
                  onDelete={() => handleRemoveSkill(index)}
                  deleteIcon={<DeleteIcon />}
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Stack>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={creating}>
          Cancel
        </Button>
        <Button 
          onClick={handleCreate} 
          variant="contained" 
          disabled={creating}
        >
          {creating ? <CircularProgress size={20} /> : 'Create Candidate'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateCandidateDialog;

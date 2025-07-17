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
  SelectChangeEvent,
  Box,
  Typography,
  Divider,
  Chip,
  IconButton,
  InputAdornment,
  CircularProgress
} from '@mui/material';
import { Add, Close } from '@mui/icons-material';
import { JobCreateRequest } from '../types/job';

interface CreateJobDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (jobData: JobCreateRequest) => Promise<void>;
  loading?: boolean;
}

const CreateJobDialog: React.FC<CreateJobDialogProps> = ({
  open,
  onClose,
  onSubmit,
  loading = false
}) => {
  const [formData, setFormData] = useState<JobCreateRequest>({
    title: '',
    description: '',
    requirements: '',
    responsibilities: '',
    benefits: '',
    department: '',
    location: '',
    employment_type: '',
    experience_level: '',
    salary_min: undefined,
    salary_max: undefined,
    salary_currency: 'USD',
    priority: 'medium',
    required_skills: [],
    preferred_skills: [],
    certifications: [],
    languages: [],
    seo_title: '',
    seo_description: '',
    keywords: []
  });

  const [newSkill, setNewSkill] = useState('');
  const [newPreferredSkill, setNewPreferredSkill] = useState('');
  const [newCertification, setNewCertification] = useState('');
  const [newLanguage, setNewLanguage] = useState('');
  const [newKeyword, setNewKeyword] = useState('');

  const handleInputChange = (field: keyof JobCreateRequest, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSelectChange = (field: keyof JobCreateRequest) => (event: SelectChangeEvent) => {
    handleInputChange(field, event.target.value);
  };

  const handleAddSkill = () => {
    if (newSkill.trim()) {
      setFormData(prev => ({
        ...prev,
        required_skills: [...(prev.required_skills || []), newSkill.trim()]
      }));
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      required_skills: prev.required_skills?.filter(s => s !== skill) || []
    }));
  };

  const handleAddPreferredSkill = () => {
    if (newPreferredSkill.trim()) {
      setFormData(prev => ({
        ...prev,
        preferred_skills: [...(prev.preferred_skills || []), newPreferredSkill.trim()]
      }));
      setNewPreferredSkill('');
    }
  };

  const handleRemovePreferredSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      preferred_skills: prev.preferred_skills?.filter(s => s !== skill) || []
    }));
  };

  const handleAddCertification = () => {
    if (newCertification.trim()) {
      setFormData(prev => ({
        ...prev,
        certifications: [...(prev.certifications || []), newCertification.trim()]
      }));
      setNewCertification('');
    }
  };

  const handleRemoveCertification = (cert: string) => {
    setFormData(prev => ({
      ...prev,
      certifications: prev.certifications?.filter(c => c !== cert) || []
    }));
  };

  const handleAddLanguage = () => {
    if (newLanguage.trim()) {
      setFormData(prev => ({
        ...prev,
        languages: [...(prev.languages || []), newLanguage.trim()]
      }));
      setNewLanguage('');
    }
  };

  const handleRemoveLanguage = (lang: string) => {
    setFormData(prev => ({
      ...prev,
      languages: prev.languages?.filter(l => l !== lang) || []
    }));
  };

  const handleAddKeyword = () => {
    if (newKeyword.trim()) {
      setFormData(prev => ({
        ...prev,
        keywords: [...(prev.keywords || []), newKeyword.trim()]
      }));
      setNewKeyword('');
    }
  };

  const handleRemoveKeyword = (keyword: string) => {
    setFormData(prev => ({
      ...prev,
      keywords: prev.keywords?.filter(k => k !== keyword) || []
    }));
  };

  const handleSubmit = async () => {
    try {
      await onSubmit(formData);
      // Reset form
      setFormData({
        title: '',
        description: '',
        requirements: '',
        responsibilities: '',
        benefits: '',
        department: '',
        location: '',
        employment_type: '',
        experience_level: '',
        salary_min: undefined,
        salary_max: undefined,
        salary_currency: 'USD',
        priority: 'medium',
        required_skills: [],
        preferred_skills: [],
        certifications: [],
        languages: [],
        seo_title: '',
        seo_description: '',
        keywords: []
      });
    } catch (error) {
      // Error handling is done in parent component
    }
  };

  const isFormValid = formData.title.trim().length > 0;

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Create New Job</Typography>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        <Grid container spacing={3}>
          {/* Basic Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>Basic Information</Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Job Title *"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              required
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Department"
              value={formData.department}
              onChange={(e) => handleInputChange('department', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Location"
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Employment Type</InputLabel>
              <Select
                value={formData.employment_type}
                onChange={handleSelectChange('employment_type')}
                label="Employment Type"
              >
                <MenuItem value="full-time">Full Time</MenuItem>
                <MenuItem value="part-time">Part Time</MenuItem>
                <MenuItem value="contract">Contract</MenuItem>
                <MenuItem value="internship">Internship</MenuItem>
                <MenuItem value="freelance">Freelance</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Experience Level</InputLabel>
              <Select
                value={formData.experience_level}
                onChange={handleSelectChange('experience_level')}
                label="Experience Level"
              >
                <MenuItem value="entry">Entry Level</MenuItem>
                <MenuItem value="mid">Mid Level</MenuItem>
                <MenuItem value="senior">Senior Level</MenuItem>
                <MenuItem value="executive">Executive</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={formData.priority}
                onChange={handleSelectChange('priority')}
                label="Priority"
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="urgent">Urgent</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* Salary Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Salary Information</Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Minimum Salary"
              type="number"
              value={formData.salary_min || ''}
              onChange={(e) => handleInputChange('salary_min', e.target.value ? Number(e.target.value) : undefined)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Maximum Salary"
              type="number"
              value={formData.salary_max || ''}
              onChange={(e) => handleInputChange('salary_max', e.target.value ? Number(e.target.value) : undefined)}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Currency</InputLabel>
              <Select
                value={formData.salary_currency}
                onChange={handleSelectChange('salary_currency')}
                label="Currency"
              >
                <MenuItem value="USD">USD</MenuItem>
                <MenuItem value="EUR">EUR</MenuItem>
                <MenuItem value="GBP">GBP</MenuItem>
                <MenuItem value="CAD">CAD</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* Job Details */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Job Details</Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Requirements"
              value={formData.requirements}
              onChange={(e) => handleInputChange('requirements', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Responsibilities"
              value={formData.responsibilities}
              onChange={(e) => handleInputChange('responsibilities', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Benefits"
              value={formData.benefits}
              onChange={(e) => handleInputChange('benefits', e.target.value)}
            />
          </Grid>
          
          {/* Skills and Requirements */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Skills & Requirements</Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Required Skills"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleAddSkill}>
                      <Add />
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            <Box sx={{ mt: 1 }}>
              {formData.required_skills?.map((skill, index) => (
                <Chip
                  key={index}
                  label={skill}
                  onDelete={() => handleRemoveSkill(skill)}
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Preferred Skills"
              value={newPreferredSkill}
              onChange={(e) => setNewPreferredSkill(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddPreferredSkill()}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleAddPreferredSkill}>
                      <Add />
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            <Box sx={{ mt: 1 }}>
              {formData.preferred_skills?.map((skill, index) => (
                <Chip
                  key={index}
                  label={skill}
                  onDelete={() => handleRemovePreferredSkill(skill)}
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Certifications"
              value={newCertification}
              onChange={(e) => setNewCertification(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddCertification()}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleAddCertification}>
                      <Add />
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            <Box sx={{ mt: 1 }}>
              {formData.certifications?.map((cert, index) => (
                <Chip
                  key={index}
                  label={cert}
                  onDelete={() => handleRemoveCertification(cert)}
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Languages"
              value={newLanguage}
              onChange={(e) => setNewLanguage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddLanguage()}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleAddLanguage}>
                      <Add />
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            <Box sx={{ mt: 1 }}>
              {formData.languages?.map((lang, index) => (
                <Chip
                  key={index}
                  label={lang}
                  onDelete={() => handleRemoveLanguage(lang)}
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </Grid>
          
          {/* SEO Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>SEO Information</Typography>
            <Divider sx={{ mb: 2 }} />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="SEO Title"
              value={formData.seo_title}
              onChange={(e) => handleInputChange('seo_title', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="SEO Description"
              value={formData.seo_description}
              onChange={(e) => handleInputChange('seo_description', e.target.value)}
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Keywords"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleAddKeyword}>
                      <Add />
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            <Box sx={{ mt: 1 }}>
              {formData.keywords?.map((keyword, index) => (
                <Chip
                  key={index}
                  label={keyword}
                  onDelete={() => handleRemoveKeyword(keyword)}
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </Grid>
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!isFormValid || loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Creating...' : 'Create Job'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateJobDialog;

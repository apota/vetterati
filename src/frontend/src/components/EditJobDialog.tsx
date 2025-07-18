import React, { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Button, 
  TextField, 
  CircularProgress, 
  Grid, 
  Chip, 
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  IconButton,
  InputAdornment
} from '@mui/material';
import { Add, Delete } from '@mui/icons-material';
import { JobDetails, JobCreateRequest } from '../types/job';

interface EditJobDialogProps {
  open: boolean;
  job: JobDetails | null;
  loading: boolean;
  error?: string;
  onClose: () => void;
  onSave: (jobId: string, jobData: Partial<JobCreateRequest>) => void;
}

const EditJobDialog: React.FC<EditJobDialogProps> = ({ open, job, loading, error, onClose, onSave }) => {
  const [form, setForm] = useState<Partial<JobCreateRequest>>({});
  
  // Debug logging
  useEffect(() => {
    console.log('EditJobDialog: Props changed', { open, loading, jobId: job?.id });
  }, [open, loading, job]);
  
  // States for managing array fields
  const [newRequiredSkill, setNewRequiredSkill] = useState('');
  const [newPreferredSkill, setNewPreferredSkill] = useState('');
  const [newCertification, setNewCertification] = useState('');
  const [newLanguage, setNewLanguage] = useState('');
  const [newKeyword, setNewKeyword] = useState('');

  useEffect(() => {
    if (job) {
      console.log('EditJobDialog: Job data received', job);
      setForm({
        title: job.title,
        description: job.description,
        requirements: job.requirements,
        responsibilities: job.responsibilities,
        benefits: job.benefits,
        department: job.department,
        location: job.location,
        employment_type: job.employment_type,
        experience_level: job.experience_level,
        salary_min: job.salary_min,
        salary_max: job.salary_max,
        salary_currency: job.salary_currency,
        priority: job.priority,
        required_skills: job.required_skills || [],
        preferred_skills: job.preferred_skills || [],
        certifications: job.certifications || [],
        languages: job.languages || [],
        seo_title: job.seo_title,
        seo_description: job.seo_description,
        keywords: job.keywords || [],
      });
    } else {
      console.log('EditJobDialog: No job data provided');
    }
  }, [job]);

  const handleChange = (field: keyof JobCreateRequest) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [field]: e.target.value });
  };

  const handleSelectChange = (field: keyof JobCreateRequest) => (e: any) => {
    setForm({ ...form, [field]: e.target.value });
  };

  // Required skills management
  const handleAddRequiredSkill = () => {
    if (newRequiredSkill.trim()) {
      setForm(prev => ({
        ...prev,
        required_skills: [...(prev.required_skills || []), newRequiredSkill.trim()]
      }));
      setNewRequiredSkill('');
    }
  };

  const handleRemoveRequiredSkill = (skill: string) => {
    setForm(prev => ({
      ...prev,
      required_skills: prev.required_skills?.filter(s => s !== skill) || []
    }));
  };

  // Preferred skills management
  const handleAddPreferredSkill = () => {
    if (newPreferredSkill.trim()) {
      setForm(prev => ({
        ...prev,
        preferred_skills: [...(prev.preferred_skills || []), newPreferredSkill.trim()]
      }));
      setNewPreferredSkill('');
    }
  };

  const handleRemovePreferredSkill = (skill: string) => {
    setForm(prev => ({
      ...prev,
      preferred_skills: prev.preferred_skills?.filter(s => s !== skill) || []
    }));
  };

  // Certifications management
  const handleAddCertification = () => {
    if (newCertification.trim()) {
      setForm(prev => ({
        ...prev,
        certifications: [...(prev.certifications || []), newCertification.trim()]
      }));
      setNewCertification('');
    }
  };

  const handleRemoveCertification = (cert: string) => {
    setForm(prev => ({
      ...prev,
      certifications: prev.certifications?.filter(c => c !== cert) || []
    }));
  };

  // Languages management
  const handleAddLanguage = () => {
    if (newLanguage.trim()) {
      setForm(prev => ({
        ...prev,
        languages: [...(prev.languages || []), newLanguage.trim()]
      }));
      setNewLanguage('');
    }
  };

  const handleRemoveLanguage = (lang: string) => {
    setForm(prev => ({
      ...prev,
      languages: prev.languages?.filter(l => l !== lang) || []
    }));
  };

  // Keywords management
  const handleAddKeyword = () => {
    if (newKeyword.trim()) {
      setForm(prev => ({
        ...prev,
        keywords: [...(prev.keywords || []), newKeyword.trim()]
      }));
      setNewKeyword('');
    }
  };

  const handleRemoveKeyword = (keyword: string) => {
    setForm(prev => ({
      ...prev,
      keywords: prev.keywords?.filter(k => k !== keyword) || []
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (job && job.id) {
      onSave(job.id, form);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Edit Job</DialogTitle>
      {loading ? (
        <DialogContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
            <Typography variant="body1" sx={{ ml: 2 }}>
              Loading job details...
            </Typography>
          </Box>
        </DialogContent>
      ) : error ? (
        <DialogContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <Typography variant="body1" color="error">
              {error}
            </Typography>
          </Box>
        </DialogContent>
      ) : !job ? (
        <DialogContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <Typography variant="body1">
              Job not found
            </Typography>
          </Box>
        </DialogContent>
      ) : (
        <form onSubmit={handleSubmit}>
          <DialogContent dividers>
          <Grid container spacing={2}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>Basic Information</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField 
                label="Job Title" 
                value={form.title || ''} 
                onChange={handleChange('title')} 
                fullWidth 
                required 
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Department</InputLabel>
                <Select
                  value={form.department || ''}
                  onChange={handleSelectChange('department')}
                  label="Department"
                >
                  <MenuItem value="Engineering">Engineering</MenuItem>
                  <MenuItem value="Product">Product</MenuItem>
                  <MenuItem value="Design">Design</MenuItem>
                  <MenuItem value="Data">Data</MenuItem>
                  <MenuItem value="Marketing">Marketing</MenuItem>
                  <MenuItem value="Sales">Sales</MenuItem>
                  <MenuItem value="Operations">Operations</MenuItem>
                  <MenuItem value="HR">HR</MenuItem>
                  <MenuItem value="Finance">Finance</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField 
                label="Location" 
                value={form.location || ''} 
                onChange={handleChange('location')} 
                fullWidth 
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Employment Type</InputLabel>
                <Select
                  value={form.employment_type || ''}
                  onChange={handleSelectChange('employment_type')}
                  label="Employment Type"
                >
                  <MenuItem value="full-time">Full-time</MenuItem>
                  <MenuItem value="part-time">Part-time</MenuItem>
                  <MenuItem value="contract">Contract</MenuItem>
                  <MenuItem value="internship">Internship</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Experience Level</InputLabel>
                <Select
                  value={form.experience_level || ''}
                  onChange={handleSelectChange('experience_level')}
                  label="Experience Level"
                >
                  <MenuItem value="entry">Entry Level</MenuItem>
                  <MenuItem value="mid">Mid Level</MenuItem>
                  <MenuItem value="senior">Senior Level</MenuItem>
                  <MenuItem value="lead">Lead</MenuItem>
                  <MenuItem value="executive">Executive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={form.priority || ''}
                  onChange={handleSelectChange('priority')}
                  label="Priority"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Salary Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Salary Information</Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField 
                label="Minimum Salary" 
                type="number" 
                value={form.salary_min || ''} 
                onChange={handleChange('salary_min')} 
                fullWidth 
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField 
                label="Maximum Salary" 
                type="number" 
                value={form.salary_max || ''} 
                onChange={handleChange('salary_max')} 
                fullWidth 
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Currency</InputLabel>
                <Select
                  value={form.salary_currency || 'USD'}
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
            </Grid>
            <Grid item xs={12}>
              <TextField 
                label="Job Description" 
                value={form.description || ''} 
                onChange={handleChange('description')} 
                fullWidth 
                multiline 
                minRows={3}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField 
                label="Requirements" 
                value={form.requirements || ''} 
                onChange={handleChange('requirements')} 
                fullWidth 
                multiline 
                minRows={3}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField 
                label="Responsibilities" 
                value={form.responsibilities || ''} 
                onChange={handleChange('responsibilities')} 
                fullWidth 
                multiline 
                minRows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField 
                label="Benefits" 
                value={form.benefits || ''} 
                onChange={handleChange('benefits')} 
                fullWidth 
                multiline 
                minRows={2}
              />
            </Grid>

            {/* Skills Section */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Required Skills</Typography>
              <TextField
                fullWidth
                label="Add Required Skill"
                value={newRequiredSkill}
                onChange={(e) => setNewRequiredSkill(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddRequiredSkill())}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleAddRequiredSkill} edge="end">
                        <Add />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {form.required_skills?.map((skill, index) => (
                  <Chip
                    key={index}
                    label={skill}
                    onDelete={() => handleRemoveRequiredSkill(skill)}
                    color="primary"
                  />
                ))}
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Preferred Skills</Typography>
              <TextField
                fullWidth
                label="Add Preferred Skill"
                value={newPreferredSkill}
                onChange={(e) => setNewPreferredSkill(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddPreferredSkill())}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleAddPreferredSkill} edge="end">
                        <Add />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {form.preferred_skills?.map((skill, index) => (
                  <Chip
                    key={index}
                    label={skill}
                    onDelete={() => handleRemovePreferredSkill(skill)}
                    variant="outlined"
                  />
                ))}
              </Box>
            </Grid>

            {/* Additional Requirements */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Additional Requirements</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Add Certification"
                value={newCertification}
                onChange={(e) => setNewCertification(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCertification())}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleAddCertification} edge="end">
                        <Add />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {form.certifications?.map((cert, index) => (
                  <Chip
                    key={index}
                    label={cert}
                    onDelete={() => handleRemoveCertification(cert)}
                    size="small"
                  />
                ))}
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Add Language"
                value={newLanguage}
                onChange={(e) => setNewLanguage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddLanguage())}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleAddLanguage} edge="end">
                        <Add />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {form.languages?.map((lang, index) => (
                  <Chip
                    key={index}
                    label={lang}
                    onDelete={() => handleRemoveLanguage(lang)}
                    size="small"
                  />
                ))}
              </Box>
            </Grid>

            {/* SEO and Keywords */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>SEO & Keywords</Typography>
            </Grid>
            <Grid item xs={12}>
              <TextField 
                label="SEO Title" 
                value={form.seo_title || ''} 
                onChange={handleChange('seo_title')} 
                fullWidth 
              />
            </Grid>
            <Grid item xs={12}>
              <TextField 
                label="SEO Description" 
                value={form.seo_description || ''} 
                onChange={handleChange('seo_description')} 
                fullWidth 
                multiline 
                minRows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Add Keyword"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddKeyword())}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={handleAddKeyword} edge="end">
                        <Add />
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {form.keywords?.map((keyword, index) => (
                  <Chip
                    key={index}
                    label={keyword}
                    onDelete={() => handleRemoveKeyword(keyword)}
                    size="small"
                    variant="outlined"
                    color="secondary"
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>Cancel</Button>
          <Button type="submit" variant="contained" color="primary" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
        </DialogActions>
        </form>
      )}
    </Dialog>
  );
};

export default EditJobDialog;

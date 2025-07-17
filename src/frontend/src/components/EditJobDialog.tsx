import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, CircularProgress, Grid, Chip, Box } from '@mui/material';
import { JobDetails, JobCreateRequest } from '../types/job';

interface EditJobDialogProps {
  open: boolean;
  job: JobDetails;
  loading: boolean;
  onClose: () => void;
  onSave: (jobId: string, jobData: Partial<JobCreateRequest>) => void;
}

const EditJobDialog: React.FC<EditJobDialogProps> = ({ open, job, loading, onClose, onSave }) => {
  const [form, setForm] = useState<Partial<JobCreateRequest>>({});

  useEffect(() => {
    if (job) {
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
        required_skills: job.required_skills,
        preferred_skills: job.preferred_skills,
        certifications: job.certifications,
        languages: job.languages,
        seo_title: job.seo_title,
        seo_description: job.seo_description,
        keywords: job.keywords,
      });
    }
  }, [job]);

  const handleChange = (field: keyof JobCreateRequest) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [field]: e.target.value });
  };

  const handleArrayChange = (field: keyof JobCreateRequest, value: string[]) => {
    setForm({ ...form, [field]: value });
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
      <form onSubmit={handleSubmit}>
        <DialogContent dividers>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField label="Title" value={form.title || ''} onChange={handleChange('title')} fullWidth required />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Department" value={form.department || ''} onChange={handleChange('department')} fullWidth />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Location" value={form.location || ''} onChange={handleChange('location')} fullWidth />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Employment Type" value={form.employment_type || ''} onChange={handleChange('employment_type')} fullWidth />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Experience Level" value={form.experience_level || ''} onChange={handleChange('experience_level')} fullWidth />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Priority" value={form.priority || ''} onChange={handleChange('priority')} fullWidth />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Salary Min" type="number" value={form.salary_min || ''} onChange={handleChange('salary_min')} fullWidth />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Salary Max" type="number" value={form.salary_max || ''} onChange={handleChange('salary_max')} fullWidth />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Salary Currency" value={form.salary_currency || ''} onChange={handleChange('salary_currency')} fullWidth />
            </Grid>
            <Grid item xs={12}>
              <TextField label="Description" value={form.description || ''} onChange={handleChange('description')} fullWidth multiline minRows={2} />
            </Grid>
            <Grid item xs={12}>
              <TextField label="Requirements" value={form.requirements || ''} onChange={handleChange('requirements')} fullWidth multiline minRows={2} />
            </Grid>
            <Grid item xs={12}>
              <TextField label="Responsibilities" value={form.responsibilities || ''} onChange={handleChange('responsibilities')} fullWidth multiline minRows={2} />
            </Grid>
            <Grid item xs={12}>
              <TextField label="Benefits" value={form.benefits || ''} onChange={handleChange('benefits')} fullWidth multiline minRows={2} />
            </Grid>
            {/* Add more fields as needed, including skills, certifications, etc. */}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>Cancel</Button>
          <Button type="submit" variant="contained" color="primary" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default EditJobDialog;

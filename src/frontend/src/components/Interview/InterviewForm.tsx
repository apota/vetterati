import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Box,
  Typography,
  Autocomplete,
  FormHelperText,
  Alert,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { format } from 'date-fns';
import {
  InterviewType,
  InterviewStatus,
  InterviewCreateRequest,
  InterviewUpdateRequest,
  InterviewDetails,
  InterviewParticipant,
} from '../../types/interview';
import { InterviewService } from '../../services/interviewService';

interface InterviewFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: InterviewCreateRequest | InterviewUpdateRequest) => Promise<void>;
  interview?: InterviewDetails | null;
  isEdit?: boolean;
  loading?: boolean;
  error?: string | null;
}

const interviewTypes: { value: InterviewType; label: string }[] = [
  { value: 'phone', label: 'Phone Interview' },
  { value: 'video', label: 'Video Call' },
  { value: 'onsite', label: 'On-site Interview' },
  { value: 'panel', label: 'Panel Interview' },
  { value: 'technical', label: 'Technical Interview' },
  { value: 'behavioral', label: 'Behavioral Interview' },
];

const interviewStatuses: { value: InterviewStatus; label: string }[] = [
  { value: 'pending', label: 'Pending' },
  { value: 'scheduled', label: 'Scheduled' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

// Mock data for candidates and jobs (replace with actual data from APIs)
const mockCandidates = [
  { id: '1', name: 'Jane Smith', email: 'jane.smith@email.com' },
  { id: '2', name: 'Mike Johnson', email: 'mike.johnson@email.com' },
  { id: '3', name: 'David Brown', email: 'david.brown@email.com' },
  { id: '4', name: 'Sarah Wilson', email: 'sarah.wilson@email.com' },
  { id: '5', name: 'Emily Davis', email: 'emily.davis@email.com' },
];

const mockJobs = [
  { id: '1', title: 'Senior Software Engineer' },
  { id: '2', title: 'Product Manager' },
  { id: '3', title: 'DevOps Engineer' },
  { id: '4', title: 'UX Designer' },
  { id: '5', title: 'Marketing Manager' },
];

const InterviewForm: React.FC<InterviewFormProps> = ({
  open,
  onClose,
  onSubmit,
  interview,
  isEdit = false,
  loading = false,
  error = null,
}) => {
  // Interviewer data state
  const [availableInterviewers, setAvailableInterviewers] = useState<Array<{id: string, name: string, email: string, role: string}>>([]);
  const [interviewersLoading, setInterviewersLoading] = useState(false);
  // Form state
  const [formData, setFormData] = useState<any>({
    title: '',
    description: '',
    interview_type: 'video' as InterviewType,
    round_number: 1,
    candidate_id: '',
    job_id: '',
    workflow_id: '',
    scheduled_start: null,
    scheduled_end: null,
    meeting_url: '',
    meeting_id: '',
    meeting_password: '',
    location: '',
    status: 'pending' as InterviewStatus,
    interviewer_ids: [],
    additional_participants: [],
    notes: '',
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Load interviewers when component mounts or opens
  useEffect(() => {
    const loadInterviewers = async () => {
      if (open) {
        try {
          setInterviewersLoading(true);
          const interviewers = await InterviewService.getInterviewers();
          setAvailableInterviewers(interviewers);
        } catch (error) {
          console.error('Error loading interviewers:', error);
        } finally {
          setInterviewersLoading(false);
        }
      }
    };

    loadInterviewers();
  }, [open]);

  // Initialize form with interview data if editing
  useEffect(() => {
    if (isEdit && interview) {
      // Check if interview has interviewer data from API
      let interviewerIds = interview.interviewer_ids || [];
      
      // If the interview response has additional interviewer data, try to use it
      const interviewAny = interview as any;
      if (interviewAny.interviewers && Array.isArray(interviewAny.interviewers)) {
        interviewerIds = interviewAny.interviewers.map((interviewer: any) => interviewer.id);
      }

      setFormData({
        title: interview.title || '',
        description: interview.description || '',
        interview_type: interview.interview_type,
        round_number: interview.round_number,
        candidate_id: interview.candidate_id || '',
        job_id: interview.job_id || '',
        workflow_id: interview.workflow_id,
        scheduled_start: interview.scheduled_start ? new Date(interview.scheduled_start) : null,
        scheduled_end: interview.scheduled_end ? new Date(interview.scheduled_end) : null,
        meeting_url: interview.meeting_url || '',
        meeting_id: interview.meeting_id || '',
        meeting_password: interview.meeting_password || '',
        location: interview.location || '',
        status: interview.status || 'pending',
        interviewer_ids: interviewerIds,
        additional_participants: interview.additional_participants || [],
        notes: interview.notes || '',
      });
    } else {
      // Reset form for create mode
      setFormData({
        title: '',
        description: '',
        interview_type: 'video' as InterviewType,
        round_number: 1,
        candidate_id: '',
        job_id: '',
        workflow_id: '',
        scheduled_start: null,
        scheduled_end: null,
        meeting_url: '',
        meeting_id: '',
        meeting_password: '',
        location: '',
        status: 'pending' as InterviewStatus,
        interviewer_ids: [],
        additional_participants: [],
        notes: '',
      });
    }
    setFormErrors({});
  }, [isEdit, interview, open]);

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (formErrors[field]) {
      setFormErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.title?.trim()) {
      errors.title = 'Title is required';
    }

    if (!formData.interview_type) {
      errors.interview_type = 'Interview type is required';
    }

    if (!isEdit) {
      if (!formData.candidate_id) {
        errors.candidate_id = 'Candidate is required';
      }
      if (!formData.job_id) {
        errors.job_id = 'Job is required';
      }
      if (!formData.workflow_id) {
        errors.workflow_id = 'Workflow ID is required';
      }
    }

    if (formData.interviewer_ids.length === 0) {
      errors.interviewer_ids = 'At least one interviewer is required';
    }

    if (formData.scheduled_start && formData.scheduled_end) {
      if (formData.scheduled_end <= formData.scheduled_start) {
        errors.scheduled_end = 'End time must be after start time';
      }
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      const submitData: any = {
        title: formData.title,
        description: formData.description,
        interview_type: formData.interview_type,
        round_number: formData.round_number,
        scheduled_start: formData.scheduled_start ? formData.scheduled_start.toISOString() : undefined,
        scheduled_end: formData.scheduled_end ? formData.scheduled_end.toISOString() : undefined,
        meeting_url: formData.meeting_url,
        meeting_id: formData.meeting_id,
        meeting_password: formData.meeting_password,
        location: formData.location,
        status: formData.status,
        interviewer_ids: formData.interviewer_ids,
        additional_participants: formData.additional_participants,
        notes: formData.notes,
      };

      if (!isEdit) {
        // Add fields required for creation
        submitData.workflow_id = formData.workflow_id || `workflow-${formData.candidate_id}-${formData.job_id}`;
        submitData.candidate_id = formData.candidate_id;
        submitData.job_id = formData.job_id;
      }

      await onSubmit(submitData);
      onClose();
    } catch (error) {
      console.error('Error submitting interview form:', error);
    }
  };

  const handleClose = () => {
    setFormErrors({});
    onClose();
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {isEdit ? 'Edit Interview' : 'Create New Interview'}
        </DialogTitle>
        
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3} sx={{ mt: 1 }}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
            </Grid>

            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Interview Title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                error={!!formErrors.title}
                helperText={formErrors.title}
                required
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl fullWidth error={!!formErrors.interview_type}>
                <InputLabel>Interview Type *</InputLabel>
                <Select
                  value={formData.interview_type}
                  label="Interview Type *"
                  onChange={(e) => handleInputChange('interview_type', e.target.value)}
                >
                  {interviewTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
                {formErrors.interview_type && (
                  <FormHelperText>{formErrors.interview_type}</FormHelperText>
                )}
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
              />
            </Grid>

            {/* Candidate and Job Selection (only for create) */}
            {!isEdit && (
              <>
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Candidate and Position
                  </Typography>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Autocomplete
                    options={mockCandidates}
                    getOptionLabel={(option) => `${option.name} (${option.email})`}
                    value={mockCandidates.find((c) => c.id === formData.candidate_id) || null}
                    onChange={(event, newValue) => {
                      handleInputChange('candidate_id', newValue?.id || '');
                    }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Candidate *"
                        error={!!formErrors.candidate_id}
                        helperText={formErrors.candidate_id}
                      />
                    )}
                  />
                </Grid>

                <Grid item xs={12} md={6}>
                  <Autocomplete
                    options={mockJobs}
                    getOptionLabel={(option) => option.title}
                    value={mockJobs.find((j) => j.id === formData.job_id) || null}
                    onChange={(event, newValue) => {
                      handleInputChange('job_id', newValue?.id || '');
                    }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Job Position *"
                        error={!!formErrors.job_id}
                        helperText={formErrors.job_id}
                      />
                    )}
                  />
                </Grid>
              </>
            )}

            {/* Scheduling */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Scheduling
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <DateTimePicker
                label="Start Date & Time"
                value={formData.scheduled_start}
                onChange={(newValue) => handleInputChange('scheduled_start', newValue)}
                slotProps={{
                  textField: {
                    fullWidth: true,
                  },
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <DateTimePicker
                label="End Date & Time"
                value={formData.scheduled_end}
                onChange={(newValue) => handleInputChange('scheduled_end', newValue)}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    error: !!formErrors.scheduled_end,
                    helperText: formErrors.scheduled_end,
                  },
                }}
              />
            </Grid>

            {/* Meeting Details */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Meeting Details
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Meeting URL"
                value={formData.meeting_url}
                onChange={(e) => handleInputChange('meeting_url', e.target.value)}
                placeholder="https://meet.google.com/..."
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Location"
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                placeholder="Conference Room A or Online"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Meeting ID"
                value={formData.meeting_id}
                onChange={(e) => handleInputChange('meeting_id', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Meeting Password"
                type="password"
                value={formData.meeting_password}
                onChange={(e) => handleInputChange('meeting_password', e.target.value)}
              />
            </Grid>

            {/* Interviewers */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Interviewers
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Autocomplete
                multiple
                loading={interviewersLoading}
                options={availableInterviewers}
                getOptionLabel={(option) => `${option.name} (${option.role})`}
                value={availableInterviewers.filter((interviewer) => formData.interviewer_ids.includes(interviewer.id))}
                onChange={(event, newValue) => {
                  handleInputChange('interviewer_ids', newValue.map((v) => v.id));
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Select Interviewers *"
                    error={!!formErrors.interviewer_ids}
                    helperText={formErrors.interviewer_ids || (interviewersLoading ? 'Loading interviewers...' : '')}
                  />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      variant="outlined"
                      label={option.name}
                      {...getTagProps({ index })}
                      key={option.id}
                    />
                  ))
                }
              />
            </Grid>

            {/* Status (only for edit) */}
            {isEdit && (
              <>
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Status & Notes
                  </Typography>
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={formData.status}
                      label="Status"
                      onChange={(e) => handleInputChange('status', e.target.value)}
                    >
                      {interviewStatuses.map((status) => (
                        <MenuItem key={status.value} value={status.value}>
                          {status.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Round Number"
                    type="number"
                    value={formData.round_number}
                    onChange={(e) => handleInputChange('round_number', parseInt(e.target.value))}
                    inputProps={{ min: 1 }}
                  />
                </Grid>
              </>
            )}

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                placeholder="Additional notes or instructions..."
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Saving...' : (isEdit ? 'Update Interview' : 'Create Interview')}
          </Button>
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
};

export default InterviewForm;

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  IconButton,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TablePagination,
  TableSortLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Divider,
  Stack,
  Alert,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  Search,
  FilterList,
  Add,
  Edit,
  Delete,
  Visibility,
  People,
  TrendingUp,
  Schedule,
  CheckCircle,
  Pause,
  Close
} from '@mui/icons-material';
import { JobListItem, JobDetails, JobSearchFilters, JobCreateRequest } from '../types/job';
import { jobService } from '../services/jobService';
import CreateJobDialog from '../components/CreateJobDialog';
import EditJobDialog from '../components/EditJobDialog';

const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<JobListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobDetails | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  
  // Edit dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editLoading, setEditLoading] = useState(false);
  const [editJob, setEditJob] = useState<JobDetails | null>(null);
  const [editError, setEditError] = useState<string | null>(null);
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [perPage, setPerPage] = useState(10);
  const [totalJobs, setTotalJobs] = useState(0);
  
  // Filter state
  const [filters, setFilters] = useState<JobSearchFilters>({
    query: '',
    status: '',
    department: '',
    employment_type: '',
    min_match_percentage: undefined,
    max_match_percentage: undefined,
    sort_by: 'created_at',
    sort_order: 'desc'
  });
  
  // Load jobs data
  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await jobService.getJobs({
        ...filters,
        page: page + 1,
        per_page: perPage
      });
      
      setJobs(response.data);
      setTotalJobs(response.total);
    } catch (err) {
      setError('Failed to load jobs');
      console.error('Error loading jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, [page, perPage, filters]);

  // Handle filter changes
  const handleFilterChange = (field: keyof JobSearchFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
    setPage(0); // Reset to first page when filters change
  };

  // Handle create job
  const handleCreateJob = async (jobData: JobCreateRequest) => {
    try {
      setCreateLoading(true);
      await jobService.createJob(jobData);
      setCreateDialogOpen(false);
      loadJobs(); // Refresh the list
    } catch (err) {
      console.error('Error creating job:', err);
      setError('Failed to create job');
    } finally {
      setCreateLoading(false);
    }
  };

  // Handle sorting
  const handleSortChange = (field: string) => {
    setFilters(prev => ({
      ...prev,
      sort_by: field,
      sort_order: prev.sort_by === field && prev.sort_order === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Handle job selection and edit dialog
  const handleJobClick = async (jobId: string) => {
    console.log('Job row clicked:', jobId);
    // Use the same edit functionality as the edit button
    await handleEditClick(jobId);
  };

  // Status chip styling
  const getStatusChip = (status: string) => {
    const statusConfig = {
      active: { color: 'success' as const, icon: <CheckCircle sx={{ fontSize: 16 }} /> },
      draft: { color: 'warning' as const, icon: <Edit sx={{ fontSize: 16 }} /> },
      paused: { color: 'info' as const, icon: <Pause sx={{ fontSize: 16 }} /> },
      closed: { color: 'error' as const, icon: <Close sx={{ fontSize: 16 }} /> }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    
    return (
      <Chip
        label={status.charAt(0).toUpperCase() + status.slice(1)}
        color={config.color}
        size="small"
        icon={config.icon}
      />
    );
  };

  // Priority chip styling
  const getPriorityChip = (priority: string) => {
    const priorityConfig = {
      high: { color: 'error' as const },
      medium: { color: 'warning' as const },
      low: { color: 'info' as const }
    };
    
    const config = priorityConfig[priority as keyof typeof priorityConfig] || priorityConfig.medium;
    
    return (
      <Chip
        label={priority.charAt(0).toUpperCase() + priority.slice(1)}
        color={config.color}
        size="small"
        variant="outlined"
      />
    );
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Format match percentage
  const formatMatchPercentage = (percentage: number) => {
    return `${percentage.toFixed(1)}%`;
  };

  // Handler for edit icon click
  const handleEditClick = async (jobId: string) => {
    console.log('Edit icon clicked for job ID:', jobId);
    try {
      setEditLoading(true);
      setEditError(null); // Clear any previous errors
      setEditDialogOpen(true); // Open dialog immediately to show loading state
      const jobDetails = await jobService.getJob(jobId);
      console.log('Job details received:', jobDetails);
      setEditJob(jobDetails);
    } catch (err: any) {
      console.error('Error loading job for editing:', err);
      const errorMessage = err.response?.data?.message || err.message || 'Failed to load job for editing';
      setEditError(errorMessage);
      setError(errorMessage); // Also set the global error for toast
    } finally {
      setEditLoading(false);
    }
  };

  // Separate handler for edit button to prevent event propagation issues
  const handleEditButtonClick = (e: React.MouseEvent, jobId: string) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Edit button clicked - preventing default and stopping propagation');
    handleEditClick(jobId);
  };

  // Handler for saving edits
  const handleSaveEdit = async (jobId: string, jobData: Partial<JobCreateRequest>) => {
    try {
      setEditLoading(true);
      console.log('Saving job edits:', { jobId, jobData });
      await jobService.updateJob(jobId, jobData);
      setEditDialogOpen(false);
      setEditJob(null);
      setEditError(null);
      loadJobs(); // Refresh list
    } catch (err: any) {
      console.error('Error saving job edits:', err);
      const errorMessage = err.response?.data?.message || err.message || 'Failed to save job edits';
      setError(errorMessage);
    } finally {
      setEditLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Jobs Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Job
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                placeholder="Search jobs..."
                value={filters.query}
                onChange={(e) => handleFilterChange('query', e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  )
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="paused">Paused</MenuItem>
                  <MenuItem value="closed">Closed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Department</InputLabel>
                <Select
                  value={filters.department}
                  onChange={(e) => handleFilterChange('department', e.target.value)}
                  label="Department"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="Engineering">Engineering</MenuItem>
                  <MenuItem value="Product">Product</MenuItem>
                  <MenuItem value="Design">Design</MenuItem>
                  <MenuItem value="Data">Data</MenuItem>
                  <MenuItem value="Marketing">Marketing</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Employment Type</InputLabel>
                <Select
                  value={filters.employment_type}
                  onChange={(e) => handleFilterChange('employment_type', e.target.value)}
                  label="Employment Type"
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="full-time">Full-time</MenuItem>
                  <MenuItem value="part-time">Part-time</MenuItem>
                  <MenuItem value="contract">Contract</MenuItem>
                  <MenuItem value="internship">Internship</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={1.5}>
              <TextField
                fullWidth
                type="number"
                placeholder="Min Match %"
                value={filters.min_match_percentage || ''}
                onChange={(e) => handleFilterChange('min_match_percentage', e.target.value ? Number(e.target.value) : undefined)}
                inputProps={{ min: 0, max: 100 }}
              />
            </Grid>
            <Grid item xs={12} md={1.5}>
              <TextField
                fullWidth
                type="number"
                placeholder="Max Match %"
                value={filters.max_match_percentage || ''}
                onChange={(e) => handleFilterChange('max_match_percentage', e.target.value ? Number(e.target.value) : undefined)}
                inputProps={{ min: 0, max: 100 }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Jobs Table */}
      <Card>
        <CardContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>
                        <TableSortLabel
                          active={filters.sort_by === 'title'}
                          direction={filters.sort_by === 'title' ? filters.sort_order : 'asc'}
                          onClick={() => handleSortChange('title')}
                        >
                          Job Title
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={filters.sort_by === 'department'}
                          direction={filters.sort_by === 'department' ? filters.sort_order : 'asc'}
                          onClick={() => handleSortChange('department')}
                        >
                          Department
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={filters.sort_by === 'location'}
                          direction={filters.sort_by === 'location' ? filters.sort_order : 'asc'}
                          onClick={() => handleSortChange('location')}
                        >
                          Location
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={filters.sort_by === 'status'}
                          direction={filters.sort_by === 'status' ? filters.sort_order : 'asc'}
                          onClick={() => handleSortChange('status')}
                        >
                          Status
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={filters.sort_by === 'priority'}
                          direction={filters.sort_by === 'priority' ? filters.sort_order : 'asc'}
                          onClick={() => handleSortChange('priority')}
                        >
                          Priority
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={filters.sort_by === 'applications_count'}
                          direction={filters.sort_by === 'applications_count' ? filters.sort_order : 'asc'}
                          onClick={() => handleSortChange('applications_count')}
                        >
                          Applications
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        Avg Match %
                      </TableCell>
                      <TableCell>
                        Highest Match %
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={filters.sort_by === 'created_at'}
                          direction={filters.sort_by === 'created_at' ? filters.sort_order : 'asc'}
                          onClick={() => handleSortChange('created_at')}
                        >
                          Created
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        Views
                      </TableCell>
                      <TableCell>
                        Actions
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {jobs.map((job) => (
                      <TableRow
                        key={job.id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => handleJobClick(job.id)}
                      >
                        <TableCell>
                          <Typography variant="subtitle2" sx={{ fontWeight: 'medium' }}>
                            {job.title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {job.employment_type}
                          </Typography>
                        </TableCell>
                        <TableCell>{job.department}</TableCell>
                        <TableCell>{job.location}</TableCell>
                        <TableCell>{getStatusChip(job.status)}</TableCell>
                        <TableCell>{getPriorityChip(job.priority)}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <People sx={{ fontSize: 16, mr: 0.5 }} />
                            {job.applications_count}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <TrendingUp sx={{ fontSize: 16, mr: 0.5 }} />
                            {job.avg_match_percentage ? formatMatchPercentage(job.avg_match_percentage) : 'N/A'}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <CheckCircle sx={{ fontSize: 16, mr: 0.5, color: 'success.main' }} />
                            {job.highest_match_percentage ? formatMatchPercentage(job.highest_match_percentage) : 'N/A'}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Schedule sx={{ fontSize: 16, mr: 0.5 }} />
                            {formatDate(job.created_at)}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Visibility sx={{ fontSize: 16, mr: 0.5 }} />
                            {job.views_count}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Button 
                            variant="outlined" 
                            size="small" 
                            startIcon={<Edit />}
                            onClick={(e) => handleEditButtonClick(e, job.id)}
                            style={{ marginRight: '8px' }}
                          >
                            Edit
                          </Button>
                          <Tooltip title="Delete">
                            <IconButton size="small" onClick={(e) => { e.stopPropagation(); /* TODO: Implement delete */ }}>
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              <TablePagination
                rowsPerPageOptions={[5, 10, 25, 50]}
                component="div"
                count={totalJobs}
                rowsPerPage={perPage}
                page={page}
                onPageChange={(_, newPage) => setPage(newPage)}
                onRowsPerPageChange={(e) => {
                  setPerPage(parseInt(e.target.value, 10));
                  setPage(0);
                }}
              />
            </>
          )}
        </CardContent>
      </Card>

      {/* Job Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">{selectedJob?.title}</Typography>
            <IconButton onClick={() => setDetailsDialogOpen(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedJob && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>Department</Typography>
                  <Typography variant="body2">{selectedJob.department}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>Location</Typography>
                  <Typography variant="body2">{selectedJob.location}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>Employment Type</Typography>
                  <Typography variant="body2">{selectedJob.employment_type}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>Experience Level</Typography>
                  <Typography variant="body2">{selectedJob.experience_level}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>Status</Typography>
                  {getStatusChip(selectedJob.status)}
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>Priority</Typography>
                  {getPriorityChip(selectedJob.priority)}
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" gutterBottom>Job Description</Typography>
              <Typography variant="body2" sx={{ mb: 2, whiteSpace: 'pre-line' }}>
                {selectedJob.description}
              </Typography>

              <Typography variant="subtitle2" gutterBottom>Requirements</Typography>
              <Typography variant="body2" sx={{ mb: 2, whiteSpace: 'pre-line' }}>
                {selectedJob.requirements}
              </Typography>

              {selectedJob.responsibilities && (
                <>
                  <Typography variant="subtitle2" gutterBottom>Responsibilities</Typography>
                  <Typography variant="body2" sx={{ mb: 2, whiteSpace: 'pre-line' }}>
                    {selectedJob.responsibilities}
                  </Typography>
                </>
              )}

              {selectedJob.benefits && (
                <>
                  <Typography variant="subtitle2" gutterBottom>Benefits</Typography>
                  <Typography variant="body2" sx={{ mb: 2, whiteSpace: 'pre-line' }}>
                    {selectedJob.benefits}
                  </Typography>
                </>
              )}

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" gutterBottom>Application Statistics</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" color="primary">
                        {selectedJob.applications_count}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Applications
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" color="success.main">
                        {selectedJob.stats?.avg_match_percentage ? formatMatchPercentage(selectedJob.stats.avg_match_percentage) : 'N/A'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Avg Match %
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" color="warning.main">
                        {selectedJob.stats?.highest_match_percentage ? formatMatchPercentage(selectedJob.stats.highest_match_percentage) : 'N/A'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Highest Match %
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" color="info.main">
                        {selectedJob.views_count}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Views
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {selectedJob.stats?.applications_by_status && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>Applications by Status</Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    {Object.entries(selectedJob.stats.applications_by_status).map(([status, count]) => (
                      <Chip
                        key={status}
                        label={`${status.charAt(0).toUpperCase() + status.slice(1)}: ${count}`}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                </Box>
              )}

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" gutterBottom>Skills</Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ mb: 1 }}>Required Skills:</Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {selectedJob.required_skills?.map((skill) => (
                    <Chip key={skill} label={skill} size="small" color="primary" />
                  ))}
                </Stack>
              </Box>
              {selectedJob.preferred_skills && selectedJob.preferred_skills.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>Preferred Skills:</Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    {selectedJob.preferred_skills.map((skill) => (
                      <Chip key={skill} label={skill} size="small" variant="outlined" />
                    ))}
                  </Stack>
                </Box>
              )}

              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Created: {formatDate(selectedJob.created_at)}
                {selectedJob.posted_at && ` • Posted: ${formatDate(selectedJob.posted_at)}`}
                {selectedJob.updated_at && ` • Updated: ${formatDate(selectedJob.updated_at)}`}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
          <Button variant="contained" onClick={() => {/* TODO: Implement edit */}}>
            Edit Job
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Job Dialog */}
      <CreateJobDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSubmit={handleCreateJob}
        loading={createLoading}
      />

      {/* Edit Job Dialog */}
      <EditJobDialog
        open={editDialogOpen}
        job={editJob}
        loading={editLoading}
        error={editError || undefined}
        onClose={() => {
          setEditDialogOpen(false);
          setEditJob(null);
          setEditError(null);
        }}
        onSave={handleSaveEdit}
      />
    </Box>
  );
};

export default JobsPage;

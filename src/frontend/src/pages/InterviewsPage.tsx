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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Alert,
  CircularProgress,
  Tooltip,
  Avatar,
  Stack
} from '@mui/material';
import {
  Search,
  Add,
  Edit,
  Delete,
  VideoCall,
  Phone,
  LocationOn,
  Schedule,
  CheckCircle,
  Cancel,
  AccessTime,
  PlayArrow,
  People
} from '@mui/icons-material';
import { 
  InterviewListItem, 
  InterviewStats, 
  InterviewSearchFilters, 
  InterviewType, 
  InterviewStatus,
  InterviewDetails,
  InterviewCreateRequest,
  InterviewUpdateRequest
} from '../types/interview';
import { InterviewService } from '../services/interviewService';
import InterviewForm from '../components/Interview/InterviewForm';

const InterviewsPage: React.FC = () => {
  const [interviews, setInterviews] = useState<InterviewListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Stats state
  const [stats, setStats] = useState<InterviewStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [perPage, setPerPage] = useState(10);
  const [totalInterviews, setTotalInterviews] = useState(0);
  
  // Filter state
  const [filters, setFilters] = useState<InterviewSearchFilters>({
    query: '',
    status: undefined,
    interview_type: undefined,
    sort_by: 'scheduled_start',
    sort_order: 'asc'
  });

  // Form state
  const [formOpen, setFormOpen] = useState(false);
  const [editingInterview, setEditingInterview] = useState<InterviewDetails | null>(null);
  const [isEdit, setIsEdit] = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Load interviews
  const loadInterviews = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await InterviewService.getInterviews({
        page: page + 1,
        limit: perPage,
        status: filters.status,
        interview_type: filters.interview_type,
        search: filters.query || undefined,
        date_from: filters.date_from,
        date_to: filters.date_to,
        sort_by: filters.sort_by,
        sort_order: filters.sort_order
      });
      
      setInterviews(response.items);
      setTotalInterviews(response.total);
    } catch (error) {
      console.error('Error loading interviews:', error);
      setError('Failed to load interviews');
    } finally {
      setLoading(false);
    }
  }, [page, perPage, filters]);

  // Load statistics
  const loadStats = React.useCallback(async () => {
    try {
      setStatsLoading(true);
      const statsData = await InterviewService.getInterviewStats();
      setStats(statsData);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setStatsLoading(false);
    }
  }, []);

  // Effects
  useEffect(() => {
    loadInterviews();
  }, [loadInterviews]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  // Handle filter changes
  const handleFilterChange = (field: keyof InterviewSearchFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
    setPage(0); // Reset to first page when filters change
  };

  // Handle stats panel clicks
  const handleStatsPanelClick = (filterType: string) => {
    let newFilters: Partial<InterviewSearchFilters> = {
      query: '',
      interview_type: undefined,
    };

    switch (filterType) {
      case 'total':
        newFilters.status = undefined;
        break;
      case 'today':
        newFilters.status = 'scheduled';
        newFilters.date_from = new Date().toISOString().split('T')[0];
        newFilters.date_to = new Date().toISOString().split('T')[0];
        break;
      case 'scheduled':
        newFilters.status = 'scheduled';
        break;
      case 'completed':
        newFilters.status = 'completed';
        break;
    }

    setFilters(prev => ({
      ...prev,
      ...newFilters
    }));
    setPage(0);
  };

  // Handle page change
  const handlePageChange = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  // Handle per page change
  const handlePerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Form handlers
  const handleCreateInterview = () => {
    setEditingInterview(null);
    setIsEdit(false);
    setFormError(null);
    setFormOpen(true);
  };

  const handleEditInterview = async (interviewId: string) => {
    try {
      setFormLoading(true);
      
      // Fetch the full interview details from the API
      const interviewDetails = await InterviewService.getInterviewById(interviewId);
      
      // Transform the response to match InterviewDetails interface
      const interviewDetailsForEdit: InterviewDetails = {
        ...interviewDetails,
        // Map API response fields if necessary
        interviewer_ids: interviewDetails.interviewer_ids || [],
        additional_participants: interviewDetails.additional_participants || [],
        interview_questions: interviewDetails.interview_questions || [],
        evaluation_criteria: interviewDetails.evaluation_criteria || [],
        feedback: interviewDetails.feedback || [],
        attachments: interviewDetails.attachments || [],
        // Use existing fields from API response
        workflow_id: interviewDetails.workflow_id,
        created_at: interviewDetails.created_at,
        updated_at: interviewDetails.updated_at,
      };
      
      setEditingInterview(interviewDetailsForEdit);
      setIsEdit(true);
      setFormError(null);
      setFormOpen(true);
    } catch (error) {
      console.error('Error loading interview for edit:', error);
      setFormError('Failed to load interview details');
    } finally {
      setFormLoading(false);
    }
  };

  const handleFormSubmit = async (data: InterviewCreateRequest | InterviewUpdateRequest) => {
    try {
      setFormLoading(true);
      setFormError(null);

      if (isEdit && editingInterview) {
        // Update existing interview
        await InterviewService.updateInterview(editingInterview.id, data as InterviewUpdateRequest);
      } else {
        // Create new interview
        await InterviewService.createInterview(data as InterviewCreateRequest);
      }

      // Refresh the interviews list
      await loadInterviews();
      await loadStats();
      
      setFormOpen(false);
    } catch (error) {
      console.error('Error saving interview:', error);
      setFormError('Failed to save interview');
    } finally {
      setFormLoading(false);
    }
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setEditingInterview(null);
    setIsEdit(false);
    setFormError(null);
  };

  // Get status chip color
  const getStatusChipColor = (status: InterviewStatus) => {
    switch (status) {
      case 'scheduled':
        return 'primary';
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'warning';
      case 'cancelled':
        return 'error';
      case 'pending':
      default:
        return 'default';
    }
  };

  // Get interview type icon
  const getInterviewTypeIcon = (type: InterviewType) => {
    switch (type) {
      case 'video':
        return <VideoCall fontSize="small" />;
      case 'phone':
        return <Phone fontSize="small" />;
      case 'onsite':
        return <LocationOn fontSize="small" />;
      case 'panel':
        return <People fontSize="small" />;
      case 'technical':
        return <VideoCall fontSize="small" color="primary" />;
      case 'behavioral':
        return <VideoCall fontSize="small" color="secondary" />;
      default:
        return <Schedule fontSize="small" />;
    }
  };

  // Format date for display
  const formatDateTime = (dateString?: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Interview Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreateInterview}
        >
          Schedule Interview
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
            onClick={() => handleStatsPanelClick('total')}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary">
                    {statsLoading ? <CircularProgress size={24} /> : stats?.total || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Total Interviews
                  </Typography>
                </Box>
                <Schedule color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
            onClick={() => handleStatsPanelClick('today')}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="warning.main">
                    {statsLoading ? <CircularProgress size={24} /> : stats?.today || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Today
                  </Typography>
                </Box>
                <AccessTime color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
            onClick={() => handleStatsPanelClick('scheduled')}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="info.main">
                    {statsLoading ? <CircularProgress size={24} /> : stats?.scheduled || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Scheduled
                  </Typography>
                </Box>
                <PlayArrow color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
            onClick={() => handleStatsPanelClick('completed')}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="success.main">
                    {statsLoading ? <CircularProgress size={24} /> : stats?.completed || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Completed
                  </Typography>
                </Box>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            {/* Search */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search interviews, candidates, jobs..."
                value={filters.query || ''}
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

            {/* Status Filter */}
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status || ''}
                  label="Status"
                  onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Interview Type Filter */}
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={filters.interview_type || ''}
                  label="Type"
                  onChange={(e) => handleFilterChange('interview_type', e.target.value || undefined)}
                >
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="phone">Phone</MenuItem>
                  <MenuItem value="video">Video</MenuItem>
                  <MenuItem value="onsite">Onsite</MenuItem>
                  <MenuItem value="panel">Panel</MenuItem>
                  <MenuItem value="technical">Technical</MenuItem>
                  <MenuItem value="behavioral">Behavioral</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Date From */}
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                type="date"
                label="From Date"
                value={filters.date_from || ''}
                onChange={(e) => handleFilterChange('date_from', e.target.value || undefined)}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>

            {/* Date To */}
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                type="date"
                label="To Date"
                value={filters.date_to || ''}
                onChange={(e) => handleFilterChange('date_to', e.target.value || undefined)}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Interviews Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Candidate</TableCell>
                <TableCell>Job</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Round</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Scheduled Time</TableCell>
                <TableCell>Interviewers</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : interviews.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    No interviews found
                  </TableCell>
                </TableRow>
              ) : (
                interviews.map((interview) => (
                  <TableRow key={interview.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Avatar sx={{ mr: 2 }}>
                          {interview.candidate_name.charAt(0)}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {interview.candidate_name}
                          </Typography>
                          {interview.title && (
                            <Typography variant="caption" color="textSecondary">
                              {interview.title}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {interview.job_title}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        {getInterviewTypeIcon(interview.interview_type)}
                        <Typography variant="body2" sx={{ ml: 1 }}>
                          {interview.interview_type.charAt(0).toUpperCase() + interview.interview_type.slice(1)}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={`Round ${interview.round_number}`} 
                        size="small" 
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={interview.status.replace('_', ' ').charAt(0).toUpperCase() + interview.status.replace('_', ' ').slice(1)}
                        color={getStatusChipColor(interview.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {formatDateTime(interview.scheduled_start)}
                        </Typography>
                        {interview.location && (
                          <Typography variant="caption" color="textSecondary">
                            📍 {interview.location}
                          </Typography>
                        )}
                        {interview.meeting_url && (
                          <Typography variant="caption" color="textSecondary">
                            🔗 Video Call
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Stack spacing={0.5}>
                        {interview.interviewer_names.map((name, index) => (
                          <Typography key={index} variant="caption" color="textSecondary">
                            {name}
                          </Typography>
                        ))}
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <Box display="flex">
                        <Tooltip title="Edit Interview">
                          <IconButton 
                            size="small"
                            onClick={() => handleEditInterview(interview.id)}
                          >
                            <Edit fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {interview.meeting_url && (
                          <Tooltip title="Join Meeting">
                            <IconButton 
                              size="small" 
                              color="primary"
                              onClick={() => window.open(interview.meeting_url, '_blank')}
                            >
                              <VideoCall fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Cancel Interview">
                          <IconButton size="small" color="error">
                            <Cancel fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={totalInterviews}
          rowsPerPage={perPage}
          page={page}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handlePerPageChange}
        />
      </Card>

      {/* Interview Form Dialog */}
      <InterviewForm
        open={formOpen}
        onClose={handleFormClose}
        onSubmit={handleFormSubmit}
        interview={editingInterview}
        isEdit={isEdit}
        loading={formLoading}
        error={formError}
      />
    </Box>
  );
};

export default InterviewsPage;

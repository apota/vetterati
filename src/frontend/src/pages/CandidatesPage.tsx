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
  TableSortLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Alert,
  CircularProgress,
  Tooltip,
  Avatar
} from '@mui/material';
import {
  Search,
  Add,
  Edit,
  Delete,
  People,
  TrendingUp,
  Schedule,
  CheckCircle,
  Pause,
  Close
} from '@mui/icons-material';
import { CandidateListItem, CandidateDetails, CandidateSearchFilters, CandidateStats } from '../types/candidate';
import { CandidateService } from '../services/candidateService';
import CreateCandidateDialog from '../components/CreateCandidateDialog';
import EditCandidateDialog from '../components/EditCandidateDialog';

const CandidatesPage: React.FC = () => {
  const [candidates, setCandidates] = useState<CandidateListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  
  // Edit dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editLoading, setEditLoading] = useState(false);
  const [editCandidate, setEditCandidate] = useState<CandidateDetails | null>(null);
  const [editError, setEditError] = useState<string | null>(null);
  
  // Delete dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteCandidate, setDeleteCandidate] = useState<CandidateListItem | null>(null);
  const [deleting, setDeleting] = useState(false);
  
  // Stats state
  const [stats, setStats] = useState<CandidateStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [perPage, setPerPage] = useState(10);
  const [totalCandidates, setTotalCandidates] = useState(0);
  
  // Filter state
  const [filters, setFilters] = useState<CandidateSearchFilters>({
    query: '',
    status: '',
    career_level: '',
    source: '',
    min_experience: undefined,
    max_experience: undefined,
    location: '',
    skills: [],
    sort_by: 'created_at',
    sort_order: 'desc'
  });

  const loadCandidates = React.useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await CandidateService.getCandidates({
        page: page + 1,
        limit: perPage,
        status: filters.status || undefined,
        search: filters.query || undefined,
        location: filters.location || undefined,
        career_level: filters.career_level || undefined,
        experience_min: filters.min_experience,
        experience_max: filters.max_experience,
        sort_by: filters.sort_by,
        sort_order: filters.sort_order
      });
      
      setCandidates(response.items);
      setTotalCandidates(response.total);
    } catch (err: any) {
      console.error('Error loading candidates:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load candidates');
    } finally {
      setLoading(false);
    }
  }, [page, perPage, filters.status, filters.query, filters.location, filters.career_level, filters.min_experience, filters.max_experience, filters.sort_by, filters.sort_order]);

  // Load stats
  const loadStats = async () => {
    try {
      setStatsLoading(true);
      const statsData = await CandidateService.getCandidateStats();
      setStats(statsData);
    } catch (err: any) {
      console.error('Error loading stats:', err);
      // Don't show error for stats, just fail silently
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, [loadCandidates]);

  useEffect(() => {
    loadStats();
  }, []);

  // Handle candidate selection and details dialog
  const handleCandidateClick = async (candidateId: string) => {
    console.log('Candidate row clicked:', candidateId);
    // Use the same edit functionality as the edit button
    await handleEditClick(candidateId);
  };

  // Handle edit dialog
  const handleEditClick = async (candidateId: string) => {
    console.log('Edit icon clicked for candidate ID:', candidateId);
    try {
      setEditLoading(true);
      setEditError(null);
      setEditDialogOpen(true);
      const candidateDetails = await CandidateService.getCandidateById(candidateId);
      console.log('Candidate details received:', candidateDetails);
      setEditCandidate(candidateDetails);
    } catch (err: any) {
      console.error('Error loading candidate for editing:', err);
      const errorMessage = err.response?.data?.message || err.message || 'Failed to load candidate for editing';
      setEditError(errorMessage);
      setError(errorMessage);
    } finally {
      setEditLoading(false);
    }
  };

  // Handle delete dialog
  const handleDeleteClick = (candidate: CandidateListItem) => {
    setDeleteCandidate(candidate);
    setDeleteDialogOpen(true);
  };

  // Handle delete confirmation
  const handleDeleteConfirm = async () => {
    if (!deleteCandidate) return;

    setDeleting(true);
    try {
      await CandidateService.deleteCandidate(deleteCandidate.id);
      setDeleteDialogOpen(false);
      setDeleteCandidate(null);
      loadCandidates(); // Refresh the list
    } catch (err: any) {
      console.error('Error deleting candidate:', err);
      setError(err.response?.data?.message || err.message || 'Failed to delete candidate');
    } finally {
      setDeleting(false);
    }
  };

  // Handle pagination
  const handlePageChange = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handlePerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle sorting
  const handleSort = (field: string) => {
    setFilters(prev => ({
      ...prev,
      sort_by: field,
      sort_order: prev.sort_by === field && prev.sort_order === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Handle filter changes
  const handleFilterChange = (field: keyof CandidateSearchFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
    setPage(0); // Reset to first page when filters change
  };

  // Handle stats panel clicks
  const handleStatsPanelClick = (filterType: string) => {
    let newFilters: Partial<CandidateSearchFilters> = {
      query: '',
      career_level: '',
      source: '',
      min_experience: undefined,
      max_experience: undefined,
      location: '',
      skills: [],
    };

    switch (filterType) {
      case 'total':
        // Show all candidates - clear all filters
        newFilters.status = '';
        break;
      case 'active':
        newFilters.status = 'active';
        break;
      case 'hired':
        newFilters.status = 'hired';
        break;
      case 'new_this_week':
        // Show all candidates from this week (no specific status filter needed)
        newFilters.status = '';
        // Note: The backend should handle the "new this week" logic based on created_at
        break;
    }

    setFilters(prev => ({
      ...prev,
      ...newFilters
    }));
    setPage(0); // Reset to first page when filters change
  };

  // Handle candidate creation
  const handleCandidateCreated = (newCandidate: CandidateDetails) => {
    loadCandidates(); // Refresh the list
    loadStats(); // Refresh stats
  };

  // Handle candidate update
  const handleCandidateUpdated = (updatedCandidate: CandidateDetails) => {
    loadCandidates(); // Refresh the list
    loadStats(); // Refresh stats
  };

  // Status chip styling
  const getStatusChip = (status: string) => {
    const statusConfig = {
      active: { color: 'success' as const, icon: <CheckCircle sx={{ fontSize: 16 }} /> },
      hired: { color: 'info' as const, icon: <CheckCircle sx={{ fontSize: 16 }} /> },
      rejected: { color: 'error' as const, icon: <Close sx={{ fontSize: 16 }} /> },
      inactive: { color: 'warning' as const, icon: <Pause sx={{ fontSize: 16 }} /> }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.active;
    
    return (
      <Chip
        label={status.charAt(0).toUpperCase() + status.slice(1)}
        color={config.color}
        size="small"
        icon={config.icon}
      />
    );
  };

  // Career level chip styling
  const getCareerLevelChip = (level: string) => {
    const levelConfig = {
      entry: { color: 'default' as const },
      mid: { color: 'primary' as const },
      senior: { color: 'secondary' as const },
      executive: { color: 'error' as const }
    };
    
    const config = levelConfig[level as keyof typeof levelConfig] || levelConfig.entry;
    
    return (
      <Chip
        label={level.charAt(0).toUpperCase() + level.slice(1)}
        color={config.color}
        size="small"
        variant="outlined"
      />
    );
  };

  // Get candidate initials for avatar
  const getCandidateInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          Candidates Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Add Candidate
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
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
                    Total Candidates
                  </Typography>
                </Box>
                <People color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
            onClick={() => handleStatsPanelClick('active')}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="success.main">
                    {statsLoading ? <CircularProgress size={24} /> : stats?.active || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Active Candidates
                  </Typography>
                </Box>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
            onClick={() => handleStatsPanelClick('hired')}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="info.main">
                    {statsLoading ? <CircularProgress size={24} /> : stats?.hired || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Hired
                  </Typography>
                </Box>
                <TrendingUp color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ cursor: 'pointer', '&:hover': { boxShadow: 4 } }}
            onClick={() => handleStatsPanelClick('new_this_week')}
          >
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="warning.main">
                    {statsLoading ? <CircularProgress size={24} /> : stats?.new_this_week || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    New This Week
                  </Typography>
                </Box>
                <Schedule color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            {/* First row */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search candidates..."
                value={filters.query}
                onChange={(e) => handleFilterChange('query', e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="hired">Hired</MenuItem>
                  <MenuItem value="rejected">Rejected</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Career Level</InputLabel>
                <Select
                  value={filters.career_level}
                  onChange={(e) => handleFilterChange('career_level', e.target.value)}
                  label="Career Level"
                >
                  <MenuItem value="">All Levels</MenuItem>
                  <MenuItem value="entry">Entry Level</MenuItem>
                  <MenuItem value="mid">Mid Level</MenuItem>
                  <MenuItem value="senior">Senior Level</MenuItem>
                  <MenuItem value="executive">Executive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            {/* Second row */}
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Min Experience"
                type="number"
                value={filters.min_experience || ''}
                onChange={(e) => handleFilterChange('min_experience', e.target.value ? parseInt(e.target.value) : undefined)}
                inputProps={{ min: 0 }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Max Experience"
                type="number"
                value={filters.max_experience || ''}
                onChange={(e) => handleFilterChange('max_experience', e.target.value ? parseInt(e.target.value) : undefined)}
                inputProps={{ min: 0 }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Location"
                value={filters.location}
                onChange={(e) => handleFilterChange('location', e.target.value)}
                placeholder="City, State"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Candidates Table */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Candidate</TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={filters.sort_by === 'status'}
                      direction={filters.sort_order}
                      onClick={() => handleSort('status')}
                    >
                      Status
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Career Level</TableCell>
                  <TableCell>Experience</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Applications</TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={filters.sort_by === 'created_at'}
                      direction={filters.sort_order}
                      onClick={() => handleSort('created_at')}
                    >
                      Added
                    </TableSortLabel>
                  </TableCell>
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
                ) : candidates.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Typography variant="body2" color="textSecondary">
                        No candidates found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  candidates.map((candidate) => (
                    <TableRow
                      key={candidate.id}
                      hover
                      onClick={() => handleCandidateClick(candidate.id)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={2}>
                          <Avatar sx={{ width: 40, height: 40 }}>
                            {getCandidateInitials(candidate.first_name, candidate.last_name)}
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle2">
                              {candidate.first_name} {candidate.last_name}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              {candidate.email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        {getStatusChip(candidate.status)}
                      </TableCell>
                      <TableCell>
                        {candidate.career_level ? getCareerLevelChip(candidate.career_level) : '-'}
                      </TableCell>
                      <TableCell>
                        {candidate.total_years_experience ? `${candidate.total_years_experience} years` : '-'}
                      </TableCell>
                      <TableCell>
                        {candidate.location || '-'}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={candidate.applications_count}
                          color="primary"
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="textSecondary">
                          {new Date(candidate.created_at).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={1}>
                          <Tooltip title="Edit">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEditClick(candidate.id);
                              }}
                            >
                              <Edit />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteClick(candidate);
                              }}
                            >
                              <Delete />
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
            count={totalCandidates}
            rowsPerPage={perPage}
            page={page}
            onPageChange={handlePageChange}
            onRowsPerPageChange={handlePerPageChange}
          />
        </CardContent>
      </Card>

      {/* Create Candidate Dialog */}
      <CreateCandidateDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onCreated={handleCandidateCreated}
      />

      {/* Edit Candidate Dialog */}
      <EditCandidateDialog
        open={editDialogOpen}
        candidate={editCandidate}
        loading={editLoading}
        error={editError}
        onClose={() => {
          setEditDialogOpen(false);
          setEditCandidate(null);
          setEditError(null);
        }}
        onSave={handleCandidateUpdated}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete candidate "{deleteCandidate?.first_name} {deleteCandidate?.last_name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={deleting}>
            Cancel
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" disabled={deleting}>
            {deleting ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CandidatesPage;

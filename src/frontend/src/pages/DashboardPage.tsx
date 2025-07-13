import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  IconButton,
  Tooltip,
  Skeleton,
} from '@mui/material';
import {
  TrendingUp,
  People,
  Work,
  Event,
  CalendarToday,
  Refresh,
} from '@mui/icons-material';
import DashboardService, { DashboardStats, RecentApplication, TimeWindow } from '../services/dashboardService';

const DashboardPage: React.FC = () => {
  // Separate loading states for each panel
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentApplications, setRecentApplications] = useState<RecentApplication[]>([]);
  const [statsLoading, setStatsLoading] = useState(true);
  const [applicationsLoading, setApplicationsLoading] = useState(true);
  const [statsError, setStatsError] = useState<string | null>(null);
  const [applicationsError, setApplicationsError] = useState<string | null>(null);
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('day');

  // Fetch dashboard stats independently
  const fetchDashboardStats = useCallback(async (selectedTimeWindow: TimeWindow) => {
    try {
      setStatsLoading(true);
      setStatsError(null);
      
      const dashboardStats = await DashboardService.getDashboardStats(selectedTimeWindow);
      setStats(dashboardStats);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
      setStatsError('Failed to load dashboard statistics. Please try again.');
    } finally {
      setStatsLoading(false);
    }
  }, []);

  // Fetch recent applications independently
  const fetchRecentApplications = useCallback(async () => {
    try {
      setApplicationsLoading(true);
      setApplicationsError(null);
      
      const applications = await DashboardService.getRecentApplications();
      setRecentApplications(applications);
    } catch (err) {
      console.error('Error fetching recent applications:', err);
      setApplicationsError('Failed to load recent applications. Please try again.');
    } finally {
      setApplicationsLoading(false);
    }
  }, []);

  // Initialize both panels independently
  useEffect(() => {
    fetchDashboardStats(timeWindow);
    fetchRecentApplications();
  }, [fetchDashboardStats, fetchRecentApplications, timeWindow]);

  const handleTimeWindowChange = useCallback((event: SelectChangeEvent<TimeWindow>) => {
    const newTimeWindow = event.target.value as TimeWindow;
    setTimeWindow(newTimeWindow);
  }, []);

  const handleRefresh = useCallback(() => {
    DashboardService.clearCache();
    fetchDashboardStats(timeWindow);
    fetchRecentApplications();
  }, [fetchDashboardStats, fetchRecentApplications, timeWindow]);

  const statCards = useMemo(() => {
    if (!stats) return [];
    
    return [
      {
        title: 'Active Jobs',
        value: stats.activeJobs.toString(),
        icon: <Work />,
        color: 'primary',
        change: stats.jobsChange,
      },
      {
        title: 'Total Candidates',
        value: stats.totalCandidates.toLocaleString(),
        icon: <People />,
        color: 'success',
        change: stats.candidatesChange,
      },
      {
        title: 'Interviews Today',
        value: stats.interviewsToday.toString(),
        icon: <Event />,
        color: 'warning',
        change: stats.interviewsChange,
      },
      {
        title: 'Hire Rate',
        value: `${stats.hireRate}%`,
        icon: <TrendingUp />,
        color: 'info',
        change: stats.hireRateChange,
      },
    ];
  }, [stats]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Interview':
        return 'primary';
      case 'Review':
        return 'warning';
      case 'Offer':
        return 'success';
      default:
        return 'default';
    }
  };

  // Skeleton component for stat cards
  const StatCardSkeleton = () => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Skeleton variant="circular" width={24} height={24} sx={{ mr: 1 }} />
          <Skeleton variant="text" width="60%" />
        </Box>
        <Skeleton variant="text" width="40%" height={40} sx={{ mb: 1 }} />
        <Skeleton variant="rectangular" width="50%" height={24} />
      </CardContent>
    </Card>
  );

  // Skeleton component for application rows
  const ApplicationRowSkeleton = () => (
    <TableRow>
      <TableCell><Skeleton variant="text" width="80%" /></TableCell>
      <TableCell><Skeleton variant="text" width="70%" /></TableCell>
      <TableCell><Skeleton variant="rectangular" width={60} height={24} /></TableCell>
      <TableCell><Skeleton variant="text" width="60%" /></TableCell>
    </TableRow>
  );

  return (
    <Box>
      {/* Header - always visible */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Tooltip title="Refresh data">
            <IconButton 
              onClick={handleRefresh} 
              disabled={statsLoading || applicationsLoading}
              color="primary"
            >
              <Refresh />
            </IconButton>
          </Tooltip>
          
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel id="time-window-select-label">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CalendarToday fontSize="small" />
                Compare with
              </Box>
            </InputLabel>
            <Select
              labelId="time-window-select-label"
              value={timeWindow}
              onChange={handleTimeWindowChange}
              label="Compare with"
              disabled={statsLoading}
            >
              {DashboardService.TIME_WINDOW_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  <Box>
                    <Typography variant="body2">{option.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {option.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Comparison period chip - only show when stats are loaded */}
      {stats && !statsLoading && (
        <Box sx={{ mb: 2 }}>
          <Chip
            icon={<CalendarToday />}
            label={`Compared to ${stats.comparisonPeriod}`}
            variant="outlined"
            color="primary"
            size="small"
          />
        </Box>
      )}
      
      {/* Stats Cards Panel */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statsLoading ? (
          // Show skeleton cards while loading
          Array.from({ length: 4 }).map((_, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <StatCardSkeleton />
            </Grid>
          ))
        ) : statsError ? (
          // Show error for stats panel
          <Grid item xs={12}>
            <Alert 
              severity="error" 
              action={
                <IconButton
                  color="inherit"
                  size="small"
                  onClick={() => fetchDashboardStats(timeWindow)}
                >
                  <Refresh />
                </IconButton>
              }
            >
              {statsError}
            </Alert>
          </Grid>
        ) : (
          // Show actual stat cards
          statCards.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ color: `${stat.color}.main`, mr: 1 }}>
                      {stat.icon}
                    </Box>
                    <Typography variant="h6" component="div">
                      {stat.title}
                    </Typography>
                  </Box>
                  <Typography variant="h4" gutterBottom>
                    {stat.value}
                  </Typography>
                  <Chip
                    label={stat.change}
                    size="small"
                    color={stat.color as any}
                    variant="outlined"
                  />
                </CardContent>
              </Card>
            </Grid>
          ))
        )}
      </Grid>

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* Recent Applications Panel */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Recent Applications
                </Typography>
                {applicationsLoading && (
                  <CircularProgress size={20} />
                )}
              </Box>
              
              {applicationsError ? (
                <Alert 
                  severity="error"
                  action={
                    <IconButton
                      color="inherit"
                      size="small"
                      onClick={fetchRecentApplications}
                    >
                      <Refresh />
                    </IconButton>
                  }
                >
                  {applicationsError}
                </Alert>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Candidate</TableCell>
                        <TableCell>Position</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Applied</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {applicationsLoading ? (
                        // Show skeleton rows while loading
                        Array.from({ length: 4 }).map((_, index) => (
                          <ApplicationRowSkeleton key={index} />
                        ))
                      ) : (
                        // Show actual application data
                        recentApplications.map((application) => (
                          <TableRow key={application.id}>
                            <TableCell>
                              <Typography variant="body2" fontWeight="medium">
                                {application.candidate}
                              </Typography>
                            </TableCell>
                            <TableCell>{application.position}</TableCell>
                            <TableCell>
                              <Chip
                                label={application.status}
                                size="small"
                                color={getStatusColor(application.status) as any}
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" color="text.secondary">
                                {application.appliedAt}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions Panel - loads instantly as it's static */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Chip
                  label="Post New Job"
                  clickable
                  color="primary"
                  sx={{ justifyContent: 'flex-start' }}
                />
                <Chip
                  label="Schedule Interview"
                  clickable
                  color="secondary"
                  sx={{ justifyContent: 'flex-start' }}
                />
                <Chip
                  label="View Analytics"
                  clickable
                  color="info"
                  sx={{ justifyContent: 'flex-start' }}
                />
                <Chip
                  label="Export Reports"
                  clickable
                  color="success"
                  sx={{ justifyContent: 'flex-start' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;

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
  ButtonBase,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
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
import CandidateMatchesSection from '../components/CandidateMatchesSection';

const DashboardPage: React.FC = () => {
  // Separate loading states for each panel
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentApplications, setRecentApplications] = useState<RecentApplication[]>([]);
  const [statsLoading, setStatsLoading] = useState(true);
  const [applicationsLoading, setApplicationsLoading] = useState(true);
  const [statsError, setStatsError] = useState<string | null>(null);
  const [applicationsError, setApplicationsError] = useState<string | null>(null);
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('day');

  // Modal state for metric breakdowns
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);
  const [metricBreakdownData, setMetricBreakdownData] = useState<any>(null);
  const [breakdownLoading, setBreakdownLoading] = useState(false);

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

  // Fetch metric breakdown data
  const fetchMetricBreakdown = useCallback(async (metricType: string) => {
    setBreakdownLoading(true);
    try {
      let breakdownData;
      
      switch (metricType) {
        case 'Active Jobs':
          // Simulate API call for job breakdown
          await new Promise(resolve => setTimeout(resolve, 800));
          breakdownData = {
            title: 'Active Jobs Breakdown',
            total: stats?.activeJobs || 0,
            items: [
              { label: 'Software Engineering', count: 8, percentage: 40, color: '#1976d2' },
              { label: 'Product Management', count: 5, percentage: 25, color: '#388e3c' },
              { label: 'Data Science', count: 4, percentage: 20, color: '#f57c00' },
              { label: 'Design', count: 2, percentage: 10, color: '#7b1fa2' },
              { label: 'Marketing', count: 1, percentage: 5, color: '#d32f2f' }
            ]
          };
          break;
          
        case 'Total Candidates':
          await new Promise(resolve => setTimeout(resolve, 800));
          breakdownData = {
            title: 'Candidates by Status',
            total: stats?.totalCandidates || 0,
            items: [
              { label: 'Active Applications', count: 45, percentage: 60, color: '#1976d2' },
              { label: 'In Interview Process', count: 18, percentage: 24, color: '#388e3c' },
              { label: 'Under Review', count: 8, percentage: 11, color: '#f57c00' },
              { label: 'Offers Extended', count: 4, percentage: 5, color: '#7b1fa2' }
            ]
          };
          break;
          
        case 'Interviews Today':
          await new Promise(resolve => setTimeout(resolve, 800));
          breakdownData = {
            title: 'Today\'s Interview Schedule',
            total: stats?.interviewsToday || 0,
            items: [
              { label: 'Technical Interviews', count: 4, percentage: 50, color: '#1976d2' },
              { label: 'Behavioral Interviews', count: 2, percentage: 25, color: '#388e3c' },
              { label: 'Final Round', count: 1, percentage: 12.5, color: '#f57c00' },
              { label: 'Phone Screenings', count: 1, percentage: 12.5, color: '#7b1fa2' }
            ]
          };
          break;
          
        case 'Hire Rate':
          await new Promise(resolve => setTimeout(resolve, 800));
          breakdownData = {
            title: 'Hiring Success by Department',
            total: `${stats?.hireRate || 0}%`,
            items: [
              { label: 'Engineering', count: 85, percentage: 85, isPercentage: true, color: '#1976d2' },
              { label: 'Product', count: 78, percentage: 78, isPercentage: true, color: '#388e3c' },
              { label: 'Design', count: 72, percentage: 72, isPercentage: true, color: '#f57c00' },
              { label: 'Marketing', count: 65, percentage: 65, isPercentage: true, color: '#7b1fa2' }
            ]
          };
          break;
          
        default:
          breakdownData = { title: 'Breakdown', total: 0, items: [] };
      }
      
      setMetricBreakdownData(breakdownData);
    } catch (error) {
      console.error('Error fetching metric breakdown:', error);
    } finally {
      setBreakdownLoading(false);
    }
  }, [stats]);

  // Handle metric card click
  const handleMetricClick = useCallback((metricTitle: string) => {
    setSelectedMetric(metricTitle);
    fetchMetricBreakdown(metricTitle);
  }, [fetchMetricBreakdown]);

  // Close breakdown modal
  const handleCloseBreakdown = useCallback(() => {
    setSelectedMetric(null);
    setMetricBreakdownData(null);
  }, []);

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
              <ButtonBase
                onClick={() => handleMetricClick(stat.title)}
                sx={{
                  width: '100%',
                  textAlign: 'left',
                  borderRadius: 1,
                  '&:hover': {
                    '& .MuiCard-root': {
                      boxShadow: 4,
                      transform: 'translateY(-2px)',
                    }
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                <Card sx={{ 
                  width: '100%',
                  transition: 'all 0.2s ease-in-out',
                  cursor: 'pointer'
                }}>
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
              </ButtonBase>
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

        {/* Candidate Matches Section */}
        <Grid item xs={12}>
          <CandidateMatchesSection 
            maxHeight={600}
            showPagination={true}
            defaultPageSize={10}
            onMatchClick={(match) => {
              // Handle match click - could navigate to candidate or job details
              console.log('Match clicked:', match);
            }}
          />
        </Grid>
      </Grid>

      {/* Metric Breakdown Dialog - shown on metric card click */}
      <Dialog
        open={!!selectedMetric}
        onClose={handleCloseBreakdown}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {breakdownLoading ? (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CircularProgress size={24} sx={{ mr: 1 }} />
              Loading Breakdown...
            </Box>
          ) : (
            selectedMetric
          )}
        </DialogTitle>
        <DialogContent>
          {breakdownLoading ? (
            <LinearProgress />
          ) : (
            metricBreakdownData && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  {metricBreakdownData.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Total: {metricBreakdownData.total}
                </Typography>
                
                {/* Breakdown items list */}
                <List>
                  {metricBreakdownData.items.map((item: any, index: number) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <div
                          style={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            backgroundColor: item.color,
                          }}
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={item.label}
                        secondary={`${item.count} (${item.percentage}%)`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseBreakdown} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DashboardPage;

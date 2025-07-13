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
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentApplications, setRecentApplications] = useState<RecentApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('day');

  const fetchDashboardData = useCallback(async (selectedTimeWindow: TimeWindow) => {
    try {
      setLoading(true);
      setError(null);
      
      const [dashboardStats, applications] = await Promise.all([
        DashboardService.getDashboardStats(selectedTimeWindow),
        DashboardService.getRecentApplications()
      ]);

      setStats(dashboardStats);
      setRecentApplications(applications);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData(timeWindow);
  }, [timeWindow]);

  const handleTimeWindowChange = useCallback((event: SelectChangeEvent<TimeWindow>) => {
    const newTimeWindow = event.target.value as TimeWindow;
    setTimeWindow(newTimeWindow);
  }, []);

  const handleRefresh = useCallback(() => {
    DashboardService.clearCache();
    fetchDashboardData(timeWindow);
  }, [fetchDashboardData, timeWindow]);

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

  if (loading) {
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            Dashboard
          </Typography>
          
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel id="time-window-select-label-loading">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CalendarToday fontSize="small" />
                Compare with
              </Box>
            </InputLabel>
            <Select
              labelId="time-window-select-label-loading"
              value={timeWindow}
              onChange={handleTimeWindowChange}
              label="Compare with"
              disabled={loading}
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
        
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            Dashboard
          </Typography>
          
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel id="time-window-select-label-error">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CalendarToday fontSize="small" />
                Compare with
              </Box>
            </InputLabel>
            <Select
              labelId="time-window-select-label-error"
              value={timeWindow}
              onChange={handleTimeWindowChange}
              label="Compare with"
              disabled={loading}
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
        
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Tooltip title="Refresh data">
            <IconButton 
              onClick={handleRefresh} 
              disabled={loading}
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
              disabled={loading}
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

      {stats && (
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
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statCards.map((stat, index) => (
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
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Applications
              </Typography>
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
                    {recentApplications.map((application) => (
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
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

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

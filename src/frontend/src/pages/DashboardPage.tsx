import React, { useState, useEffect } from 'react';
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
} from '@mui/material';
import {
  TrendingUp,
  People,
  Work,
  Event,
} from '@mui/icons-material';
import DashboardService, { DashboardStats, RecentApplication } from '../services/dashboardService';

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentApplications, setRecentApplications] = useState<RecentApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [dashboardStats, applications] = await Promise.all([
          DashboardService.getDashboardStats(),
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
    };

    fetchDashboardData();
  }, []);

  const statCards = stats ? [
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
  ] : [];

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
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
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

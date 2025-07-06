import React from 'react';
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
} from '@mui/material';
import {
  TrendingUp,
  People,
  Work,
  Event,
} from '@mui/icons-material';

const DashboardPage: React.FC = () => {
  // Mock data - in real app, this would come from API calls
  const stats = [
    {
      title: 'Active Jobs',
      value: '24',
      icon: <Work />,
      color: 'primary',
      change: '+12%',
    },
    {
      title: 'Total Candidates',
      value: '1,247',
      icon: <People />,
      color: 'success',
      change: '+8%',
    },
    {
      title: 'Interviews Today',
      value: '12',
      icon: <Event />,
      color: 'warning',
      change: '+3',
    },
    {
      title: 'Hire Rate',
      value: '23%',
      icon: <TrendingUp />,
      color: 'info',
      change: '+2.5%',
    },
  ];

  const recentApplications = [
    {
      candidate: 'John Doe',
      position: 'Senior Software Engineer',
      status: 'Interview',
      applied: '2 hours ago',
    },
    {
      candidate: 'Jane Smith',
      position: 'Product Manager',
      status: 'Review',
      applied: '5 hours ago',
    },
    {
      candidate: 'Bob Johnson',
      position: 'UX Designer',
      status: 'Offer',
      applied: '1 day ago',
    },
    {
      candidate: 'Alice Brown',
      position: 'Data Scientist',
      status: 'Interview',
      applied: '2 days ago',
    },
  ];

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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
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
                    {recentApplications.map((application, index) => (
                      <TableRow key={index}>
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
                            {application.applied}
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

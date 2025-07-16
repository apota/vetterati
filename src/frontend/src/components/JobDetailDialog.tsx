import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Chip,
  Avatar
} from '@mui/material';
import {
  Work,
  LocationOn,
  AttachMoney,
  AccessTime,
  Group,
  Business,
  Category,
  Description,
  Close,
  CalendarToday,
  TrendingUp
} from '@mui/icons-material';
import { CandidateMatch } from '../services/ahpService';

interface JobDetailDialogProps {
  open: boolean;
  onClose: () => void;
  match: CandidateMatch;
}

const JobDetailDialog: React.FC<JobDetailDialogProps> = ({
  open,
  onClose,
  match
}) => {
  // Sample job data - in real implementation, this would come from job service
  const jobDetails = {
    title: match.jobTitle,
    company: 'TechCorp Inc.',
    location: 'San Francisco, CA',
    type: 'Full-time',
    remote: 'Hybrid',
    salary: '$120,000 - $180,000',
    department: 'Engineering',
    level: 'Senior',
    postedDate: '2025-07-10',
    applicationDeadline: '2025-08-10',
    description: 'We are seeking a talented Senior Software Engineer to join our growing engineering team. You will work on cutting-edge technologies and help build scalable solutions that serve millions of users.',
    requirements: [
      '5+ years of experience in software development',
      'Strong proficiency in React, Node.js, and TypeScript',
      'Experience with cloud platforms (AWS, Azure, or GCP)',
      'Familiarity with microservices architecture',
      'Bachelor\'s degree in Computer Science or related field',
      'Excellent problem-solving and communication skills'
    ],
    responsibilities: [
      'Design and develop scalable web applications',
      'Collaborate with cross-functional teams to deliver features',
      'Write clean, maintainable, and well-tested code',
      'Participate in code reviews and technical discussions',
      'Mentor junior developers and contribute to team growth',
      'Stay up-to-date with emerging technologies and best practices'
    ],
    benefits: [
      'Competitive salary and equity package',
      'Comprehensive health, dental, and vision insurance',
      'Flexible work arrangements',
      'Professional development budget',
      'Unlimited PTO policy',
      'Stock options and 401(k) matching'
    ],
    skills: ['React', 'Node.js', 'TypeScript', 'AWS', 'Docker', 'GraphQL', 'PostgreSQL'],
    teamSize: 12,
    reportingTo: 'Engineering Manager',
    applicants: 45,
    status: 'Active'
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { minHeight: '80vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'secondary.main', width: 56, height: 56 }}>
              <Work />
            </Avatar>
            <Box>
              <Typography variant="h6">{jobDetails.title}</Typography>
              <Typography variant="body2" color="text.secondary">
                {jobDetails.company} • {jobDetails.location}
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Grid container spacing={3}>
          {/* Job Overview */}
          <Grid item xs={12} md={8}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Job Overview
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Business fontSize="small" color="action" />
                      <Typography variant="body2">
                        <strong>Company:</strong> {jobDetails.company}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <LocationOn fontSize="small" color="action" />
                      <Typography variant="body2">
                        <strong>Location:</strong> {jobDetails.location}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <AccessTime fontSize="small" color="action" />
                      <Typography variant="body2">
                        <strong>Type:</strong> {jobDetails.type} ({jobDetails.remote})
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <AttachMoney fontSize="small" color="action" />
                      <Typography variant="body2">
                        <strong>Salary:</strong> {jobDetails.salary}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Category fontSize="small" color="action" />
                      <Typography variant="body2">
                        <strong>Department:</strong> {jobDetails.department}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <TrendingUp fontSize="small" color="action" />
                      <Typography variant="body2">
                        <strong>Level:</strong> {jobDetails.level}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Job Stats */}
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Job Statistics
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">Match %:</Typography>
                    <Chip
                      label={`${match.matchPercentage}%`}
                      color={match.overallScore >= 0.8 ? 'success' : match.overallScore >= 0.6 ? 'warning' : 'error'}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">Applicants:</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {jobDetails.applicants}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">Team Size:</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {jobDetails.teamSize}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">Status:</Typography>
                    <Chip
                      label={jobDetails.status}
                      color="success"
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Job Description */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Job Description
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {jobDetails.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Requirements */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Requirements
                </Typography>
                <List dense>
                  {jobDetails.requirements.map((req, index) => (
                    <ListItem key={index} sx={{ pl: 0 }}>
                      <ListItemText
                        primary={req}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Responsibilities */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Responsibilities
                </Typography>
                <List dense>
                  {jobDetails.responsibilities.map((resp, index) => (
                    <ListItem key={index} sx={{ pl: 0 }}>
                      <ListItemText
                        primary={resp}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Required Skills */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Required Skills
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {jobDetails.skills.map((skill, index) => (
                    <Chip
                      key={index}
                      label={skill}
                      size="small"
                      variant="outlined"
                      color="primary"
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Benefits */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Benefits & Perks
                </Typography>
                <List dense>
                  {jobDetails.benefits.map((benefit, index) => (
                    <ListItem key={index} sx={{ pl: 0 }}>
                      <ListItemText
                        primary={benefit}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Timeline */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Timeline
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CalendarToday fontSize="small" color="action" />
                      <Typography variant="body2">
                        <strong>Posted:</strong> {new Date(jobDetails.postedDate).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CalendarToday fontSize="small" color="action" />
                      <Typography variant="body2">
                        <strong>Application Deadline:</strong> {new Date(jobDetails.applicationDeadline).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button
          variant="contained"
          startIcon={<Description />}
          onClick={() => {
            // In real implementation, this would open full job posting
            console.log('View full job posting for:', match.jobProfileId);
          }}
        >
          View Full Posting
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default JobDetailDialog;

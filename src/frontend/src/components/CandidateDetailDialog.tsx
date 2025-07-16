import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Avatar,
  Chip,
  Card,
  CardContent,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Person,
  Email,
  Phone,
  LocationOn,
  Work,
  School,
  Language,
  Star,
  Close,
  LinkedIn,
  GitHub,
  Description
} from '@mui/icons-material';
import { CandidateMatch } from '../services/ahpService';

interface CandidateDetailDialogProps {
  open: boolean;
  onClose: () => void;
  match: CandidateMatch;
}

const CandidateDetailDialog: React.FC<CandidateDetailDialogProps> = ({
  open,
  onClose,
  match
}) => {
  // Mock candidate data - in real implementation, this would come from candidate service
  const candidateDetails = {
    name: match.candidateName,
    email: 'candidate@example.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    avatar: null,
    summary: 'Experienced software engineer with 8+ years in full-stack development, specializing in React, Node.js, and cloud technologies.',
    experience: [
      {
        title: 'Senior Software Engineer',
        company: 'Tech Corp',
        duration: '2021 - Present',
        description: 'Lead development of customer-facing web applications'
      },
      {
        title: 'Software Engineer',
        company: 'StartupXYZ',
        duration: '2019 - 2021',
        description: 'Built scalable backend services and APIs'
      }
    ],
    education: [
      {
        degree: 'Bachelor of Science in Computer Science',
        school: 'University of California, Berkeley',
        year: '2019'
      }
    ],
    skills: ['React', 'Node.js', 'TypeScript', 'Python', 'AWS', 'Docker', 'GraphQL'],
    languages: ['English (Native)', 'Spanish (Conversational)'],
    links: {
      linkedin: 'https://linkedin.com/in/candidate',
      github: 'https://github.com/candidate',
      portfolio: 'https://candidate-portfolio.com'
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
              <Person />
            </Avatar>
            <Box>
              <Typography variant="h6">{candidateDetails.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                Candidate ID: {match.candidateId.substring(0, 8)}...
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
          {/* Contact Information */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Contact Information
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><Email /></ListItemIcon>
                    <ListItemText primary={candidateDetails.email} />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Phone /></ListItemIcon>
                    <ListItemText primary={candidateDetails.phone} />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><LocationOn /></ListItemIcon>
                    <ListItemText primary={candidateDetails.location} />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Match Information */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Match Information
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">Overall Score:</Typography>
                    <Chip
                      label={`${match.matchPercentage}%`}
                      color={match.overallScore >= 0.8 ? 'success' : match.overallScore >= 0.6 ? 'warning' : 'error'}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">Confidence:</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {match.overallScore >= 0.8 ? 'HIGH' : match.overallScore >= 0.6 ? 'MEDIUM' : 'LOW'}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">Calculated:</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(match.calculatedAt).toLocaleDateString()}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Summary */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Professional Summary
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {candidateDetails.summary}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Experience */}
          <Grid item xs={12} md={8}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Experience
                </Typography>
                {candidateDetails.experience.map((exp, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Work fontSize="small" color="action" />
                      <Typography variant="subtitle2">{exp.title}</Typography>
                    </Box>
                    <Typography variant="body2" color="primary" gutterBottom>
                      {exp.company} • {exp.duration}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {exp.description}
                    </Typography>
                    {index < candidateDetails.experience.length - 1 && <Divider sx={{ mt: 2 }} />}
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Skills & Education */}
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {/* Skills */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Skills
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {candidateDetails.skills.map((skill, index) => (
                      <Chip
                        key={index}
                        label={skill}
                        size="small"
                        variant="outlined"
                        icon={<Star />}
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>

              {/* Education */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Education
                  </Typography>
                  {candidateDetails.education.map((edu, index) => (
                    <Box key={index} sx={{ mb: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <School fontSize="small" color="action" />
                        <Typography variant="subtitle2">{edu.degree}</Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {edu.school} • {edu.year}
                      </Typography>
                    </Box>
                  ))}
                </CardContent>
              </Card>

              {/* Languages */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Languages
                  </Typography>
                  {candidateDetails.languages.map((lang, index) => (
                    <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Language fontSize="small" color="action" />
                      <Typography variant="body2">{lang}</Typography>
                    </Box>
                  ))}
                </CardContent>
              </Card>
            </Box>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button
          variant="contained"
          startIcon={<Description />}
          onClick={() => {
            // In real implementation, this would download or view resume
            console.log('View resume for candidate:', match.candidateId);
          }}
        >
          View Resume
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CandidateDetailDialog;

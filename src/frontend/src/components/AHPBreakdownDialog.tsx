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
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import {
  Analytics,
  Close,
  ExpandMore,
  TrendingUp,
  Assessment,
  Timeline,
  Speed,
  Balance,
  Star,
  CheckCircle,
  Warning,
  Info
} from '@mui/icons-material';
import { CandidateMatch } from '../services/ahpService';

interface AHPBreakdownDialogProps {
  open: boolean;
  onClose: () => void;
  match: CandidateMatch;
}

const AHPBreakdownDialog: React.FC<AHPBreakdownDialogProps> = ({
  open,
  onClose,
  match
}) => {
  // Mock AHP breakdown data - in real implementation, this would come from the AHP service
  const ahpBreakdown = {
    overallScore: match.overallScore,
    matchPercentage: match.matchPercentage,
    methodology: 'Analytic Hierarchy Process (AHP)',
    calculatedAt: match.calculatedAt,
    
    // Criteria weights (importance of each factor)
    criteriaWeights: {
      technicalSkills: 0.35,
      experience: 0.25,
      education: 0.15,
      communication: 0.10,
      culturalFit: 0.10,
      leadership: 0.05
    },
    
    // Candidate scores for each criterion
    candidateScores: {
      technicalSkills: 0.85,
      experience: 0.78,
      education: 0.92,
      communication: 0.74,
      culturalFit: 0.68,
      leadership: 0.45
    },
    
    // Detailed breakdown of technical skills
    technicalBreakdown: {
      programming: { score: 0.90, weight: 0.4 },
      systemDesign: { score: 0.85, weight: 0.3 },
      databases: { score: 0.80, weight: 0.2 },
      devOps: { score: 0.75, weight: 0.1 }
    },
    
    // Experience breakdown
    experienceBreakdown: {
      yearsOfExperience: { score: 0.80, weight: 0.4 },
      relevantExperience: { score: 0.85, weight: 0.4 },
      industryExperience: { score: 0.70, weight: 0.2 }
    },
    
    // Confidence metrics
    confidenceMetrics: {
      dataQuality: 0.88,
      consistency: 0.92,
      completeness: 0.85,
      reliability: 0.90
    },
    
    // Comparison with other candidates
    benchmarks: {
      percentile: 78,
      averageScore: 0.65,
      topScore: 0.95,
      candidateRank: 3,
      totalCandidates: 45
    }
  };

  const getCriteriaLabel = (key: string) => {
    const labels: { [key: string]: string } = {
      technicalSkills: 'Technical Skills',
      experience: 'Experience',
      education: 'Education',
      communication: 'Communication',
      culturalFit: 'Cultural Fit',
      leadership: 'Leadership'
    };
    return labels[key] || key;
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  const getConfidenceIcon = (score: number) => {
    if (score >= 0.9) return <CheckCircle color="success" />;
    if (score >= 0.7) return <Info color="info" />;
    return <Warning color="warning" />;
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
            <Avatar sx={{ bgcolor: 'info.main', width: 56, height: 56 }}>
              <Analytics />
            </Avatar>
            <Box>
              <Typography variant="h6">AHP Score Breakdown</Typography>
              <Typography variant="body2" color="text.secondary">
                {match.candidateName} • {match.jobTitle}
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
          {/* Overall Score Summary */}
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Overall Score
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Typography variant="h3" color="primary">
                    {match.matchPercentage}%
                  </Typography>
                  <Chip
                    label={match.overallScore >= 0.8 ? 'HIGH' : match.overallScore >= 0.6 ? 'MEDIUM' : 'LOW'}
                    color={getScoreColor(match.overallScore)}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Calculated using {ahpBreakdown.methodology}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Last updated: {new Date(ahpBreakdown.calculatedAt).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Benchmarks */}
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Benchmarks
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Percentile:</Typography>
                    <Typography variant="body2" color="primary">
                      {ahpBreakdown.benchmarks.percentile}th
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Rank:</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {ahpBreakdown.benchmarks.candidateRank} of {ahpBreakdown.benchmarks.totalCandidates}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Average Score:</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Math.round(ahpBreakdown.benchmarks.averageScore * 100)}%
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Top Score:</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Math.round(ahpBreakdown.benchmarks.topScore * 100)}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Confidence Metrics */}
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Confidence Metrics
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {Object.entries(ahpBreakdown.confidenceMetrics).map(([key, value]) => (
                    <Box key={key} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getConfidenceIcon(value)}
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {key.replace(/([A-Z])/g, ' $1').trim()}:
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {Math.round(value * 100)}%
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Criteria Breakdown */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Criteria Breakdown
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Criteria</TableCell>
                        <TableCell align="center">Weight</TableCell>
                        <TableCell align="center">Score</TableCell>
                        <TableCell align="center">Weighted Score</TableCell>
                        <TableCell align="center">Progress</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(ahpBreakdown.criteriaWeights).map(([key, weight]) => {
                        const score = ahpBreakdown.candidateScores[key as keyof typeof ahpBreakdown.candidateScores];
                        const weightedScore = weight * score;
                        return (
                          <TableRow key={key}>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Star fontSize="small" color="action" />
                                {getCriteriaLabel(key)}
                              </Box>
                            </TableCell>
                            <TableCell align="center">
                              <Chip
                                label={`${Math.round(weight * 100)}%`}
                                size="small"
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell align="center">
                              <Chip
                                label={`${Math.round(score * 100)}%`}
                                color={getScoreColor(score)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell align="center">
                              <Typography variant="body2" color="text.secondary">
                                {weightedScore.toFixed(3)}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Box sx={{ width: 100 }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={score * 100}
                                  color={getScoreColor(score)}
                                />
                              </Box>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Detailed Breakdowns */}
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Technical Skills Breakdown
                </Typography>
                {Object.entries(ahpBreakdown.technicalBreakdown).map(([key, data]) => (
                  <Box key={key} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {Math.round(data.score * 100)}% (Weight: {Math.round(data.weight * 100)}%)
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={data.score * 100}
                      color={getScoreColor(data.score)}
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Experience Breakdown
                </Typography>
                {Object.entries(ahpBreakdown.experienceBreakdown).map(([key, data]) => (
                  <Box key={key} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {Math.round(data.score * 100)}% (Weight: {Math.round(data.weight * 100)}%)
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={data.score * 100}
                      color={getScoreColor(data.score)}
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Methodology Information */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="h6">AHP Methodology</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary" paragraph>
                  The Analytic Hierarchy Process (AHP) is a structured technique for organizing and analyzing complex decisions. 
                  It provides a comprehensive framework for setting priorities and making the best decision when both qualitative 
                  and quantitative factors need to be considered.
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  <strong>How it works:</strong>
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="1. Criteria are weighted based on their relative importance to the job role"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="2. Candidates are scored on each criterion using objective and subjective measures"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="3. Weighted scores are calculated and summed to produce an overall match score"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="4. Consistency checks ensure the reliability of the scoring process"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                </List>
              </AccordionDetails>
            </Accordion>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button
          variant="contained"
          startIcon={<Assessment />}
          onClick={() => {
            // In real implementation, this would export detailed report
            console.log('Export AHP report for:', match.id);
          }}
        >
          Export Report
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AHPBreakdownDialog;

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
  Pagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  LinearProgress,
  Avatar,
  TableSortLabel,
  Skeleton,
  ButtonBase
} from '@mui/material';
import {
  Refresh,
  TrendingUp,
  Person,
  Work,
  FilterList,
  Sort
} from '@mui/icons-material';
import AhpService, { CandidateMatch, GetCandidateMatchesOptions, PaginatedCandidateMatches } from '../services/ahpService';
import CandidateDetailDialog from './CandidateDetailDialog';
import JobDetailDialog from './JobDetailDialog';
import AHPBreakdownDialog from './AHPBreakdownDialog';

interface CandidateMatchesSectionProps {
  maxHeight?: number;
  showPagination?: boolean;
  defaultPageSize?: number;
  onMatchClick?: (match: CandidateMatch) => void;
}

const CandidateMatchesSection: React.FC<CandidateMatchesSectionProps> = ({
  maxHeight = 500,
  showPagination = true,
  defaultPageSize = 10,
  onMatchClick
}) => {
  const [matches, setMatches] = useState<PaginatedCandidateMatches | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Dialog states
  const [candidateDialogOpen, setCandidateDialogOpen] = useState(false);
  const [jobDialogOpen, setJobDialogOpen] = useState(false);
  const [ahpDialogOpen, setAhpDialogOpen] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState<CandidateMatch | null>(null);
  
  // Pagination and sorting state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(defaultPageSize);
  const [sortBy, setSortBy] = useState<GetCandidateMatchesOptions['sortBy']>('score');
  const [sortOrder, setSortOrder] = useState<GetCandidateMatchesOptions['sortOrder']>('desc');

  // Fetch candidate matches
  const fetchMatches = useCallback(async (options: GetCandidateMatchesOptions = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const fetchOptions: GetCandidateMatchesOptions = {
        page: currentPage,
        pageSize,
        sortBy,
        sortOrder,
        ...options
      };
      
      const result = await AhpService.getAllCandidateMatches(fetchOptions);
      setMatches(result);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch candidate matches');
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, sortBy, sortOrder]);

  // Initial load
  useEffect(() => {
    fetchMatches();
  }, [fetchMatches]);

  // Handle page change
  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setCurrentPage(value);
  };

  // Handle page size change
  const handlePageSizeChange = (event: any) => {
    setPageSize(event.target.value);
    setCurrentPage(1);
  };

  // Handle sort change
  const handleSortChange = (field: GetCandidateMatchesOptions['sortBy']) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

  // Handle refresh
  const handleRefresh = () => {
    fetchMatches();
  };

  // Handle match click
  const handleMatchClick = (match: CandidateMatch) => {
    if (onMatchClick) {
      onMatchClick(match);
    }
  };

  // Handle candidate column click
  const handleCandidateClick = (event: React.MouseEvent, match: CandidateMatch) => {
    event.stopPropagation();
    setSelectedMatch(match);
    setCandidateDialogOpen(true);
  };

  // Handle job column click
  const handleJobClick = (event: React.MouseEvent, match: CandidateMatch) => {
    event.stopPropagation();
    setSelectedMatch(match);
    setJobDialogOpen(true);
  };

  // Handle match score/confidence column click
  const handleScoreClick = (event: React.MouseEvent, match: CandidateMatch) => {
    event.stopPropagation();
    setSelectedMatch(match);
    setAhpDialogOpen(true);
  };

  // Get match confidence color
  const getMatchColor = (score: number): 'success' | 'warning' | 'error' => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  // Format date
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Skeleton component for loading state
  const MatchRowSkeleton = () => (
    <TableRow>
      <TableCell>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Skeleton variant="circular" width={40} height={40} />
          <Skeleton variant="text" width="60%" />
        </Box>
      </TableCell>
      <TableCell><Skeleton variant="text" width="80%" /></TableCell>
      <TableCell><Skeleton variant="rectangular" width={80} height={32} /></TableCell>
      <TableCell><Skeleton variant="rectangular" width={60} height={24} /></TableCell>
      <TableCell><Skeleton variant="text" width="70%" /></TableCell>
    </TableRow>
  );

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Top Candidate Matches
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {matches?.summary && (
              <Tooltip title={`${matches.summary.totalMatches} total matches`}>
                <Chip
                  icon={<TrendingUp />}
                  label={`${matches.summary.totalMatches} matches`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Tooltip>
            )}
            
            <Tooltip title="Refresh matches">
              <IconButton
                onClick={handleRefresh}
                disabled={loading}
                color="primary"
                size="small"
              >
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Controls */}
        <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Page Size</InputLabel>
            <Select
              value={pageSize}
              onChange={handlePageSizeChange}
              label="Page Size"
              disabled={loading}
            >
              <MenuItem value={5}>5</MenuItem>
              <MenuItem value={10}>10</MenuItem>
              <MenuItem value={20}>20</MenuItem>
              <MenuItem value={50}>50</MenuItem>
            </Select>
          </FormControl>

          <Typography variant="body2" color="text.secondary">
            {matches && `${matches.totalCount} total matches`}
          </Typography>
        </Box>

        {error ? (
          <Alert
            severity="error"
            action={
              <IconButton
                color="inherit"
                size="small"
                onClick={handleRefresh}
              >
                <Refresh />
              </IconButton>
            }
          >
            {error}
          </Alert>
        ) : (
          <Box sx={{ position: 'relative' }}>
            {loading && (
              <LinearProgress sx={{ position: 'absolute', top: 0, left: 0, right: 0, zIndex: 1 }} />
            )}
            
            <TableContainer 
              component={Paper} 
              variant="outlined"
              sx={{ 
                maxHeight: `${maxHeight}px`,
                '& .MuiTableHead-root': {
                  position: 'sticky',
                  top: 0,
                  zIndex: 2
                }
              }}
            >
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell align="left" sx={{ padding: '8px 16px' }}>
                      <Tooltip title="Click to view candidate details">
                        <TableSortLabel
                          active={sortBy === 'candidateName'}
                          direction={sortBy === 'candidateName' ? sortOrder : 'asc'}
                          onClick={() => handleSortChange('candidateName')}
                        >
                          Candidate
                        </TableSortLabel>
                      </Tooltip>
                    </TableCell>
                    <TableCell align="left" sx={{ padding: '8px 16px' }}>
                      <Tooltip title="Click to view job details">
                        <TableSortLabel
                          active={sortBy === 'jobTitle'}
                          direction={sortBy === 'jobTitle' ? sortOrder : 'asc'}
                          onClick={() => handleSortChange('jobTitle')}
                        >
                          Position
                        </TableSortLabel>
                      </Tooltip>
                    </TableCell>
                    <TableCell align="left">
                      <Tooltip title="Click to view AHP breakdown">
                        <TableSortLabel
                          active={sortBy === 'score'}
                          direction={sortBy === 'score' ? sortOrder : 'asc'}
                          onClick={() => handleSortChange('score')}
                        >
                          Match %
                        </TableSortLabel>
                      </Tooltip>
                    </TableCell>
                    <TableCell align="left">
                      <Tooltip title="Click to view AHP breakdown">
                        <Typography variant="body2" fontWeight="medium">
                          Confidence
                        </Typography>
                      </Tooltip>
                    </TableCell>
                    <TableCell align="left">
                      <TableSortLabel
                        active={sortBy === 'calculatedAt'}
                        direction={sortBy === 'calculatedAt' ? sortOrder : 'asc'}
                        onClick={() => handleSortChange('calculatedAt')}
                      >
                        Calculated
                      </TableSortLabel>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    Array.from({ length: pageSize }).map((_, index) => (
                      <MatchRowSkeleton key={index} />
                    ))
                  ) : matches?.matches.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        <Typography variant="body2" color="text.secondary">
                          No candidate matches found
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    matches?.matches.map((match) => (
                      <TableRow key={match.id} hover onClick={() => handleMatchClick(match)} sx={{ cursor: 'pointer' }}>
                        <TableCell align="left" sx={{ padding: '8px 16px' }}>
                          <ButtonBase
                            onClick={(e) => handleCandidateClick(e, match)}
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'flex-start',
                              gap: 1,
                              textAlign: 'left',
                              width: '100%',
                              borderRadius: 1,
                              p: 0.5,
                              '&:hover': {
                                backgroundColor: 'action.hover',
                              }
                            }}
                          >
                            <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                              <Person sx={{ fontSize: 18 }} />
                            </Avatar>
                            <Typography variant="subtitle2" fontWeight="bold" sx={{ textAlign: 'left', flex: 1 }}>
                              {match.candidateName}
                            </Typography>
                          </ButtonBase>
                        </TableCell>
                        <TableCell align="left" sx={{ padding: '8px 16px' }}>
                          <Typography variant="subtitle2" fontWeight="bold" sx={{ textAlign: 'left' }}>
                            {match.jobTitle}
                          </Typography>
                        </TableCell>
                        <TableCell align="left">
                          <Box sx={{ minWidth: 80, textAlign: 'left' }}>
                            <Typography variant="subtitle2" fontWeight="bold" sx={{ textAlign: 'left' }}>
                              {match.matchPercentage}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="left">
                          <Box sx={{ minWidth: 60, textAlign: 'left' }}>
                            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'left' }}>
                              {match.overallScore}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="left">
                          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'left' }}>
                            {formatDate(match.calculatedAt)}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Pagination */}
            {showPagination && matches && matches.totalPages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <Pagination
                  count={matches.totalPages}
                  page={currentPage}
                  onChange={handlePageChange}
                  disabled={loading}
                  color="primary"
                  showFirstButton
                  showLastButton
                />
              </Box>
            )}
          </Box>
        )}
      </CardContent>

      {/* Detail Dialogs */}
      {selectedMatch && (
        <>
          <CandidateDetailDialog
            open={candidateDialogOpen}
            onClose={() => setCandidateDialogOpen(false)}
            match={selectedMatch}
          />
          <JobDetailDialog
            open={jobDialogOpen}
            onClose={() => setJobDialogOpen(false)}
            match={selectedMatch}
          />
          <AHPBreakdownDialog
            open={ahpDialogOpen}
            onClose={() => setAhpDialogOpen(false)}
            match={selectedMatch}
          />
        </>
      )}
    </Card>
  );
};

export default CandidateMatchesSection;

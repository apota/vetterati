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
  Skeleton
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
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'candidateName'}
                        direction={sortBy === 'candidateName' ? sortOrder : 'asc'}
                        onClick={() => handleSortChange('candidateName')}
                      >
                        Candidate
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'jobTitle'}
                        direction={sortBy === 'jobTitle' ? sortOrder : 'asc'}
                        onClick={() => handleSortChange('jobTitle')}
                      >
                        Position
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'score'}
                        direction={sortBy === 'score' ? sortOrder : 'asc'}
                        onClick={() => handleSortChange('score')}
                      >
                        Match %
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>
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
                      <TableRow 
                        key={match.id}
                        hover
                        onClick={() => handleMatchClick(match)}
                        sx={{ cursor: 'pointer' }}
                      >
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ bgcolor: 'primary.main' }}>
                              <Person />
                            </Avatar>
                            <Box>
                              <Typography variant="body2" fontWeight="medium">
                                {match.candidateName}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                ID: {match.candidateId.substring(0, 8)}...
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Work fontSize="small" color="action" />
                            <Typography variant="body2">
                              {match.jobTitle}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${match.matchPercentage}%`}
                            color={getMatchColor(match.overallScore)}
                            size="small"
                            variant="filled"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={AhpService.getMatchConfidence(match.overallScore).toUpperCase()}
                            size="small"
                            variant="outlined"
                            sx={{ 
                              color: AhpService.getMatchConfidenceColor(match.overallScore),
                              borderColor: AhpService.getMatchConfidenceColor(match.overallScore)
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
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
    </Card>
  );
};

export default CandidateMatchesSection;

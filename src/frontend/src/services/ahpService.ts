import api from './apiService';
import axios from 'axios';

// Create direct AHP service client
const AHP_BASE_URL = 'http://localhost:5002/api/scoring';
const ahpApi = axios.create({
  baseURL: AHP_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor for AHP service
ahpApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export interface CandidateMatch {
  id: string;
  candidateId: string;
  jobProfileId: string;
  candidateName: string;
  jobTitle: string;
  overallScore: number;
  matchPercentage: number;
  criteriaScores: Record<string, number>;
  scoreBreakdown: Record<string, any>;
  calculatedAt: string;
  scoredAt: string;
  methodology: string;
  metadata?: Record<string, any>;
}

export interface CandidateMatchSummary {
  totalMatches: number;
  averageScore: number;
  highestScore: number;
  lowestScore: number;
  matchedJobs: number;
}

export interface PaginatedCandidateMatches {
  matches: CandidateMatch[];
  totalCount: number;
  currentPage: number;
  pageSize: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  summary?: CandidateMatchSummary;
}

export interface GetCandidateMatchesOptions {
  page?: number;
  pageSize?: number;
  sortBy?: 'score' | 'matchPercentage' | 'calculatedAt' | 'candidateName' | 'jobTitle';
  sortOrder?: 'asc' | 'desc';
  minScore?: number;
  maxScore?: number;
  jobProfileIds?: string[];
  candidateIds?: string[];
  dateFrom?: string;
  dateTo?: string;
}

export class AhpService {
  private static readonly BASE_URL = '/api/scoring';
  private static readonly AHP_BASE_URL = 'http://localhost:5002/api/scoring';

  // Get top candidate matches across all jobs
  static async getAllCandidateMatches(options: GetCandidateMatchesOptions = {}): Promise<PaginatedCandidateMatches> {
    const {
      page = 1,
      pageSize = 10,
      sortBy = 'score',
      sortOrder = 'desc',
      minScore,
      maxScore,
      jobProfileIds,
      candidateIds,
      dateFrom,
      dateTo
    } = options;

    const params = new URLSearchParams({
      page: page.toString(),
      pageSize: pageSize.toString(),
      sortBy,
      sortOrder
    });

    if (minScore !== undefined) params.append('minScore', minScore.toString());
    if (maxScore !== undefined) params.append('maxScore', maxScore.toString());
    if (jobProfileIds) jobProfileIds.forEach(id => params.append('jobProfileIds', id));
    if (candidateIds) candidateIds.forEach(id => params.append('candidateIds', id));
    if (dateFrom) params.append('dateFrom', dateFrom);
    if (dateTo) params.append('dateTo', dateTo);

    const response = await ahpApi.get(`/matches?${params}`);
    return this.transformMatchesResponse(response.data);
  }

  // Get candidate matches for a specific job
  static async getJobCandidateMatches(
    jobProfileId: string, 
    options: GetCandidateMatchesOptions = {}
  ): Promise<PaginatedCandidateMatches> {
    const {
      page = 1,
      pageSize = 10,
      sortBy = 'score',
      sortOrder = 'desc',
      minScore,
      maxScore
    } = options;

    const params = new URLSearchParams({
      limit: pageSize.toString()
    });

    if (minScore !== undefined) params.append('minScore', minScore.toString());
    if (maxScore !== undefined) params.append('maxScore', maxScore.toString());

    const response = await api.get(`${this.BASE_URL}/${jobProfileId}/top-candidates?${params}`);
    return this.transformJobMatchesResponse(response.data, jobProfileId);
  }

  // Get candidate match summary statistics
  static async getMatchSummary(): Promise<CandidateMatchSummary> {
    const response = await api.get(`${this.BASE_URL}/matches/summary`);
    return response.data;
  }

  // Score a candidate for a specific job
  static async scoreCandidateForJob(candidateId: string, jobProfileId: string): Promise<CandidateMatch> {
    const response = await api.post(`${this.BASE_URL}/calculate`, {
      candidateId,
      jobProfileId
    });
    return this.transformSingleMatch(response.data);
  }

  // Score all candidates for a job
  static async scoreAllCandidatesForJob(jobProfileId: string): Promise<{ candidatesScored: number; averageScore: number }> {
    const response = await api.post(`${this.BASE_URL}/${jobProfileId}/score-all`);
    return response.data;
  }

  // Refresh scores for a job profile
  static async refreshJobScores(jobProfileId: string): Promise<{ success: boolean; candidatesRefreshed: number }> {
    const response = await api.post(`${this.BASE_URL}/${jobProfileId}/refresh`);
    return response.data;
  }

  // Transform the API response from the AHP service to our frontend model
  private static transformMatchesResponse(data: any): PaginatedCandidateMatches {
    // This assumes we'll create a comprehensive matches endpoint
    // For now, we'll use the existing structure
    return {
      matches: data.matches?.map(this.transformSingleMatch) || [],
      totalCount: data.totalCount || 0,
      currentPage: data.currentPage || 1,
      pageSize: data.pageSize || 10,
      totalPages: data.totalPages || 1,
      hasNextPage: data.hasNextPage || false,
      hasPreviousPage: data.hasPreviousPage || false,
      summary: data.summary
    };
  }

  // Transform job-specific matches response
  private static transformJobMatchesResponse(data: any, jobProfileId: string): PaginatedCandidateMatches {
    const matches = Array.isArray(data) ? data : (data.matches || []);
    
    return {
      matches: matches.map((match: any) => this.transformSingleMatch(match, jobProfileId)),
      totalCount: matches.length,
      currentPage: 1,
      pageSize: matches.length,
      totalPages: 1,
      hasNextPage: false,
      hasPreviousPage: false
    };
  }

  // Transform a single candidate match
  private static transformSingleMatch(match: any, jobProfileId?: string): CandidateMatch {
    return {
      id: match.id || `${match.candidateId}-${match.jobProfileId}`,
      candidateId: match.candidateId,
      jobProfileId: match.jobProfileId || jobProfileId,
      candidateName: match.candidateName || 'Unknown Candidate',
      jobTitle: match.jobTitle || 'Unknown Position',
      overallScore: match.overallScore || 0,
      matchPercentage: Math.round((match.overallScore || 0) * 100),
      criteriaScores: match.criteriaScores || {},
      scoreBreakdown: match.scoreBreakdown || {},
      calculatedAt: match.calculatedAt || new Date().toISOString(),
      scoredAt: match.scoredAt || new Date().toISOString(),
      methodology: match.methodology || 'AHP',
      metadata: match.metadata
    };
  }

  // Helper method to get formatted match percentage
  static getFormattedMatchPercentage(score: number): string {
    return `${Math.round(score * 100)}%`;
  }

  // Helper method to get match confidence level
  static getMatchConfidence(score: number): 'high' | 'medium' | 'low' {
    if (score >= 0.8) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
  }

  // Helper method to get match confidence color
  static getMatchConfidenceColor(score: number): string {
    const confidence = this.getMatchConfidence(score);
    switch (confidence) {
      case 'high': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'low': return '#f44336';
      default: return '#757575';
    }
  }
}

export default AhpService;

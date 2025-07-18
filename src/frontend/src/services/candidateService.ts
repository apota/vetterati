import api from './apiService';
import { 
  CandidateListItem, 
  CandidateDetails, 
  CandidateCreateRequest, 
  CandidateUpdateRequest
} from '../types/candidate';

// Legacy interface for backward compatibility
export interface Candidate {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  location?: string;
  status: 'active' | 'hired' | 'rejected' | 'inactive';
  created_at: string;
  updated_at: string;
  skills: string[];
  experience_years?: number;
  education?: string;
  resume_url?: string;
}

export interface CandidateStats {
  total: number;
  active: number;
  hired: number;
  rejected: number;
  inactive: number;
  new_this_week: number;
  avg_experience_years: number;
  top_skills: Array<{ name: string; count: number }>;
  applications_by_status: Record<string, number>;
}

export interface CandidateApplication {
  id: string;
  job_id: string;
  job_title: string;
  status: 'applied' | 'reviewing' | 'interview' | 'offer' | 'hired' | 'rejected';
  created_at: string;
  updated_at: string;
}

export class CandidateService {
  // Get all candidates
  static async getCandidates(params?: {
    page?: number;
    limit?: number;
    status?: string;
    search?: string;
  }): Promise<{ items: CandidateListItem[], total: number }> {
    try {
      const response = await api.get('/api/v1/candidates', { params });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching candidates:', error);
      throw error;
    }
  }

  // Get candidate by ID
  static async getCandidateById(id: string): Promise<CandidateDetails> {
    try {
      const response = await api.get(`/api/v1/candidates/${id}`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching candidate:', error);
      throw error;
    }
  }

  // Create new candidate
  static async createCandidate(candidateData: CandidateCreateRequest): Promise<CandidateDetails> {
    try {
      const response = await api.post('/api/v1/candidates', candidateData);
      return response.data.data;
    } catch (error) {
      console.error('Error creating candidate:', error);
      throw error;
    }
  }

  // Update candidate
  static async updateCandidate(id: string, candidateData: CandidateUpdateRequest): Promise<CandidateDetails> {
    try {
      const response = await api.put(`/api/v1/candidates/${id}`, candidateData);
      return response.data.data;
    } catch (error) {
      console.error('Error updating candidate:', error);
      throw error;
    }
  }

  // Delete candidate
  static async deleteCandidate(id: string): Promise<void> {
    try {
      await api.delete(`/api/v1/candidates/${id}`);
    } catch (error) {
      console.error('Error deleting candidate:', error);
      throw error;
    }
  }

  // Get candidate statistics
  static async getCandidateStats(): Promise<CandidateStats> {
    try {
      const response = await api.get('/api/v1/candidates/stats');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching candidate stats:', error);
      throw error;
    }
  }

  // Get applications for a candidate
  static async getCandidateApplications(candidateId: string, params?: {
    page?: number;
    limit?: number;
  }): Promise<{ items: CandidateApplication[], total: number }> {
    try {
      const response = await api.get(`/api/v1/candidates/${candidateId}/applications`, { params });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching candidate applications:', error);
      throw error;
    }
  }

  // Search candidates
  static async searchCandidates(searchParams: {
    query?: string;
    skills?: string[];
    experience_min?: number;
    experience_max?: number;
    location?: string;
    page?: number;
    limit?: number;
  }): Promise<{ items: CandidateListItem[], total: number }> {
    try {
      const response = await api.post('/api/v1/candidates/search', searchParams);
      return response.data.data;
    } catch (error) {
      console.error('Error searching candidates:', error);
      throw error;
    }
  }

  // Upload candidate resume
  static async uploadResume(candidateId: string, file: File): Promise<{ url: string }> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post(`/api/v1/candidates/${candidateId}/resumes`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data.data;
    } catch (error) {
      console.error('Error uploading resume:', error);
      throw error;
    }
  }
}

export default CandidateService;

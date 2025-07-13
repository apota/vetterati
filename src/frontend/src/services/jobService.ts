import api from './apiService';

export interface Job {
  id: string;
  title: string;
  description: string;
  requirements: string;
  status: 'draft' | 'active' | 'paused' | 'closed';
  created_at: string;
  updated_at: string;
  company_id: string;
  location: string;
  salary_min?: number;
  salary_max?: number;
  employment_type: string;
}

export interface JobApplication {
  id: string;
  job_id: string;
  candidate_id: string;
  candidate_name: string;
  status: 'applied' | 'reviewing' | 'interview' | 'offer' | 'hired' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface JobStats {
  total: number;
  active: number;
  draft: number;
  paused: number;
  closed: number;
}

export class JobService {
  // Get all jobs
  static async getJobs(params?: {
    page?: number;
    limit?: number;
    status?: string;
    search?: string;
  }): Promise<{ items: Job[], total: number }> {
    try {
      const response = await api.get('/api/v1/jobs', { params });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching jobs:', error);
      throw error;
    }
  }

  // Get job by ID
  static async getJobById(id: string): Promise<Job> {
    try {
      const response = await api.get(`/api/v1/jobs/${id}`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching job:', error);
      throw error;
    }
  }

  // Create new job
  static async createJob(jobData: Partial<Job>): Promise<Job> {
    try {
      const response = await api.post('/api/v1/jobs', jobData);
      return response.data.data;
    } catch (error) {
      console.error('Error creating job:', error);
      throw error;
    }
  }

  // Update job
  static async updateJob(id: string, jobData: Partial<Job>): Promise<Job> {
    try {
      const response = await api.put(`/api/v1/jobs/${id}`, jobData);
      return response.data.data;
    } catch (error) {
      console.error('Error updating job:', error);
      throw error;
    }
  }

  // Delete job
  static async deleteJob(id: string): Promise<void> {
    try {
      await api.delete(`/api/v1/jobs/${id}`);
    } catch (error) {
      console.error('Error deleting job:', error);
      throw error;
    }
  }

  // Get job statistics
  static async getJobStats(): Promise<JobStats> {
    try {
      const response = await api.get('/api/v1/jobs/stats');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching job stats:', error);
      throw error;
    }
  }

  // Get applications for a job
  static async getJobApplications(jobId: string, params?: {
    page?: number;
    limit?: number;
  }): Promise<{ items: JobApplication[], total: number }> {
    try {
      const response = await api.get(`/api/v1/jobs/${jobId}/applications`, { params });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching job applications:', error);
      throw error;
    }
  }

  // Publish job
  static async publishJob(id: string): Promise<Job> {
    try {
      const response = await api.post(`/api/v1/jobs/${id}/publish`);
      return response.data.data;
    } catch (error) {
      console.error('Error publishing job:', error);
      throw error;
    }
  }

  // Pause job
  static async pauseJob(id: string): Promise<Job> {
    try {
      const response = await api.post(`/api/v1/jobs/${id}/pause`);
      return response.data.data;
    } catch (error) {
      console.error('Error pausing job:', error);
      throw error;
    }
  }
}

export default JobService;

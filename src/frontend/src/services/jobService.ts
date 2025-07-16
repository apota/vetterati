import axios from 'axios';
import { JobListItem, JobDetails, JobSearchFilters, PaginatedJobsResponse, JobCreateRequest } from '../types/job';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const jobService = {
  // Get paginated jobs list with filters
  async getJobs(filters: JobSearchFilters = {}): Promise<PaginatedJobsResponse> {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await axios.get(`${API_BASE_URL}/api/v1/jobs?${params}`);
    return response.data;
  },

  // Get single job details
  async getJob(jobId: string): Promise<JobDetails> {
    const response = await axios.get(`${API_BASE_URL}/api/v1/jobs/${jobId}`);
    return response.data;
  },

  // Create new job
  async createJob(jobData: JobCreateRequest): Promise<JobDetails> {
    const response = await axios.post(`${API_BASE_URL}/api/v1/jobs`, jobData);
    return response.data;
  },

  // Update job
  async updateJob(jobId: string, jobData: Partial<JobCreateRequest>): Promise<JobDetails> {
    const response = await axios.put(`${API_BASE_URL}/api/v1/jobs/${jobId}`, jobData);
    return response.data;
  },

  // Delete job
  async deleteJob(jobId: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/api/v1/jobs/${jobId}`);
  },

  // Get job statistics
  async getJobStats(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/api/v1/jobs/stats`);
    return response.data;
  },

  // Get job applications for a specific job
  async getJobApplications(jobId: string): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/api/v1/jobs/${jobId}/applications`);
    return response.data;
  }
};

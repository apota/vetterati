import axios from 'axios';
import { JobListItem, JobDetails, JobSearchFilters, PaginatedJobsResponse, JobCreateRequest } from '../types/job';

// Use relative URLs to leverage the proxy configuration
const API_BASE_URL = '/api/v1';

export const jobService = {
  // Get paginated jobs list with filters
  async getJobs(filters: JobSearchFilters = {}): Promise<PaginatedJobsResponse> {
    const params = new URLSearchParams();
    
    // Build query parameters
    for (const [key, value] of Object.entries(filters)) {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    }

    const response = await axios.get(`${API_BASE_URL}/jobs?${params}`);
    return response.data;
  },

  // Get single job details
  async getJob(jobId: string): Promise<JobDetails> {
    const response = await axios.get(`${API_BASE_URL}/jobs/${jobId}`);
    return response.data;
  },

  // Create new job
  async createJob(jobData: JobCreateRequest): Promise<JobDetails> {
    const response = await axios.post(`${API_BASE_URL}/jobs`, jobData);
    return response.data;
  },

  // Update job
  async updateJob(jobId: string, jobData: Partial<JobCreateRequest>): Promise<JobDetails> {
    const response = await axios.put(`${API_BASE_URL}/jobs/${jobId}`, jobData);
    return response.data;
  },

  // Delete job
  async deleteJob(jobId: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/jobs/${jobId}`);
  },

  // Get job statistics
  async getJobStats(): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/jobs/stats`);
    return response.data;
  },

  // Get job applications for a specific job
  async getJobApplications(jobId: string): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/jobs/${jobId}/applications`);
    return response.data;
  }
};

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

// Mock service for development/testing
export const mockJobService = {
  async getJobs(filters: JobSearchFilters = {}): Promise<PaginatedJobsResponse> {
    // Mock implementation using local storage or static data
    const mockJobs: JobListItem[] = [
      {
        id: '1',
        title: 'Senior Full Stack Developer',
        department: 'Engineering',
        location: 'San Francisco, CA',
        employment_type: 'full-time',
        status: 'active',
        priority: 'high',
        applications_count: 12,
        views_count: 145,
        created_at: new Date('2025-07-10').toISOString(),
        posted_at: new Date('2025-07-11').toISOString(),
        avg_match_percentage: 78.5,
        highest_match_percentage: 94
      },
      {
        id: '2',
        title: 'DevOps Engineer',
        department: 'Engineering',
        location: 'Remote',
        employment_type: 'full-time',
        status: 'active',
        priority: 'medium',
        applications_count: 8,
        views_count: 89,
        created_at: new Date('2025-07-08').toISOString(),
        posted_at: new Date('2025-07-09').toISOString(),
        avg_match_percentage: 72.3,
        highest_match_percentage: 87
      },
      {
        id: '3',
        title: 'Product Manager',
        department: 'Product',
        location: 'New York, NY',
        employment_type: 'full-time',
        status: 'paused',
        priority: 'medium',
        applications_count: 15,
        views_count: 203,
        created_at: new Date('2025-07-05').toISOString(),
        posted_at: new Date('2025-07-06').toISOString(),
        avg_match_percentage: 69.8,
        highest_match_percentage: 91
      },
      {
        id: '4',
        title: 'UX Designer',
        department: 'Design',
        location: 'Austin, TX',
        employment_type: 'full-time',
        status: 'active',
        priority: 'low',
        applications_count: 6,
        views_count: 67,
        created_at: new Date('2025-07-12').toISOString(),
        posted_at: new Date('2025-07-13').toISOString(),
        avg_match_percentage: 81.2,
        highest_match_percentage: 96
      },
      {
        id: '5',
        title: 'Data Scientist',
        department: 'Data',
        location: 'Seattle, WA',
        employment_type: 'full-time',
        status: 'closed',
        priority: 'high',
        applications_count: 22,
        views_count: 312,
        created_at: new Date('2025-06-28').toISOString(),
        posted_at: new Date('2025-06-29').toISOString(),
        avg_match_percentage: 75.9,
        highest_match_percentage: 89
      }
    ];

    // Apply filters
    let filteredJobs = mockJobs;

    if (filters.query) {
      filteredJobs = filteredJobs.filter(job => 
        job.title.toLowerCase().includes(filters.query!.toLowerCase()) ||
        job.department?.toLowerCase().includes(filters.query!.toLowerCase())
      );
    }

    if (filters.status) {
      filteredJobs = filteredJobs.filter(job => job.status === filters.status);
    }

    if (filters.department) {
      filteredJobs = filteredJobs.filter(job => job.department === filters.department);
    }

    if (filters.employment_type) {
      filteredJobs = filteredJobs.filter(job => job.employment_type === filters.employment_type);
    }

    if (filters.min_match_percentage) {
      filteredJobs = filteredJobs.filter(job => 
        (job.avg_match_percentage || 0) >= filters.min_match_percentage!
      );
    }

    if (filters.max_match_percentage) {
      filteredJobs = filteredJobs.filter(job => 
        (job.avg_match_percentage || 0) <= filters.max_match_percentage!
      );
    }

    // Apply sorting
    const sortBy = filters.sort_by || 'created_at';
    const sortOrder = filters.sort_order || 'desc';

    filteredJobs.sort((a, b) => {
      let aValue: any = a[sortBy as keyof JobListItem];
      let bValue: any = b[sortBy as keyof JobListItem];

      if (sortBy === 'created_at' || sortBy === 'posted_at') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    // Apply pagination
    const page = filters.page || 1;
    const perPage = filters.per_page || 10;
    const startIndex = (page - 1) * perPage;
    const endIndex = startIndex + perPage;
    const paginatedJobs = filteredJobs.slice(startIndex, endIndex);

    return {
      data: paginatedJobs,
      total: filteredJobs.length,
      page,
      per_page: perPage,
      total_pages: Math.ceil(filteredJobs.length / perPage),
      has_next: endIndex < filteredJobs.length,
      has_prev: page > 1
    };
  },

  async getJob(jobId: string): Promise<JobDetails> {
    const mockJob: JobDetails = {
      id: jobId,
      title: 'Senior Full Stack Developer',
      description: 'We are seeking a skilled Senior Full Stack Developer to join our dynamic engineering team. You will work on cutting-edge web applications using modern technologies and contribute to the architecture and development of scalable solutions.',
      requirements: '• 5+ years of experience in full-stack development\n• Proficiency in React, Node.js, and TypeScript\n• Experience with cloud platforms (AWS, Azure, or GCP)\n• Strong understanding of database design and SQL\n• Experience with REST APIs and GraphQL',
      responsibilities: '• Design and develop scalable web applications\n• Collaborate with cross-functional teams\n• Participate in code reviews and technical discussions\n• Mentor junior developers\n• Contribute to technical architecture decisions',
      benefits: '• Competitive salary and equity\n• Comprehensive health insurance\n• 401(k) with company matching\n• Flexible work arrangements\n• Professional development budget\n• Unlimited PTO',
      department: 'Engineering',
      location: 'San Francisco, CA',
      employment_type: 'full-time',
      experience_level: 'senior',
      salary_min: 140000,
      salary_max: 180000,
      salary_currency: 'USD',
      status: 'active',
      priority: 'high',
      required_skills: ['React', 'Node.js', 'TypeScript', 'AWS', 'PostgreSQL'],
      preferred_skills: ['GraphQL', 'Docker', 'Kubernetes', 'Python'],
      certifications: ['AWS Certified Developer'],
      languages: ['English'],
      created_by: 'user123',
      created_at: new Date('2025-07-10').toISOString(),
      updated_at: new Date('2025-07-15').toISOString(),
      posted_at: new Date('2025-07-11').toISOString(),
      applications_count: 12,
      views_count: 145,
      stats: {
        total_applications: 12,
        avg_match_percentage: 78.5,
        highest_match_percentage: 94,
        applications_by_status: {
          applied: 7,
          screening: 3,
          interview: 1,
          offer: 1
        }
      }
    };

    return mockJob;
  },

  async createJob(jobData: JobCreateRequest): Promise<JobDetails> {
    // Mock implementation - in real app, this would call the API
    const newJob: JobDetails = {
      id: Math.random().toString(36).substring(7),
      ...jobData,
      status: 'draft',
      priority: jobData.priority || 'medium',
      salary_currency: jobData.salary_currency || 'USD',
      created_by: 'current-user',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      applications_count: 0,
      views_count: 0
    };

    return newJob;
  },

  async updateJob(jobId: string, jobData: Partial<JobCreateRequest>): Promise<JobDetails> {
    // Mock implementation
    const existingJob = await this.getJob(jobId);
    return {
      ...existingJob,
      ...jobData,
      updated_at: new Date().toISOString()
    };
  },

  async deleteJob(jobId: string): Promise<void> {
    // Mock implementation
    console.log(`Deleting job ${jobId}`);
  }
};

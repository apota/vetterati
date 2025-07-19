import api from './apiService';
import { 
  InterviewStep,
  InterviewListItem, 
  InterviewDetails, 
  InterviewCreateRequest, 
  InterviewUpdateRequest,
  InterviewStats,
  ScheduleInterviewRequest,
  InterviewSearchFilters
} from '../types/interview';

export class InterviewService {
  // Get interview statistics
  static async getInterviewStats(): Promise<InterviewStats> {
    try {
      const response = await api.get('http://localhost:8002/api/v1/interviews/stats');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching interview stats:', error);
      // Return mock data on error
      return {
        today: 2,
        thisWeek: 5,
        scheduled: 3,
        completed: 8,
        total: 15
      };
    }
  }

  // Get all interviews with filtering and pagination
  static async getInterviews(params?: {
    page?: number;
    limit?: number;
    status?: string;
    interview_type?: string;
    search?: string;
    candidate_id?: string;
    job_id?: string;
    interviewer_id?: string;
    date_from?: string;
    date_to?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<{ items: InterviewListItem[], total: number }> {
    try {
      // Map frontend parameter names to backend parameter names
      const apiParams = {
        page: params?.page || 1,
        limit: params?.limit || 10,
        status: params?.status,
        interview_type: params?.interview_type,
        q: params?.search,
        candidate_id: params?.candidate_id,
        job_id: params?.job_id,
        interviewer_id: params?.interviewer_id,
        date_from: params?.date_from,
        date_to: params?.date_to,
        sort_by: params?.sort_by || 'scheduled_start',
        sort_order: params?.sort_order || 'asc'
      };

      // Call the workflow service for interviews
      const response = await api.get('http://localhost:8002/api/v1/interviews', { params: apiParams });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching interviews:', error);
      // Fallback to mock data on error
      const mockData = await this.getMockInterviews(params || {});
      return mockData;
    }
  }

  // Get interview by ID
  static async getInterviewById(id: string): Promise<InterviewDetails> {
    try {
      const response = await api.get(`/interviews/${id}`);
      return response.data.data;
    } catch (error) {
      console.error('Error fetching interview:', error);
      throw error;
    }
  }

  // Create new interview
  static async createInterview(interviewData: InterviewCreateRequest): Promise<InterviewStep> {
    try {
      const response = await api.post('/interviews', interviewData);
      return response.data.data;
    } catch (error) {
      console.error('Error creating interview:', error);
      throw error;
    }
  }

  // Update interview
  static async updateInterview(id: string, interviewData: InterviewUpdateRequest): Promise<InterviewStep> {
    try {
      const response = await api.put(`/interviews/${id}`, interviewData);
      return response.data.data;
    } catch (error) {
      console.error('Error updating interview:', error);
      throw error;
    }
  }

  // Schedule interview
  static async scheduleInterview(id: string, scheduleData: ScheduleInterviewRequest): Promise<void> {
    try {
      await api.post(`/interviews/${id}/schedule`, scheduleData);
    } catch (error) {
      console.error('Error scheduling interview:', error);
      throw error;
    }
  }

  // Cancel interview
  static async cancelInterview(id: string, reason?: string): Promise<void> {
    try {
      await api.post(`/interviews/${id}/cancel`, { reason });
    } catch (error) {
      console.error('Error cancelling interview:', error);
      throw error;
    }
  }

  // Submit interview feedback
  static async submitFeedback(id: string, feedback: any): Promise<void> {
    try {
      await api.post(`/interviews/${id}/feedback`, feedback);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  }

  // Get interviews for a specific workflow
  static async getWorkflowInterviews(workflowId: string): Promise<InterviewStep[]> {
    try {
      const response = await api.get(`/workflows/${workflowId}/interviews`);
      return response.data;
    } catch (error) {
      console.error('Error fetching workflow interviews:', error);
      throw error;
    }
  }

  // Get interviews for a specific candidate
  static async getCandidateInterviews(candidateId: string): Promise<InterviewListItem[]> {
    try {
      const response = await this.getInterviews({ candidate_id: candidateId });
      return response.items;
    } catch (error) {
      console.error('Error fetching candidate interviews:', error);
      throw error;
    }
  }

  // Mock data generator for development
  private static async getMockInterviews(params: any): Promise<{ items: InterviewListItem[], total: number }> {
    // This is temporary mock data - replace with actual API call when backend is ready
    const mockInterviews: InterviewListItem[] = [
      {
        id: '1',
        candidate_name: 'Jane Smith',
        candidate_id: '333333333-3333-3333-33333-333333333333',
        job_title: 'Senior Software Engineer',
        job_id: 'job-1',
        interview_type: 'technical',
        round_number: 1,
        title: 'Technical Interview - React & TypeScript',
        status: 'scheduled',
        scheduled_start: '2025-07-19T10:00:00Z',
        scheduled_end: '2025-07-19T11:30:00Z',
        interviewer_names: ['John Doe', 'Sarah Wilson'],
        meeting_url: 'https://meet.google.com/abc-defg-hij',
        created_at: '2025-07-18T08:00:00Z'
      },
      {
        id: '2',
        candidate_name: 'Mike Johnson',
        candidate_id: '444444444-4444-4444-44444-444444444444',
        job_title: 'Product Manager',
        job_id: 'job-2',
        interview_type: 'behavioral',
        round_number: 1,
        title: 'Initial Screening',
        status: 'completed',
        scheduled_start: '2025-07-17T14:00:00Z',
        scheduled_end: '2025-07-17T15:00:00Z',
        interviewer_names: ['Emily Davis'],
        meeting_url: 'https://zoom.us/j/123456789',
        created_at: '2025-07-16T10:00:00Z'
      },
      {
        id: '3',
        candidate_name: 'David Brown',
        candidate_id: '555555555-5555-5555-55555-555555555555',
        job_title: 'DevOps Engineer',
        job_id: 'job-3',
        interview_type: 'onsite',
        round_number: 2,
        title: 'Final Interview - System Design',
        status: 'pending',
        scheduled_start: '2025-07-20T09:00:00Z',
        scheduled_end: '2025-07-20T12:00:00Z',
        interviewer_names: ['Alex Chen', 'Maria Garcia', 'Tom Wilson'],
        location: 'Conference Room A',
        created_at: '2025-07-18T12:00:00Z'
      },
      {
        id: '4',
        candidate_name: 'Sarah Wilson',
        candidate_id: '666666666-6666-6666-66666-666666666666',
        job_title: 'UX Designer',
        job_id: 'job-4',
        interview_type: 'video',
        round_number: 1,
        title: 'Portfolio Review',
        status: 'in_progress',
        scheduled_start: '2025-07-18T16:00:00Z',
        scheduled_end: '2025-07-18T17:00:00Z',
        interviewer_names: ['Lisa Park'],
        meeting_url: 'https://teams.microsoft.com/l/meetup-join/abc123',
        created_at: '2025-07-17T14:00:00Z'
      },
      {
        id: '5',
        candidate_name: 'Emily Davis',
        candidate_id: '777777777-7777-7777-77777-777777777777',
        job_title: 'Marketing Manager',
        job_id: 'job-5',
        interview_type: 'phone',
        round_number: 1,
        title: 'HR Screening',
        status: 'cancelled',
        scheduled_start: '2025-07-19T11:00:00Z',
        scheduled_end: '2025-07-19T11:30:00Z',
        interviewer_names: ['Robert Kim'],
        created_at: '2025-07-18T09:00:00Z'
      }
    ];

    // Apply basic filtering
    let filteredInterviews = [...mockInterviews];
    
    if (params.status) {
      filteredInterviews = filteredInterviews.filter(interview => 
        interview.status === params.status
      );
    }
    
    if (params.interview_type) {
      filteredInterviews = filteredInterviews.filter(interview => 
        interview.interview_type === params.interview_type
      );
    }
    
    if (params.q) {
      const searchTerm = params.q.toLowerCase();
      filteredInterviews = filteredInterviews.filter(interview => 
        interview.candidate_name.toLowerCase().includes(searchTerm) ||
        interview.job_title.toLowerCase().includes(searchTerm) ||
        (interview.title && interview.title.toLowerCase().includes(searchTerm))
      );
    }

    // Apply pagination
    const startIndex = ((params.page || 1) - 1) * (params.limit || 10);
    const endIndex = startIndex + (params.limit || 10);
    const paginatedInterviews = filteredInterviews.slice(startIndex, endIndex);

    return {
      items: paginatedInterviews,
      total: filteredInterviews.length
    };
  }
}

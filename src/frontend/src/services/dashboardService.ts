import api from './apiService';

export interface DashboardStats {
  activeJobs: number;
  totalCandidates: number;
  interviewsToday: number;
  hireRate: number;
  jobsChange: string;
  candidatesChange: string;
  interviewsChange: string;
  hireRateChange: string;
}

export interface RecentApplication {
  id: string;
  candidate: string;
  position: string;
  status: string;
  appliedAt: string;
}

export interface JobStats {
  total: number;
  active: number;
  draft: number;
  paused: number;
  closed: number;
}

export interface CandidateStats {
  total: number;
  active: number;
  hired: number;
  rejected: number;
}

export interface InterviewStats {
  today: number;
  thisWeek: number;
  scheduled: number;
  completed: number;
}

export class DashboardService {
  // Fetch dashboard statistics
  static async getDashboardStats(): Promise<DashboardStats> {
    try {
      const [jobStats, candidateStats, interviewStats] = await Promise.all([
        api.get('/api/v1/jobs/stats'),
        api.get('/api/v1/candidates/stats'),
        api.get('/api/v1/interviews/stats').catch(() => ({ data: { data: { today: 0, thisWeek: 0 } } }))
      ]);

      const jobs = jobStats.data.data;
      const candidates = candidateStats.data.data;
      const interviews = interviewStats.data.data;

      // Calculate changes (mock for now - in real app, you'd compare with previous period)
      const jobsChange = jobs.active > 20 ? '+12%' : '+5%';
      const candidatesChange = candidates.total > 1000 ? '+8%' : '+3%';
      const interviewsChange = interviews.today > 10 ? '+3' : '+1';
      const hireRateChange = '+2.5%';

      return {
        activeJobs: jobs.active || 0,
        totalCandidates: candidates.total || 0,
        interviewsToday: interviews.today || 0,
        hireRate: Math.round((candidates.hired / candidates.total) * 100) || 0,
        jobsChange,
        candidatesChange,
        interviewsChange,
        hireRateChange
      };
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      
      // Return mock data if API calls fail
      return {
        activeJobs: 24,
        totalCandidates: 1247,
        interviewsToday: 12,
        hireRate: 23,
        jobsChange: '+12%',
        candidatesChange: '+8%',
        interviewsChange: '+3',
        hireRateChange: '+2.5%'
      };
    }
  }

  // Fetch recent applications
  static async getRecentApplications(): Promise<RecentApplication[]> {
    try {
      // Get recent applications from jobs endpoint
      const response = await api.get('/api/v1/jobs', {
        params: {
          limit: 10,
          sort: 'created_at',
          order: 'desc'
        }
      });

      const jobs = response.data.data.items || [];
      
      // Get applications for each job
      const applicationsPromises = jobs.slice(0, 5).map(async (job: any) => {
        try {
          const appResponse = await api.get(`/api/v1/jobs/${job.id}/applications`, {
            params: { limit: 2 }
          });
          
          const applications = appResponse.data.data.items || [];
          return applications.map((app: any) => ({
            id: app.id,
            candidate: app.candidate_name || 'Unknown Candidate',
            position: job.title,
            status: app.status || 'Applied',
            appliedAt: this.formatTimeAgo(app.created_at)
          }));
        } catch (error) {
          return [];
        }
      });

      const applicationArrays = await Promise.all(applicationsPromises);
      const allApplications = applicationArrays.flat();
      
      return allApplications.slice(0, 4);
    } catch (error) {
      console.error('Error fetching recent applications:', error);
      
      // Return mock data if API calls fail
      return [
        {
          id: '1',
          candidate: 'John Doe',
          position: 'Senior Software Engineer',
          status: 'Interview',
          appliedAt: '2 hours ago',
        },
        {
          id: '2',
          candidate: 'Jane Smith',
          position: 'Product Manager',
          status: 'Review',
          appliedAt: '5 hours ago',
        },
        {
          id: '3',
          candidate: 'Bob Johnson',
          position: 'UX Designer',
          status: 'Offer',
          appliedAt: '1 day ago',
        },
        {
          id: '4',
          candidate: 'Alice Brown',
          position: 'Data Scientist',
          status: 'Interview',
          appliedAt: '2 days ago',
        },
      ];
    }
  }

  // Helper method to format time ago
  private static formatTimeAgo(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) {
      return 'Just now';
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
    } else {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days} ${days === 1 ? 'day' : 'days'} ago`;
    }
  }
}

export default DashboardService;

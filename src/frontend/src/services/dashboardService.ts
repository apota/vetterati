import api from './apiService';

export type TimeWindow = 'day' | 'week' | 'month' | 'quarter' | 'year';

export interface TimeWindowOption {
  value: TimeWindow;
  label: string;
  description: string;
}

export interface DashboardStats {
  activeJobs: number;
  totalCandidates: number;
  interviewsToday: number;
  hireRate: number;
  jobsChange: string;
  candidatesChange: string;
  interviewsChange: string;
  hireRateChange: string;
  timeWindow: TimeWindow;
  comparisonPeriod: string;
}

export interface TimeWindowStats {
  current: {
    activeJobs: number;
    totalCandidates: number;
    interviewsToday: number;
    hireRate: number;
  };
  previous: {
    activeJobs: number;
    totalCandidates: number;
    interviewsToday: number;
    hireRate: number;
  };
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
  static readonly TIME_WINDOW_OPTIONS: TimeWindowOption[] = [
    { value: 'day', label: 'Previous Day', description: 'Compare with yesterday' },
    { value: 'week', label: 'Previous Week', description: 'Compare with last week' },
    { value: 'month', label: 'Previous Month', description: 'Compare with last month' },
    { value: 'quarter', label: 'Previous Quarter', description: 'Compare with last quarter' },
    { value: 'year', label: 'Previous Year', description: 'Compare with last year' },
  ];

  // Helper method to get date range for time window
  private static getDateRange(timeWindow: TimeWindow): { start: Date; end: Date; previousStart: Date; previousEnd: Date } {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    switch (timeWindow) {
      case 'day':
        return {
          start: today,
          end: now,
          previousStart: new Date(today.getTime() - 24 * 60 * 60 * 1000),
          previousEnd: today
        };
      case 'week':
        const weekStart = new Date(today.getTime() - today.getDay() * 24 * 60 * 60 * 1000);
        const weekEnd = new Date(weekStart.getTime() + 7 * 24 * 60 * 60 * 1000);
        return {
          start: weekStart,
          end: weekEnd,
          previousStart: new Date(weekStart.getTime() - 7 * 24 * 60 * 60 * 1000),
          previousEnd: weekStart
        };
      case 'month':
        const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
        const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        const prevMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
        const prevMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);
        return {
          start: monthStart,
          end: monthEnd,
          previousStart: prevMonthStart,
          previousEnd: prevMonthEnd
        };
      case 'quarter':
        const quarter = Math.floor(today.getMonth() / 3);
        const quarterStart = new Date(today.getFullYear(), quarter * 3, 1);
        const quarterEnd = new Date(today.getFullYear(), (quarter + 1) * 3, 0);
        const prevQuarterStart = new Date(today.getFullYear(), (quarter - 1) * 3, 1);
        const prevQuarterEnd = new Date(today.getFullYear(), quarter * 3, 0);
        return {
          start: quarterStart,
          end: quarterEnd,
          previousStart: prevQuarterStart,
          previousEnd: prevQuarterEnd
        };
      case 'year':
        const yearStart = new Date(today.getFullYear(), 0, 1);
        const yearEnd = new Date(today.getFullYear(), 11, 31);
        const prevYearStart = new Date(today.getFullYear() - 1, 0, 1);
        const prevYearEnd = new Date(today.getFullYear() - 1, 11, 31);
        return {
          start: yearStart,
          end: yearEnd,
          previousStart: prevYearStart,
          previousEnd: prevYearEnd
        };
      default:
        return this.getDateRange('day');
    }
  }

  // Helper method to calculate percentage change
  private static calculateChange(current: number, previous: number): string {
    if (previous === 0) return current > 0 ? '+100%' : '0%';
    const change = ((current - previous) / previous) * 100;
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(1)}%`;
  }

  // Helper method to format comparison period
  private static formatComparisonPeriod(timeWindow: TimeWindow): string {
    const option = this.TIME_WINDOW_OPTIONS.find(opt => opt.value === timeWindow);
    return option ? option.label : 'Previous Day';
  }

  // Fetch dashboard statistics with time window
  static async getDashboardStats(timeWindow: TimeWindow = 'day'): Promise<DashboardStats> {
    try {
      // For now, we'll simulate time-based data since the backend doesn't support date ranges yet
      // In a real implementation, you would pass date parameters to the API calls
      const [jobStats, candidateStats, interviewStats] = await Promise.all([
        api.get('/api/v1/jobs/stats'),
        api.get('/api/v1/candidates/stats'),
        api.get('/api/v1/interviews/stats').catch(() => ({ data: { data: { today: 0, thisWeek: 0 } } }))
      ]);

      const jobs = jobStats.data.data;
      const candidates = candidateStats.data.data;
      const interviews = interviewStats.data.data;

      // Simulate historical data based on time window
      const simulatedPrevious = this.simulatePreviousData(timeWindow, {
        activeJobs: jobs.active || 0,
        totalCandidates: candidates.total || 0,
        interviewsToday: interviews.today || 0,
        hireRate: Math.round((candidates.hired / candidates.total) * 100) || 0
      });

      return {
        activeJobs: jobs.active || 0,
        totalCandidates: candidates.total || 0,
        interviewsToday: interviews.today || 0,
        hireRate: Math.round((candidates.hired / candidates.total) * 100) || 0,
        jobsChange: this.calculateChange(jobs.active || 0, simulatedPrevious.activeJobs),
        candidatesChange: this.calculateChange(candidates.total || 0, simulatedPrevious.totalCandidates),
        interviewsChange: this.calculateChange(interviews.today || 0, simulatedPrevious.interviewsToday),
        hireRateChange: this.calculateChange(Math.round((candidates.hired / candidates.total) * 100) || 0, simulatedPrevious.hireRate),
        timeWindow,
        comparisonPeriod: this.formatComparisonPeriod(timeWindow)
      };
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      
      // Return mock data with time window if API calls fail
      const mockCurrent = {
        activeJobs: 24,
        totalCandidates: 1247,
        interviewsToday: 12,
        hireRate: 23
      };
      
      const simulatedPrevious = this.simulatePreviousData(timeWindow, mockCurrent);

      return {
        ...mockCurrent,
        jobsChange: this.calculateChange(mockCurrent.activeJobs, simulatedPrevious.activeJobs),
        candidatesChange: this.calculateChange(mockCurrent.totalCandidates, simulatedPrevious.totalCandidates),
        interviewsChange: this.calculateChange(mockCurrent.interviewsToday, simulatedPrevious.interviewsToday),
        hireRateChange: this.calculateChange(mockCurrent.hireRate, simulatedPrevious.hireRate),
        timeWindow,
        comparisonPeriod: this.formatComparisonPeriod(timeWindow)
      };
    }
  }

  // Simulate previous period data for demonstration
  private static simulatePreviousData(timeWindow: TimeWindow, current: any) {
    const variations = {
      day: { min: 0.85, max: 1.15 },
      week: { min: 0.80, max: 1.20 },
      month: { min: 0.70, max: 1.30 },
      quarter: { min: 0.60, max: 1.40 },
      year: { min: 0.50, max: 1.50 }
    };

    const variation = variations[timeWindow] || variations.day;
    const randomFactor = variation.min + Math.random() * (variation.max - variation.min);

    return {
      activeJobs: Math.floor(current.activeJobs / randomFactor),
      totalCandidates: Math.floor(current.totalCandidates / randomFactor),
      interviewsToday: Math.floor(current.interviewsToday / randomFactor),
      hireRate: Math.floor(current.hireRate / randomFactor)
    };
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

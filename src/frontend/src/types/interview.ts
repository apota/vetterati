// Interview Management API Models

export type InterviewType = 'phone' | 'video' | 'onsite' | 'panel' | 'technical' | 'behavioral';

export type InterviewStatus = 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';

export type WorkflowStatus = 'active' | 'completed' | 'cancelled' | 'on_hold';

export interface InterviewParticipant {
  id: string;
  name: string;
  email: string;
  role?: string;
}

export interface InterviewQuestion {
  id: string;
  question: string;
  category: string;
  expected_answer?: string;
  weight?: number;
}

export interface EvaluationCriteria {
  id: string;
  name: string;
  description: string;
  weight: number;
  scale_min: number;
  scale_max: number;
}

export interface InterviewFeedback {
  interviewer_id: string;
  interviewer_name: string;
  ratings: Record<string, number>;
  comments: string;
  recommendation: 'hire' | 'reject' | 'maybe' | 'strong_hire';
  submitted_at: string;
}

export interface InterviewScores {
  overall_score: number;
  technical_score?: number;
  communication_score?: number;
  cultural_fit_score?: number;
  problem_solving_score?: number;
  detailed_scores: Record<string, number>;
}

export interface InterviewStep {
  id: string;
  workflow_id: string;
  interview_type: InterviewType;
  round_number: number;
  title?: string;
  description?: string;
  
  // Scheduling
  scheduled_start?: string;
  scheduled_end?: string;
  actual_start?: string;
  actual_end?: string;
  
  // Participants
  interviewer_ids: string[];
  additional_participants: InterviewParticipant[];
  
  // Meeting details
  meeting_url?: string;
  meeting_id?: string;
  meeting_password?: string;
  location?: string;
  
  // Content and evaluation
  interview_questions: InterviewQuestion[];
  evaluation_criteria: EvaluationCriteria[];
  feedback: InterviewFeedback[];
  scores?: InterviewScores;
  
  // Status and metadata
  status: InterviewStatus;
  notes?: string;
  attachments?: string[];
  created_at: string;
  updated_at: string;
}

export interface CandidateWorkflow {
  id: string;
  candidate_id: string;
  job_id: string;
  template_id?: string;
  
  // State management
  current_state: string;
  previous_state?: string;
  state_history: Array<{
    state: string;
    timestamp: string;
    changed_by?: string;
    notes?: string;
  }>;
  
  // Progress tracking
  progress_percentage: number;
  estimated_completion?: string;
  
  // Workflow data
  workflow_data: Record<string, any>;
  
  // Status
  status: WorkflowStatus;
  
  // Timestamps
  started_at: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  
  // Related data
  interview_steps?: InterviewStep[];
}

export interface InterviewStats {
  today: number;
  thisWeek: number;
  scheduled: number;
  completed: number;
  total: number;
}

export interface InterviewListItem {
  id: string;
  candidate_name: string;
  candidate_id: string;
  job_title: string;
  job_id: string;
  interview_type: InterviewType;
  round_number: number;
  title?: string;
  status: InterviewStatus;
  scheduled_start?: string;
  scheduled_end?: string;
  interviewer_names: string[];
  location?: string;
  meeting_url?: string;
  created_at: string;
}

export interface InterviewDetails extends InterviewStep {
  candidate_name: string;
  candidate_email: string;
  job_title: string;
  job_department?: string;
  interviewer_details: InterviewParticipant[];
}

export interface InterviewCreateRequest {
  workflow_id: string;
  interview_type: InterviewType;
  round_number: number;
  title?: string;
  description?: string;
  interviewer_ids: string[];
  additional_participants?: InterviewParticipant[];
  interview_questions?: InterviewQuestion[];
  evaluation_criteria?: EvaluationCriteria[];
}

export interface InterviewUpdateRequest {
  title?: string;
  description?: string;
  scheduled_start?: string;
  scheduled_end?: string;
  meeting_url?: string;
  meeting_id?: string;
  meeting_password?: string;
  location?: string;
  status?: InterviewStatus;
  feedback?: InterviewFeedback;
  scores?: InterviewScores;
  notes?: string;
}

export interface InterviewSearchFilters {
  query?: string;
  status?: InterviewStatus;
  interview_type?: InterviewType;
  candidate_id?: string;
  job_id?: string;
  interviewer_id?: string;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface ScheduleInterviewRequest {
  scheduled_start: string;
  scheduled_end: string;
  meeting_url?: string;
  meeting_id?: string;
  meeting_password?: string;
  location?: string;
  send_notifications?: boolean;
}

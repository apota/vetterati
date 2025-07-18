// Candidate Management API Models
export interface CandidateStatus {
  ACTIVE: 'active';
  HIRED: 'hired';
  REJECTED: 'rejected';
  INACTIVE: 'inactive';
}

export interface CareerLevel {
  ENTRY: 'entry';
  MID: 'mid';
  SENIOR: 'senior';
  EXECUTIVE: 'executive';
}

export interface CandidateSource {
  WEB: 'web';
  REFERRAL: 'referral';
  LINKEDIN: 'linkedin';
  INDEED: 'indeed';
  GLASSDOOR: 'glassdoor';
  AGENCY: 'agency';
  OTHER: 'other';
}

export interface CandidateSkill {
  id: string;
  name: string;
  proficiency_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  years_experience: number;
}

export interface CandidateExperience {
  id: string;
  company_name: string;
  job_title: string;
  start_date: string;
  end_date?: string;
  description: string;
  is_current: boolean;
}

export interface CandidateEducation {
  id: string;
  institution: string;
  degree: string;
  field_of_study: string;
  graduation_year: number;
  gpa?: number;
}

export interface CandidateResume {
  id: string;
  filename: string;
  file_url: string;
  file_size: number;
  uploaded_at: string;
  is_primary: boolean;
}

export interface CandidateApplication {
  id: string;
  job_id: string;
  job_title: string;
  status: 'applied' | 'reviewing' | 'interview' | 'offer' | 'hired' | 'rejected';
  source: string;
  match_percentage: number;
  ahp_score: number;
  applied_at: string;
  last_updated: string;
}

export interface CandidateListItem {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  location?: string;
  status: 'active' | 'hired' | 'rejected' | 'inactive';
  career_level?: 'entry' | 'mid' | 'senior' | 'executive';
  total_years_experience?: number;
  source?: string;
  created_at: string;
  updated_at: string;
  applications_count: number;
  latest_application_status?: string;
}

export interface CandidateDetails {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  
  // Location information
  location_city?: string;
  location_state?: string;
  location_country?: string;
  location_coordinates_lat?: number;
  location_coordinates_lng?: number;
  
  // Social profiles
  linkedin_url?: string;
  portfolio_url?: string;
  github_url?: string;
  
  // Career summary
  total_years_experience?: number;
  career_level?: 'entry' | 'mid' | 'senior' | 'executive';
  current_salary?: number;
  expected_salary?: number;
  
  // Profile information
  summary?: string;
  status: 'active' | 'hired' | 'rejected' | 'inactive';
  source?: string;
  
  // Metadata
  created_at: string;
  updated_at: string;
  created_by?: string;
  
  // Related data
  skills: CandidateSkill[];
  experiences: CandidateExperience[];
  educations: CandidateEducation[];
  resumes: CandidateResume[];
  applications: CandidateApplication[];
}

export interface CandidateSearchFilters {
  query: string;
  status: string;
  career_level: string;
  source: string;
  min_experience: number | undefined;
  max_experience: number | undefined;
  location: string;
  skills: string[];
  sort_by: string;
  sort_order: 'asc' | 'desc';
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

export interface CandidateCreateRequest {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  location_city?: string;
  location_state?: string;
  location_country?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  github_url?: string;
  total_years_experience?: number;
  career_level?: 'entry' | 'mid' | 'senior' | 'executive';
  current_salary?: number;
  expected_salary?: number;
  summary?: string;
  status?: 'active' | 'hired' | 'rejected' | 'inactive';
  source?: string;
  skills?: Array<{
    name: string;
    proficiency_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
    years_experience: number;
  }>;
}

export interface CandidateUpdateRequest extends Partial<CandidateCreateRequest> {
  id: string;
}

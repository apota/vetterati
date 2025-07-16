// Job Management API Models
export interface JobStatus {
  DRAFT: 'draft';
  ACTIVE: 'active';
  PAUSED: 'paused';
  CLOSED: 'closed';
}

export interface EmploymentType {
  FULL_TIME: 'full-time';
  PART_TIME: 'part-time';
  CONTRACT: 'contract';
  INTERNSHIP: 'internship';
  FREELANCE: 'freelance';
}

export interface ExperienceLevel {
  ENTRY: 'entry';
  MID: 'mid';
  SENIOR: 'senior';
  EXECUTIVE: 'executive';
}

export interface Priority {
  LOW: 'low';
  MEDIUM: 'medium';
  HIGH: 'high';
  URGENT: 'urgent';
}

export interface JobApplication {
  id: string;
  job_id: string;
  candidate_id: string;
  status: string;
  source: string;
  cover_letter?: string;
  match_percentage: number;
  ahp_score: number;
  applied_at: string;
  last_updated: string;
}

export interface JobStats {
  total_applications: number;
  avg_match_percentage: number;
  highest_match_percentage: number;
  applications_by_status: Record<string, number>;
}

export interface JobListItem {
  id: string;
  title: string;
  department?: string;
  location?: string;
  employment_type?: string;
  status: string;
  priority: string;
  applications_count: number;
  views_count: number;
  created_at: string;
  posted_at?: string;
  avg_match_percentage?: number;
  highest_match_percentage?: number;
}

export interface JobDetails {
  id: string;
  title: string;
  description?: string;
  requirements?: string;
  responsibilities?: string;
  benefits?: string;
  department?: string;
  location?: string;
  employment_type?: string;
  experience_level?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  status: string;
  priority: string;
  slug?: string;
  required_skills?: string[];
  preferred_skills?: string[];
  certifications?: string[];
  languages?: string[];
  seo_title?: string;
  seo_description?: string;
  keywords?: string[];
  created_by: string;
  created_at: string;
  updated_at: string;
  posted_at?: string;
  closed_at?: string;
  applications_count: number;
  views_count: number;
  applications?: JobApplication[];
  stats?: JobStats;
}

export interface JobSearchFilters {
  query?: string;
  department?: string;
  location?: string;
  employment_type?: string;
  experience_level?: string;
  status?: string;
  priority?: string;
  min_match_percentage?: number;
  max_match_percentage?: number;
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedJobsResponse {
  data: JobListItem[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface JobCreateRequest {
  title: string;
  description?: string;
  requirements?: string;
  responsibilities?: string;
  benefits?: string;
  department?: string;
  location?: string;
  employment_type?: string;
  experience_level?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  priority?: string;
  required_skills?: string[];
  preferred_skills?: string[];
  certifications?: string[];
  languages?: string[];
  seo_title?: string;
  seo_description?: string;
  keywords?: string[];
}

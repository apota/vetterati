from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from models import Job, JobApplication, JobTemplate, JobView
from schemas import JobCreate, JobUpdate, JobSearchRequest
from database import get_elasticsearch
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import uuid
from slugify import slugify
import json

class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.es = get_elasticsearch()
    
    def create_job(self, job_data: JobCreate, created_by: uuid.UUID) -> Job:
        """Create a new job posting"""
        # Generate slug from title
        slug = self._generate_unique_slug(job_data.title)
        
        job = Job(
            **job_data.dict(exclude={'slug'}),
            slug=slug,
            created_by=created_by
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        # Index in Elasticsearch
        self._index_job_in_elasticsearch(job)
        
        return job
    
    def get_job(self, job_id: uuid.UUID) -> Optional[Job]:
        """Get job by ID"""
        return self.db.query(Job).filter(Job.id == job_id).first()
    
    def get_job_by_slug(self, slug: str) -> Optional[Job]:
        """Get job by slug"""
        return self.db.query(Job).filter(Job.slug == slug).first()
    
    def update_job(self, job_id: uuid.UUID, job_data: JobUpdate) -> Optional[Job]:
        """Update existing job"""
        job = self.get_job(job_id)
        if not job:
            return None
        
        update_data = job_data.dict(exclude_unset=True)
        
        # Update slug if title changed
        if 'title' in update_data:
            update_data['slug'] = self._generate_unique_slug(update_data['title'], exclude_id=job_id)
        
        for field, value in update_data.items():
            setattr(job, field, value)
        
        self.db.commit()
        self.db.refresh(job)
        
        # Update in Elasticsearch
        self._index_job_in_elasticsearch(job)
        
        return job
    
    def delete_job(self, job_id: uuid.UUID) -> bool:
        """Delete job (soft delete by setting status to closed)"""
        job = self.get_job(job_id)
        if not job:
            return False
        
        job.status = 'closed'
        job.closed_at = datetime.utcnow()
        self.db.commit()
        
        # Remove from Elasticsearch active index
        self._remove_job_from_elasticsearch(job_id)
        
        return True
    
    def search_jobs(self, search_request: JobSearchRequest) -> Tuple[List[Job], int]:
        """Search jobs with filters and pagination"""
        query = self.db.query(Job)
        
        # Apply filters
        if search_request.query:
            query = query.filter(
                or_(
                    Job.title.ilike(f"%{search_request.query}%"),
                    Job.description.ilike(f"%{search_request.query}%"),
                    Job.requirements.ilike(f"%{search_request.query}%")
                )
            )
        
        if search_request.department:
            query = query.filter(Job.department.ilike(f"%{search_request.department}%"))
        
        if search_request.location:
            query = query.filter(Job.location.ilike(f"%{search_request.location}%"))
        
        if search_request.employment_type:
            query = query.filter(Job.employment_type == search_request.employment_type)
        
        if search_request.experience_level:
            query = query.filter(Job.experience_level == search_request.experience_level)
        
        if search_request.status:
            query = query.filter(Job.status == search_request.status)
        
        if search_request.skills:
            for skill in search_request.skills:
                query = query.filter(
                    or_(
                        Job.required_skills.contains([skill]),
                        Job.preferred_skills.contains([skill])
                    )
                )
        
        if search_request.salary_min:
            query = query.filter(Job.salary_min >= search_request.salary_min)
        
        if search_request.salary_max:
            query = query.filter(Job.salary_max <= search_request.salary_max)
        
        if search_request.created_by:
            query = query.filter(Job.created_by == search_request.created_by)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(Job, search_request.sort_by, Job.created_at)
        if search_request.sort_order == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (search_request.page - 1) * search_request.per_page
        jobs = query.offset(offset).limit(search_request.per_page).all()
        
        return jobs, total
    
    def get_job_stats(self) -> Dict[str, Any]:
        """Get job statistics"""
        # Get total jobs by status
        total_jobs = self.db.query(Job).count()
        active_jobs = self.db.query(Job).filter(Job.status == 'active').count()
        draft_jobs = self.db.query(Job).filter(Job.status == 'draft').count()
        paused_jobs = self.db.query(Job).filter(Job.status == 'paused').count()
        closed_jobs = self.db.query(Job).filter(Job.status == 'closed').count()
        
        # Get total applications
        total_applications = self.db.query(JobApplication).count()
        
        return {
            "total": total_jobs,
            "active": active_jobs,
            "draft": draft_jobs,
            "paused": paused_jobs,
            "closed": closed_jobs,
            "total_applications": total_applications
        }

    def publish_job(self, job_id: uuid.UUID) -> Optional[Job]:
        """Publish a job (change status from draft to active)"""
        job = self.get_job(job_id)
        if not job or job.status != 'draft':
            return None
        
        job.status = 'active'
        job.posted_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(job)
        
        # Update in Elasticsearch
        self._index_job_in_elasticsearch(job)
        
        return job
    
    def pause_job(self, job_id: uuid.UUID) -> Optional[Job]:
        """Pause an active job"""
        job = self.get_job(job_id)
        if not job or job.status != 'active':
            return None
        
        job.status = 'paused'
        self.db.commit()
        self.db.refresh(job)
        
        return job
    
    def track_job_view(self, job_id: uuid.UUID, visitor_data: Dict[str, Any]) -> None:
        """Track job view for analytics"""
        view = JobView(
            job_id=job_id,
            **visitor_data
        )
        self.db.add(view)
        self.db.commit()
    
    def _generate_unique_slug(self, title: str, exclude_id: Optional[uuid.UUID] = None) -> str:
        """Generate unique slug for job title"""
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        
        while True:
            query = self.db.query(Job).filter(Job.slug == slug)
            if exclude_id:
                query = query.filter(Job.id != exclude_id)
            
            if not query.first():
                return slug
            
            slug = f"{base_slug}-{counter}"
            counter += 1
    
    def _index_job_in_elasticsearch(self, job: Job) -> None:
        """Index job in Elasticsearch for search"""
        try:
            doc = {
                'id': str(job.id),
                'title': job.title,
                'description': job.description,
                'requirements': job.requirements,
                'responsibilities': job.responsibilities,
                'department': job.department,
                'location': job.location,
                'employment_type': job.employment_type,
                'experience_level': job.experience_level,
                'status': job.status,
                'required_skills': job.required_skills or [],
                'preferred_skills': job.preferred_skills or [],
                'salary_min': float(job.salary_min) if job.salary_min else None,
                'salary_max': float(job.salary_max) if job.salary_max else None,
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'posted_at': job.posted_at.isoformat() if job.posted_at else None,
            }
            
            self.es.index(
                index='jobs',
                id=str(job.id),
                document=doc
            )
        except Exception as e:
            # Log error but don't fail the main operation
            print(f"Failed to index job in Elasticsearch: {e}")
    
    def _remove_job_from_elasticsearch(self, job_id: uuid.UUID) -> None:
        """Remove job from Elasticsearch index"""
        try:
            self.es.delete(index='jobs', id=str(job_id))
        except Exception as e:
            # Log error but don't fail the main operation
            print(f"Failed to remove job from Elasticsearch: {e}")

class JobApplicationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_application(self, application_data: Dict[str, Any]) -> JobApplication:
        """Create a new job application"""
        application = JobApplication(**application_data)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def get_applications_for_job(self, job_id: uuid.UUID, page: int = 1, per_page: int = 20) -> Tuple[List[JobApplication], int]:
        """Get applications for a specific job"""
        query = self.db.query(JobApplication).filter(JobApplication.job_id == job_id)
        total = query.count()
        
        offset = (page - 1) * per_page
        applications = query.order_by(desc(JobApplication.applied_at)).offset(offset).limit(per_page).all()
        
        return applications, total
    
    def update_application_status(self, application_id: uuid.UUID, status: str) -> Optional[JobApplication]:
        """Update application status"""
        application = self.db.query(JobApplication).filter(JobApplication.id == application_id).first()
        if not application:
            return None
        
        application.status = status
        application.last_updated = datetime.utcnow()
        self.db.commit()
        self.db.refresh(application)
        
        return application

class JobTemplateService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_template(self, template_data: Dict[str, Any], created_by: uuid.UUID) -> JobTemplate:
        """Create a new job template"""
        template = JobTemplate(**template_data, created_by=created_by)
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def get_templates(self, created_by: Optional[uuid.UUID] = None, category: Optional[str] = None) -> List[JobTemplate]:
        """Get job templates with optional filters"""
        query = self.db.query(JobTemplate)
        
        if created_by:
            query = query.filter(JobTemplate.created_by == created_by)
        
        if category:
            query = query.filter(JobTemplate.category == category)
        
        return query.order_by(desc(JobTemplate.created_at)).all()
    
    def create_job_from_template(self, template_id: uuid.UUID, created_by: uuid.UUID) -> Optional[Job]:
        """Create a new job from a template"""
        template = self.db.query(JobTemplate).filter(JobTemplate.id == template_id).first()
        if not template:
            return None
        
        job_data = JobCreate(**template.template_data)
        job_service = JobService(self.db)
        return job_service.create_job(job_data, created_by)

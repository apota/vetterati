from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import uuid
import json

from models import Candidate, CandidateExperience, CandidateEducation, CandidateSkill, CandidateResume
from schemas import (
    CandidateCreate, CandidateUpdate, CandidateSearchParams,
    ExperienceCreate, EducationCreate, SkillCreate
)
from database import get_elasticsearch
from config import settings

class CandidateService:
    def __init__(self, db: Session):
        self.db = db
        self.es = get_elasticsearch()
    
    def create_candidate(self, candidate_data: CandidateCreate, created_by: Optional[uuid.UUID] = None) -> Candidate:
        """Create a new candidate profile"""
        # Create main candidate record
        candidate_dict = candidate_data.dict(exclude={'experience', 'education', 'skills'})
        
        # Handle location data
        if candidate_data.location:
            location = candidate_data.location
            candidate_dict.update({
                'location_city': location.city,
                'location_state': location.state,
                'location_country': location.country,
                'location_coordinates_lat': location.coordinates.lat if location.coordinates else None,
                'location_coordinates_lng': location.coordinates.lng if location.coordinates else None,
            })
            del candidate_dict['location']
        
        candidate = Candidate(**candidate_dict, created_by=created_by)
        self.db.add(candidate)
        self.db.flush()  # Get the ID without committing
        
        # Add related records
        if candidate_data.experience:
            for exp_data in candidate_data.experience:
                experience = CandidateExperience(**exp_data.dict(), candidate_id=candidate.id)
                self.db.add(experience)
        
        if candidate_data.education:
            for edu_data in candidate_data.education:
                education = CandidateEducation(**edu_data.dict(), candidate_id=candidate.id)
                self.db.add(education)
        
        if candidate_data.skills:
            for skill_data in candidate_data.skills:
                skill = CandidateSkill(**skill_data.dict(), candidate_id=candidate.id)
                self.db.add(skill)
        
        # Calculate career metrics
        self._calculate_career_metrics(candidate)
        
        self.db.commit()
        self.db.refresh(candidate)
        
        # Index in Elasticsearch
        self._index_candidate_in_elasticsearch(candidate)
        
        return candidate
    
    def get_candidate(self, candidate_id: uuid.UUID) -> Optional[Candidate]:
        """Get candidate by ID"""
        return self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    def get_candidate_by_email(self, email: str) -> Optional[Candidate]:
        """Get candidate by email"""
        return self.db.query(Candidate).filter(Candidate.email == email).first()
    
    def update_candidate(self, candidate_id: uuid.UUID, candidate_data: CandidateUpdate) -> Optional[Candidate]:
        """Update existing candidate"""
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            return None
        
        update_data = candidate_data.dict(exclude_unset=True)
        
        # Handle location data
        if 'location' in update_data and update_data['location']:
            location = update_data['location']
            update_data.update({
                'location_city': location.get('city'),
                'location_state': location.get('state'),
                'location_country': location.get('country'),
                'location_coordinates_lat': location.get('coordinates', {}).get('lat'),
                'location_coordinates_lng': location.get('coordinates', {}).get('lng'),
            })
            del update_data['location']
        
        # Update fields
        for field, value in update_data.items():
            setattr(candidate, field, value)
        
        self.db.commit()
        self.db.refresh(candidate)
        
        # Update in Elasticsearch
        self._index_candidate_in_elasticsearch(candidate)
        
        return candidate
    
    def delete_candidate(self, candidate_id: uuid.UUID) -> bool:
        """Soft delete candidate (set status to inactive)"""
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            return False
        
        candidate.status = "inactive"
        self.db.commit()
        
        # Remove from Elasticsearch active index
        self._remove_candidate_from_elasticsearch(candidate_id)
        
        return True
    
    def search_candidates(self, search_params: CandidateSearchParams) -> Tuple[List[Candidate], int, Dict[str, Any]]:
        """Search candidates with advanced filters"""
        if search_params.q or search_params.skills:
            # Use Elasticsearch for complex search
            return self._search_candidates_elasticsearch(search_params)
        else:
            # Use database for simple queries
            return self._search_candidates_database(search_params)
    
    def _search_candidates_database(self, search_params: CandidateSearchParams) -> Tuple[List[Candidate], int, Dict[str, Any]]:
        """Search candidates using database queries"""
        query = self.db.query(Candidate)
        
        # Apply filters
        if search_params.status:
            query = query.filter(Candidate.status == search_params.status)
        
        if search_params.location:
            query = query.filter(
                or_(
                    Candidate.location_city.ilike(f"%{search_params.location}%"),
                    Candidate.location_state.ilike(f"%{search_params.location}%")
                )
            )
        
        if search_params.experience_min:
            query = query.filter(Candidate.total_years_experience >= search_params.experience_min)
        
        if search_params.experience_max:
            query = query.filter(Candidate.total_years_experience <= search_params.experience_max)
        
        if search_params.career_level:
            query = query.filter(Candidate.career_level == search_params.career_level)
        
        if search_params.company:
            # Join with experience table to filter by company
            query = query.join(CandidateExperience).filter(
                CandidateExperience.company.ilike(f"%{search_params.company}%")
            )
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if search_params.sort_by == "name":
            sort_column = Candidate.first_name
        elif search_params.sort_by == "experience":
            sort_column = Candidate.total_years_experience
        else:
            sort_column = Candidate.created_at
        
        if search_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.per_page
        candidates = query.offset(offset).limit(search_params.per_page).all()
        
        # Generate facets
        facets = self._generate_facets()
        
        return candidates, total, facets
    
    def _search_candidates_elasticsearch(self, search_params: CandidateSearchParams) -> Tuple[List[Candidate], int, Dict[str, Any]]:
        """Search candidates using Elasticsearch"""
        try:
            # Build Elasticsearch query
            query = {
                "query": {
                    "bool": {
                        "must": [],
                        "filter": [{"term": {"status": "active"}}]
                    }
                },
                "sort": [],
                "from": (search_params.page - 1) * search_params.per_page,
                "size": search_params.per_page,
                "highlight": {
                    "fields": {
                        "first_name": {},
                        "last_name": {},
                        "skills.name": {},
                        "experience.description": {}
                    }
                },
                "aggs": {
                    "skills": {
                        "nested": {"path": "skills"},
                        "aggs": {
                            "skill_names": {
                                "terms": {"field": "skills.name", "size": 20}
                            }
                        }
                    },
                    "experience_levels": {
                        "range": {
                            "field": "total_years_experience",
                            "ranges": [
                                {"key": "0-2", "from": 0, "to": 2},
                                {"key": "3-5", "from": 3, "to": 5},
                                {"key": "6-10", "from": 6, "to": 10},
                                {"key": "10+", "from": 11}
                            ]
                        }
                    }
                }
            }
            
            # Add search query
            if search_params.q:
                query["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": search_params.q,
                        "fields": [
                            "first_name^2", "last_name^2", "skills.name^3", 
                            "experience.company", "experience.position^2", 
                            "experience.description", "summary"
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })
            
            # Add skills filter
            if search_params.skills:
                skills_list = [skill.strip() for skill in search_params.skills.split(',')]
                query["query"]["bool"]["filter"].append({
                    "nested": {
                        "path": "skills",
                        "query": {
                            "terms": {"skills.name": skills_list}
                        }
                    }
                })
            
            # Add other filters
            if search_params.location:
                query["query"]["bool"]["filter"].append({
                    "multi_match": {
                        "query": search_params.location,
                        "fields": ["location.city", "location.state"]
                    }
                })
            
            if search_params.experience_min or search_params.experience_max:
                range_filter = {"range": {"total_years_experience": {}}}
                if search_params.experience_min:
                    range_filter["range"]["total_years_experience"]["gte"] = search_params.experience_min
                if search_params.experience_max:
                    range_filter["range"]["total_years_experience"]["lte"] = search_params.experience_max
                query["query"]["bool"]["filter"].append(range_filter)
            
            # Add sorting
            if search_params.sort_by == "relevance" and search_params.q:
                query["sort"].append({"_score": {"order": search_params.sort_order}})
            elif search_params.sort_by == "name":
                query["sort"].append({"first_name.keyword": {"order": search_params.sort_order}})
            elif search_params.sort_by == "experience":
                query["sort"].append({"total_years_experience": {"order": search_params.sort_order}})
            else:
                query["sort"].append({"created_at": {"order": search_params.sort_order}})
            
            # Execute search
            response = self.es.search(
                index=settings.elasticsearch_index,
                body=query,
                timeout=f"{settings.search_timeout}s"
            )
            
            # Extract candidate IDs
            candidate_ids = [hit["_id"] for hit in response["hits"]["hits"]]
            
            # Get candidates from database
            candidates = self.db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all()
            
            # Maintain order from Elasticsearch
            candidate_dict = {str(c.id): c for c in candidates}
            ordered_candidates = [candidate_dict[cid] for cid in candidate_ids if cid in candidate_dict]
            
            # Extract facets
            facets = {}
            if "aggregations" in response:
                aggs = response["aggregations"]
                if "skills" in aggs:
                    facets["skills"] = {
                        bucket["key"]: bucket["doc_count"] 
                        for bucket in aggs["skills"]["skill_names"]["buckets"]
                    }
                if "experience_levels" in aggs:
                    facets["experience_levels"] = {
                        bucket["key"]: bucket["doc_count"] 
                        for bucket in aggs["experience_levels"]["buckets"]
                    }
            
            total = response["hits"]["total"]["value"]
            return ordered_candidates, total, facets
            
        except Exception as e:
            print(f"Elasticsearch search failed: {e}")
            # Fallback to database search
            return self._search_candidates_database(search_params)
    
    def _calculate_career_metrics(self, candidate: Candidate):
        """Calculate career-related metrics for a candidate"""
        if candidate.experiences:
            # Calculate total years of experience
            total_months = 0
            for exp in candidate.experiences:
                if exp.start_date:
                    end_date = exp.end_date or datetime.utcnow()
                    months = (end_date.year - exp.start_date.year) * 12 + (end_date.month - exp.start_date.month)
                    total_months += max(0, months)
            
            candidate.total_years_experience = total_months // 12
            
            # Determine career level
            if candidate.total_years_experience >= 10:
                candidate.career_level = "executive"
            elif candidate.total_years_experience >= 5:
                candidate.career_level = "senior"
            elif candidate.total_years_experience >= 2:
                candidate.career_level = "mid"
            else:
                candidate.career_level = "entry"
    
    def _generate_facets(self) -> Dict[str, Any]:
        """Generate facets for search results"""
        # Top skills
        skills_query = self.db.query(
            CandidateSkill.name,
            func.count(CandidateSkill.id).label('count')
        ).join(Candidate).filter(
            Candidate.status == "active"
        ).group_by(CandidateSkill.name).order_by(desc('count')).limit(20)
        
        skills_facets = {skill[0]: skill[1] for skill in skills_query.all()}
        
        # Experience levels
        exp_levels = self.db.query(
            Candidate.career_level,
            func.count(Candidate.id).label('count')
        ).filter(
            Candidate.status == "active",
            Candidate.career_level.isnot(None)
        ).group_by(Candidate.career_level).all()
        
        exp_facets = {level[0]: level[1] for level in exp_levels}
        
        return {
            "skills": skills_facets,
            "experience_levels": exp_facets
        }
    
    def _index_candidate_in_elasticsearch(self, candidate: Candidate):
        """Index candidate in Elasticsearch"""
        try:
            # Prepare document
            doc = {
                "id": str(candidate.id),
                "first_name": candidate.first_name,
                "last_name": candidate.last_name,
                "full_name": f"{candidate.first_name} {candidate.last_name}",
                "email": candidate.email,
                "phone": candidate.phone,
                "location": {
                    "city": candidate.location_city,
                    "state": candidate.location_state,
                    "country": candidate.location_country,
                    "coordinates": {
                        "lat": candidate.location_coordinates_lat,
                        "lon": candidate.location_coordinates_lng
                    } if candidate.location_coordinates_lat and candidate.location_coordinates_lng else None
                },
                "total_years_experience": candidate.total_years_experience or 0,
                "career_level": candidate.career_level,
                "summary": candidate.summary,
                "status": candidate.status,
                "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
                "updated_at": candidate.updated_at.isoformat() if candidate.updated_at else None
            }
            
            # Add skills
            if candidate.skills:
                doc["skills"] = [
                    {
                        "name": skill.name,
                        "level": skill.level,
                        "years_experience": skill.years_experience or 0,
                        "category": skill.category
                    }
                    for skill in candidate.skills
                ]
            
            # Add experience
            if candidate.experiences:
                doc["experience"] = [
                    {
                        "company": exp.company,
                        "position": exp.position,
                        "start_date": exp.start_date.isoformat() if exp.start_date else None,
                        "end_date": exp.end_date.isoformat() if exp.end_date else None,
                        "current": exp.current,
                        "description": exp.description,
                        "skills": exp.skills_used or []
                    }
                    for exp in candidate.experiences
                ]
            
            # Add education
            if candidate.educations:
                doc["education"] = [
                    {
                        "institution": edu.institution,
                        "degree": edu.degree,
                        "field": edu.field,
                        "start_date": edu.start_date.isoformat() if edu.start_date else None,
                        "end_date": edu.end_date.isoformat() if edu.end_date else None,
                        "gpa": edu.gpa
                    }
                    for edu in candidate.educations
                ]
            
            # Index document
            self.es.index(
                index=settings.elasticsearch_index,
                id=str(candidate.id),
                document=doc
            )
            
        except Exception as e:
            print(f"Failed to index candidate in Elasticsearch: {e}")
    
    def _remove_candidate_from_elasticsearch(self, candidate_id: uuid.UUID):
        """Remove candidate from Elasticsearch index"""
        try:
            self.es.delete(index=settings.elasticsearch_index, id=str(candidate_id))
        except Exception as e:
            print(f"Failed to remove candidate from Elasticsearch: {e}")
    
    def get_candidate_stats(self) -> Dict[str, Any]:
        """Get candidate statistics"""
        # Get total candidates by status
        total_candidates = self.db.query(Candidate).count()
        active_candidates = self.db.query(Candidate).filter(Candidate.status == 'active').count()
        inactive_candidates = self.db.query(Candidate).filter(Candidate.status == 'inactive').count()
        
        # For now, return basic stats without job applications
        # TODO: Implement proper job application tracking
        return {
            "total": total_candidates,
            "active": active_candidates,
            "inactive": inactive_candidates,
            "hired": 0,  # Will be implemented when job applications are properly linked
            "rejected": 0  # Will be implemented when job applications are properly linked
        }

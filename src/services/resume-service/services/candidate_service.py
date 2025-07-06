from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import uuid
import hashlib
import os
import aiofiles
from datetime import datetime
import logging

from models import CandidateProfile, ResumeFile
from schemas import CandidateProfileCreate, CandidateProfileResponse
from services.resume_parser import ParsedResumeData
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class CandidateService:
    """Service for managing candidate profiles and resume files"""
    
    async def save_resume_file(self, db: AsyncSession, file) -> ResumeFile:
        """Save uploaded resume file to storage and database"""
        try:
            # Read file content
            content = await file.read()
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Check for duplicate
            existing = await db.execute(
                select(ResumeFile).where(ResumeFile.file_hash == file_hash)
            )
            if existing.scalar_one_or_none():
                raise ValueError("File already exists")
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file.filename)[1]
            filename = f"{file_id}{file_extension}"
            file_path = os.path.join(settings.upload_dir, filename)
            
            # Ensure upload directory exists
            os.makedirs(settings.upload_dir, exist_ok=True)
            
            # Save file to disk
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Create database record
            resume_file = ResumeFile(
                id=uuid.UUID(file_id),
                filename=filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=len(content),
                content_type=file.content_type,
                file_hash=file_hash,
                processing_status="pending"
            )
            
            db.add(resume_file)
            await db.commit()
            await db.refresh(resume_file)
            
            return resume_file
            
        except Exception as e:
            logger.error(f"Error saving resume file: {e}")
            await db.rollback()
            raise
    
    async def create_candidate_from_resume(
        self, 
        db: AsyncSession, 
        resume_id: str, 
        parsed_data: ParsedResumeData
    ) -> CandidateProfile:
        """Create candidate profile from parsed resume data"""
        try:
            # Check if candidate already exists by email
            email = parsed_data.personal_info.get('email')
            existing_candidate = None
            
            if email:
                result = await db.execute(
                    select(CandidateProfile).where(CandidateProfile.email == email)
                )
                existing_candidate = result.scalar_one_or_none()
            
            if existing_candidate:
                # Update existing candidate
                candidate = await self._update_candidate_from_parsed_data(
                    db, existing_candidate, parsed_data
                )
                
                # Link resume to existing candidate
                await db.execute(
                    update(ResumeFile)
                    .where(ResumeFile.id == uuid.UUID(resume_id))
                    .values(
                        candidate_id=candidate.id,
                        processing_status="completed",
                        processed_at=datetime.utcnow(),
                        raw_text=parsed_data.raw_text,
                        parsed_data=self._serialize_parsed_data(parsed_data)
                    )
                )
            else:
                # Create new candidate
                candidate = await self._create_new_candidate_from_parsed_data(
                    db, parsed_data
                )
                
                # Link resume to new candidate
                await db.execute(
                    update(ResumeFile)
                    .where(ResumeFile.id == uuid.UUID(resume_id))
                    .values(
                        candidate_id=candidate.id,
                        processing_status="completed",
                        processed_at=datetime.utcnow(),
                        raw_text=parsed_data.raw_text,
                        parsed_data=self._serialize_parsed_data(parsed_data)
                    )
                )
            
            await db.commit()
            await db.refresh(candidate)
            
            return candidate
            
        except Exception as e:
            logger.error(f"Error creating candidate from resume: {e}")
            await db.rollback()
            raise
    
    async def _create_new_candidate_from_parsed_data(
        self, 
        db: AsyncSession, 
        parsed_data: ParsedResumeData
    ) -> CandidateProfile:
        """Create new candidate profile from parsed data"""
        
        personal_info = parsed_data.personal_info
        
        candidate = CandidateProfile(
            first_name=personal_info.get('first_name'),
            last_name=personal_info.get('last_name'),
            email=personal_info.get('email'),
            phone=personal_info.get('phone'),
            linkedin_url=personal_info.get('linkedin_url'),
            portfolio_url=personal_info.get('portfolio_url'),
            summary=parsed_data.summary,
            experience=parsed_data.experience,
            education=parsed_data.education,
            skills=parsed_data.skills,
            total_years_experience=self._calculate_total_experience(parsed_data.experience),
            average_tenure=self._calculate_average_tenure(parsed_data.experience),
            career_progression_score=self._calculate_career_progression(parsed_data.experience),
            source="resume_upload",
            parsing_confidence=parsed_data.confidence_score,
            parsing_metadata=parsed_data.metadata
        )
        
        db.add(candidate)
        return candidate
    
    async def _update_candidate_from_parsed_data(
        self, 
        db: AsyncSession, 
        candidate: CandidateProfile,
        parsed_data: ParsedResumeData
    ) -> CandidateProfile:
        """Update existing candidate with new parsed data"""
        
        personal_info = parsed_data.personal_info
        
        # Update fields that might have changed
        if personal_info.get('phone') and not candidate.phone:
            candidate.phone = personal_info.get('phone')
        
        if personal_info.get('linkedin_url') and not candidate.linkedin_url:
            candidate.linkedin_url = personal_info.get('linkedin_url')
        
        if personal_info.get('portfolio_url') and not candidate.portfolio_url:
            candidate.portfolio_url = personal_info.get('portfolio_url')
        
        # Merge experience and education
        candidate.experience = self._merge_experience(candidate.experience, parsed_data.experience)
        candidate.education = self._merge_education(candidate.education, parsed_data.education)
        candidate.skills = self._merge_skills(candidate.skills, parsed_data.skills)
        
        # Recalculate metrics
        candidate.total_years_experience = self._calculate_total_experience(candidate.experience)
        candidate.average_tenure = self._calculate_average_tenure(candidate.experience)
        candidate.career_progression_score = self._calculate_career_progression(candidate.experience)
        
        candidate.updated_at = datetime.utcnow()
        
        return candidate
    
    async def create_candidate(
        self, 
        db: AsyncSession, 
        candidate_data: CandidateProfileCreate
    ) -> CandidateProfile:
        """Create candidate profile manually"""
        try:
            # Check for existing email
            if candidate_data.email:
                result = await db.execute(
                    select(CandidateProfile).where(CandidateProfile.email == candidate_data.email)
                )
                if result.scalar_one_or_none():
                    raise ValueError("Candidate with this email already exists")
            
            candidate = CandidateProfile(
                first_name=candidate_data.first_name,
                last_name=candidate_data.last_name,
                email=candidate_data.email,
                phone=candidate_data.phone,
                location=candidate_data.location.dict() if candidate_data.location else None,
                linkedin_url=candidate_data.linkedin_url,
                portfolio_url=candidate_data.portfolio_url,
                summary=candidate_data.summary,
                experience=[exp.dict() for exp in candidate_data.experience],
                education=[edu.dict() for edu in candidate_data.education],
                skills=candidate_data.skills.dict() if candidate_data.skills else None,
                source=candidate_data.source or "manual",
                source_details=candidate_data.source_details,
                total_years_experience=self._calculate_total_experience([exp.dict() for exp in candidate_data.experience]),
                average_tenure=self._calculate_average_tenure([exp.dict() for exp in candidate_data.experience]),
                career_progression_score=self._calculate_career_progression([exp.dict() for exp in candidate_data.experience])
            )
            
            db.add(candidate)
            await db.commit()
            await db.refresh(candidate)
            
            return candidate
            
        except Exception as e:
            logger.error(f"Error creating candidate: {e}")
            await db.rollback()
            raise
    
    async def get_candidate(self, db: AsyncSession, candidate_id: str) -> Optional[CandidateProfile]:
        """Get candidate by ID"""
        result = await db.execute(
            select(CandidateProfile)
            .options(selectinload(CandidateProfile.resumes))
            .where(CandidateProfile.id == uuid.UUID(candidate_id))
        )
        return result.scalar_one_or_none()
    
    async def list_candidates(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[CandidateProfile]:
        """List candidates with pagination"""
        result = await db.execute(
            select(CandidateProfile)
            .offset(skip)
            .limit(limit)
            .order_by(CandidateProfile.created_at.desc())
        )
        return result.scalars().all()
    
    async def update_candidate(
        self, 
        db: AsyncSession, 
        candidate_id: str,
        candidate_data: CandidateProfileCreate
    ) -> Optional[CandidateProfile]:
        """Update candidate profile"""
        try:
            candidate = await self.get_candidate(db, candidate_id)
            if not candidate:
                return None
            
            # Update fields
            candidate.first_name = candidate_data.first_name
            candidate.last_name = candidate_data.last_name
            candidate.email = candidate_data.email
            candidate.phone = candidate_data.phone
            candidate.location = candidate_data.location.dict() if candidate_data.location else None
            candidate.linkedin_url = candidate_data.linkedin_url
            candidate.portfolio_url = candidate_data.portfolio_url
            candidate.summary = candidate_data.summary
            candidate.experience = [exp.dict() for exp in candidate_data.experience]
            candidate.education = [edu.dict() for edu in candidate_data.education]
            candidate.skills = candidate_data.skills.dict() if candidate_data.skills else None
            candidate.updated_at = datetime.utcnow()
            
            # Recalculate metrics
            candidate.total_years_experience = self._calculate_total_experience(candidate.experience)
            candidate.average_tenure = self._calculate_average_tenure(candidate.experience)
            candidate.career_progression_score = self._calculate_career_progression(candidate.experience)
            
            await db.commit()
            await db.refresh(candidate)
            
            return candidate
            
        except Exception as e:
            logger.error(f"Error updating candidate: {e}")
            await db.rollback()
            raise
    
    async def delete_candidate(self, db: AsyncSession, candidate_id: str) -> bool:
        """Delete candidate profile"""
        try:
            result = await db.execute(
                delete(CandidateProfile).where(CandidateProfile.id == uuid.UUID(candidate_id))
            )
            await db.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting candidate: {e}")
            await db.rollback()
            raise
    
    def _serialize_parsed_data(self, parsed_data: ParsedResumeData) -> Dict[str, Any]:
        """Serialize parsed data for JSON storage"""
        return {
            'personal_info': parsed_data.personal_info,
            'experience': parsed_data.experience,
            'education': parsed_data.education,
            'skills': parsed_data.skills,
            'summary': parsed_data.summary,
            'confidence_score': parsed_data.confidence_score,
            'metadata': parsed_data.metadata
        }
    
    def _calculate_total_experience(self, experience_list: List[Dict]) -> float:
        """Calculate total years of experience"""
        # Simplified calculation - in reality would need proper date parsing
        return len(experience_list) * 2.0  # Assume 2 years per job on average
    
    def _calculate_average_tenure(self, experience_list: List[Dict]) -> float:
        """Calculate average job tenure"""
        if not experience_list:
            return 0.0
        return 2.0  # Simplified - assume 2 years average tenure
    
    def _calculate_career_progression(self, experience_list: List[Dict]) -> float:
        """Calculate career progression score"""
        if not experience_list:
            return 0.0
        return min(len(experience_list) * 0.2, 1.0)  # More jobs = better progression
    
    def _merge_experience(self, existing: List[Dict], new: List[Dict]) -> List[Dict]:
        """Merge experience lists, avoiding duplicates"""
        merged = list(existing) if existing else []
        
        for new_exp in new:
            # Simple duplicate detection by company and position
            is_duplicate = any(
                exp.get('company', '').lower() == new_exp.get('company', '').lower() and
                exp.get('position', '').lower() == new_exp.get('position', '').lower()
                for exp in merged
            )
            
            if not is_duplicate:
                merged.append(new_exp)
        
        return merged
    
    def _merge_education(self, existing: List[Dict], new: List[Dict]) -> List[Dict]:
        """Merge education lists, avoiding duplicates"""
        merged = list(existing) if existing else []
        
        for new_edu in new:
            # Simple duplicate detection by institution and degree
            is_duplicate = any(
                edu.get('institution', '').lower() == new_edu.get('institution', '').lower() and
                edu.get('degree', '').lower() == new_edu.get('degree', '').lower()
                for edu in merged
            )
            
            if not is_duplicate:
                merged.append(new_edu)
        
        return merged
    
    def _merge_skills(self, existing: Dict, new: Dict) -> Dict:
        """Merge skills dictionaries"""
        if not existing:
            return new
        
        merged = existing.copy()
        
        # Merge technical skills
        if new.get('technical'):
            existing_tech = {skill['name'].lower(): skill for skill in merged.get('technical', [])}
            for new_skill in new['technical']:
                existing_tech[new_skill['name'].lower()] = new_skill
            merged['technical'] = list(existing_tech.values())
        
        # Merge soft skills
        if new.get('soft'):
            existing_soft = set(skill.lower() for skill in merged.get('soft', []))
            new_soft = [skill for skill in new['soft'] if skill.lower() not in existing_soft]
            merged['soft'] = merged.get('soft', []) + new_soft
        
        # Merge certifications
        if new.get('certifications'):
            existing_certs = {cert['name'].lower(): cert for cert in merged.get('certifications', [])}
            for new_cert in new['certifications']:
                existing_certs[new_cert['name'].lower()] = new_cert
            merged['certifications'] = list(existing_certs.values())
        
        return merged

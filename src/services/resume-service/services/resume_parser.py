import spacy
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import PyPDF2
from docx import Document
import magic
import io
import logging
from dataclasses import dataclass
from transformers import pipeline
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

@dataclass
class ParsedResumeData:
    """Container for parsed resume data"""
    personal_info: Dict[str, Any]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: Dict[str, Any]
    summary: str
    confidence_score: float
    raw_text: str
    metadata: Dict[str, Any]

class ResumeParserService:
    """AI-powered resume parsing service"""
    
    def __init__(self):
        self.nlp = None
        self.skill_extractor = None
        self._load_models()
    
    def _load_models(self):
        """Load NLP models"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model successfully")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
    
    async def parse_resume(self, file) -> ParsedResumeData:
        """Parse resume file and extract structured data"""
        try:
            # Extract text from file
            raw_text = await self._extract_text_from_file(file)
            
            if not raw_text.strip():
                raise ValueError("No text content found in file")
            
            # Parse with NLP
            doc = self.nlp(raw_text) if self.nlp else None
            
            # Extract different sections
            personal_info = self._extract_personal_info(raw_text, doc)
            experience = self._extract_experience(raw_text, doc)
            education = self._extract_education(raw_text, doc)
            skills = self._extract_skills(raw_text, doc)
            summary = self._extract_summary(raw_text, doc)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                personal_info, experience, education, skills
            )
            
            metadata = {
                "file_type": file.content_type,
                "original_filename": file.filename,
                "text_length": len(raw_text),
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
            return ParsedResumeData(
                personal_info=personal_info,
                experience=experience,
                education=education,
                skills=skills,
                summary=summary,
                confidence_score=confidence_score,
                raw_text=raw_text,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            raise
    
    async def _extract_text_from_file(self, file) -> str:
        """Extract text content from uploaded file"""
        content = await file.read()
        
        if file.content_type == "application/pdf":
            return self._extract_text_from_pdf(content)
        elif file.content_type in [
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]:
            return self._extract_text_from_docx(content)
        elif file.content_type == "text/plain":
            return content.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file.content_type}")
    
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(io.BytesIO(content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return ""
    
    def _extract_personal_info(self, text: str, doc=None) -> Dict[str, Any]:
        """Extract personal information"""
        personal_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            personal_info['email'] = emails[0]
        
        # Phone extraction
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            personal_info['phone'] = ''.join(phones[0])
        
        # LinkedIn URL extraction
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            personal_info['linkedin_url'] = f"https://{linkedin_matches[0]}"
        
        # Name extraction (basic heuristic)
        lines = text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            if len(line.split()) == 2 and line.replace(' ', '').isalpha():
                parts = line.split()
                personal_info['first_name'] = parts[0]
                personal_info['last_name'] = parts[1]
                break
        
        return personal_info
    
    def _extract_experience(self, text: str, doc=None) -> List[Dict[str, Any]]:
        """Extract work experience"""
        experience = []
        
        # Simple pattern matching for experience sections
        exp_patterns = [
            r'(?i)(experience|work history|employment history|professional experience)',
            r'(?i)(work experience|career history|professional background)'
        ]
        
        for pattern in exp_patterns:
            matches = re.search(pattern, text)
            if matches:
                # Extract experience section (simplified)
                start_idx = matches.end()
                # Look for next major section
                next_section = re.search(r'(?i)(education|skills|projects)', text[start_idx:])
                end_idx = next_section.start() + start_idx if next_section else len(text)
                
                exp_text = text[start_idx:end_idx]
                
                # Extract individual experiences (basic implementation)
                job_entries = self._parse_job_entries(exp_text)
                experience.extend(job_entries)
                break
        
        return experience
    
    def _parse_job_entries(self, exp_text: str) -> List[Dict[str, Any]]:
        """Parse individual job entries from experience text"""
        jobs = []
        
        # Split by common delimiters for job entries
        potential_jobs = re.split(r'\n(?=\S)', exp_text)
        
        for job_text in potential_jobs:
            if len(job_text.strip()) < 20:  # Skip short entries
                continue
                
            job = {}
            lines = [line.strip() for line in job_text.split('\n') if line.strip()]
            
            if lines:
                # First line often contains company and position
                first_line = lines[0]
                
                # Try to extract company and position
                if ' at ' in first_line:
                    parts = first_line.split(' at ')
                    job['position'] = parts[0].strip()
                    job['company'] = parts[1].strip()
                elif ' - ' in first_line:
                    parts = first_line.split(' - ')
                    job['position'] = parts[0].strip()
                    job['company'] = parts[1].strip() if len(parts) > 1 else ""
                else:
                    job['position'] = first_line
                
                # Extract dates (simplified)
                date_pattern = r'(\d{4}|\d{1,2}/\d{4}|\w+ \d{4})'
                dates = re.findall(date_pattern, job_text)
                if len(dates) >= 2:
                    job['start_date'] = dates[0]
                    job['end_date'] = dates[1]
                elif len(dates) == 1:
                    job['start_date'] = dates[0]
                
                # Description is remaining text
                if len(lines) > 1:
                    job['description'] = '\n'.join(lines[1:])
                
                jobs.append(job)
        
        return jobs
    
    def _extract_education(self, text: str, doc=None) -> List[Dict[str, Any]]:
        """Extract education information"""
        education = []
        
        # Find education section
        edu_pattern = r'(?i)(education|academic background|qualifications)'
        match = re.search(edu_pattern, text)
        
        if match:
            start_idx = match.end()
            # Look for next major section
            next_section = re.search(r'(?i)(experience|skills|projects)', text[start_idx:])
            end_idx = next_section.start() + start_idx if next_section else len(text)
            
            edu_text = text[start_idx:end_idx]
            
            # Extract degree information (simplified)
            degree_patterns = [
                r'(?i)(bachelor|master|phd|doctorate|associate)',
                r'(?i)(b\.?s\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?)'
            ]
            
            for pattern in degree_patterns:
                matches = re.finditer(pattern, edu_text)
                for match in matches:
                    # Extract surrounding context for each degree
                    start = max(0, match.start() - 100)
                    end = min(len(edu_text), match.end() + 100)
                    context = edu_text[start:end]
                    
                    edu_entry = {
                        'degree': match.group(),
                        'description': context.strip()
                    }
                    
                    # Try to extract institution
                    university_pattern = r'(?i)(university|college|institute|school)'
                    uni_match = re.search(university_pattern, context)
                    if uni_match:
                        # Extract institution name (simplified)
                        lines = context.split('\n')
                        for line in lines:
                            if university_pattern in line.lower():
                                edu_entry['institution'] = line.strip()
                                break
                    
                    education.append(edu_entry)
        
        return education
    
    def _extract_skills(self, text: str, doc=None) -> Dict[str, Any]:
        """Extract skills information"""
        skills = {
            'technical': [],
            'soft': [],
            'certifications': []
        }
        
        # Common technical skills
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'postgresql',
            'mongodb', 'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux',
            'machine learning', 'data science', 'artificial intelligence'
        ]
        
        text_lower = text.lower()
        for skill in tech_skills:
            if skill in text_lower:
                skills['technical'].append({
                    'name': skill,
                    'level': 'intermediate'  # Default level
                })
        
        # Extract certifications
        cert_patterns = [
            r'(?i)(certified|certification)',
            r'(?i)(aws|azure|google cloud|gcp)',
            r'(?i)(pmp|cissp|cisa|cism)'
        ]
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                context = text[max(0, match.start()-50):match.end()+50]
                skills['certifications'].append({
                    'name': match.group(),
                    'context': context.strip()
                })
        
        return skills
    
    def _extract_summary(self, text: str, doc=None) -> str:
        """Extract or generate professional summary"""
        # Look for summary section
        summary_patterns = [
            r'(?i)(summary|profile|objective|about)',
            r'(?i)(professional summary|career objective)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text)
            if match:
                start_idx = match.end()
                # Get next few lines as summary
                lines = text[start_idx:].split('\n')[:5]
                summary_text = ' '.join([line.strip() for line in lines if line.strip()])
                if len(summary_text) > 50:  # Reasonable summary length
                    return summary_text[:500]  # Limit to 500 chars
        
        # If no summary section found, use first paragraph
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if len(para.strip()) > 100:
                return para.strip()[:500]
        
        return ""
    
    def _calculate_confidence_score(self, personal_info: Dict, experience: List, 
                                   education: List, skills: Dict) -> float:
        """Calculate parsing confidence score"""
        score = 0.0
        
        # Personal info scoring
        if personal_info.get('email'):
            score += 0.3
        if personal_info.get('phone'):
            score += 0.2
        if personal_info.get('first_name') and personal_info.get('last_name'):
            score += 0.2
        
        # Experience scoring
        if experience:
            score += 0.2
            if any(exp.get('company') and exp.get('position') for exp in experience):
                score += 0.1
        
        # Education scoring
        if education:
            score += 0.1
        
        # Skills scoring
        if skills.get('technical'):
            score += 0.1
        
        return min(score, 1.0)

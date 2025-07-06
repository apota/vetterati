# Resume Management Design

## Overview
This document outlines the design for the resume management subsystem, including resume collection, parsing, and candidate database management with AI-powered data extraction.

## Architecture

### Resume Processing Pipeline
```
Resume Upload → File Validation → Storage → AI Parsing → Data Extraction → Database Storage → Search Indexing
```

### Components

#### 1. Resume Collection Service
- **Multi-Channel Intake**: Web portal, email, API integrations
- **File Format Support**: PDF, DOC, DOCX, TXT, HTML
- **Integration Points**: LinkedIn, Indeed, ZipRecruiter, Glassdoor
- **Bulk Upload**: CSV/Excel candidate data import

#### 2. Resume Parsing Engine
- **AI/ML Models**: Custom NLP models with pre-trained embeddings
- **OCR Integration**: Tesseract for scanned documents
- **Multiple Parsers**: Primary + fallback parsing strategies
- **Quality Scoring**: Confidence metrics for extracted data

#### 3. Candidate Database
- **Search Engine**: Elasticsearch for full-text search
- **Data Storage**: PostgreSQL for structured data
- **File Storage**: AWS S3 or Azure Blob Storage
- **Caching Layer**: Redis for frequently accessed profiles

## Data Models

### Candidate Profile
```json
{
  "id": "uuid",
  "personalInfo": {
    "firstName": "string",
    "lastName": "string",
    "email": "string",
    "phone": "string",
    "location": {
      "city": "string",
      "state": "string",
      "country": "string",
      "coordinates": "object"
    },
    "linkedInUrl": "string",
    "portfolioUrl": "string"
  },
  "experience": [
    {
      "company": "string",
      "position": "string",
      "startDate": "date",
      "endDate": "date",
      "description": "string",
      "skills": ["string"],
      "achievements": ["string"],
      "companySize": "startup|small|medium|large|enterprise",
      "industry": "string"
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "field": "string",
      "startDate": "date",
      "endDate": "date",
      "gpa": "number",
      "honors": ["string"],
      "prestige": "number"
    }
  ],
  "skills": {
    "technical": [
      {
        "name": "string",
        "level": "beginner|intermediate|advanced|expert",
        "yearsOfExperience": "number",
        "lastUsed": "date"
      }
    ],
    "soft": ["string"],
    "certifications": [
      {
        "name": "string",
        "issuer": "string",
        "dateObtained": "date",
        "expiryDate": "date",
        "verificationUrl": "string"
      }
    ]
  },
  "careerMetrics": {
    "totalYearsExperience": "number",
    "averageTenure": "number",
    "careerProgression": "linear|exponential|lateral|declining",
    "leadershipExperience": "boolean",
    "managementYears": "number",
    "teamSizesManaged": ["number"],
    "careerPattern": "big_fish_little_pond|little_fish_big_pond|consistent"
  },
  "resumeMetadata": {
    "originalFileName": "string",
    "fileSize": "number",
    "uploadDate": "timestamp",
    "source": "web|email|integration|bulk_import",
    "parsingConfidence": "number",
    "lastUpdated": "timestamp",
    "versions": ["object"]
  }
}
```

### Resume File Entity
```json
{
  "id": "uuid",
  "candidateId": "uuid",
  "fileName": "string",
  "fileType": "string",
  "fileSize": "number",
  "storagePath": "string",
  "uploadSource": "string",
  "uploadDate": "timestamp",
  "processingStatus": "pending|processing|completed|failed",
  "parsingResults": "object",
  "qualityScore": "number"
}
```

## Resume Parsing Implementation

### AI/NLP Pipeline

#### 1. Document Processing
```python
class DocumentProcessor:
    def process(self, file_path):
        # Text extraction
        text = self.extract_text(file_path)
        
        # Text cleaning and normalization
        cleaned_text = self.clean_text(text)
        
        # Section detection
        sections = self.detect_sections(cleaned_text)
        
        # Named entity recognition
        entities = self.extract_entities(sections)
        
        return ParsedDocument(text, sections, entities)
```

#### 2. Information Extraction Models
- **Contact Information**: Regex + NER for email, phone, address
- **Work Experience**: Date parsing, company recognition, role extraction
- **Education**: Institution matching, degree classification
- **Skills**: Technical skill taxonomy, soft skill identification
- **Achievements**: Quantifiable accomplishment extraction

#### 3. Career Pattern Analysis
```python
class CareerAnalyzer:
    def analyze_pattern(self, work_history):
        tenure_analysis = self.calculate_tenure_metrics(work_history)
        progression_analysis = self.analyze_career_progression(work_history)
        company_analysis = self.analyze_company_types(work_history)
        
        return {
            "pattern": self.classify_pattern(company_analysis),
            "progression": progression_analysis,
            "stability": tenure_analysis
        }
```

## Search and Indexing

### Elasticsearch Schema
```json
{
  "mappings": {
    "properties": {
      "personalInfo": {
        "properties": {
          "name": {"type": "text", "analyzer": "standard"},
          "email": {"type": "keyword"},
          "location": {"type": "geo_point"}
        }
      },
      "skills": {
        "type": "nested",
        "properties": {
          "name": {"type": "keyword"},
          "level": {"type": "keyword"},
          "yearsOfExperience": {"type": "integer"}
        }
      },
      "experience": {
        "type": "nested",
        "properties": {
          "company": {"type": "text"},
          "position": {"type": "text"},
          "skills": {"type": "keyword"},
          "duration": {"type": "integer"}
        }
      },
      "fullText": {"type": "text", "analyzer": "english"}
    }
  }
}
```

### Search Features
- **Full-text Search**: Natural language queries across all fields
- **Faceted Search**: Filter by skills, location, experience level
- **Semantic Search**: Vector similarity using sentence embeddings
- **Boolean Search**: Complex AND/OR/NOT queries
- **Fuzzy Matching**: Handle typos and variations in skill names

## File Storage Architecture

### Storage Strategy
- **Hot Storage**: Recently uploaded resumes (S3 Standard)
- **Warm Storage**: Older resumes (S3 IA)
- **Cold Storage**: Archive resumes (S3 Glacier)
- **CDN**: CloudFront for resume preview/download

### File Organization
```
/resumes/
  /{year}/
    /{month}/
      /{candidate_id}/
        /original_{timestamp}.pdf
        /parsed_{timestamp}.json
        /preview_{timestamp}.png
```

## Integration Capabilities

### Email Integration
```python
class EmailResumeProcessor:
    def process_email(self, email):
        attachments = self.extract_attachments(email)
        candidate_info = self.parse_email_signature(email)
        
        for attachment in attachments:
            if self.is_resume(attachment):
                self.process_resume(attachment, candidate_info)
```

### Job Board APIs
- **LinkedIn**: LinkedIn Talent Solutions API
- **Indeed**: Indeed Apply integration
- **ZipRecruiter**: Partner API integration
- **Glassdoor**: Job board connector

### Third-party Parsing Services
- **Backup Parsers**: Sovren, HireAbility, RChilli
- **Quality Comparison**: Cross-validation between parsers
- **Fallback Strategy**: Cascade to backup if primary fails

## Data Quality and Validation

### Parsing Quality Metrics
```python
class QualityAssessment:
    def assess_quality(self, parsed_resume):
        scores = {
            "contact_completeness": self.check_contact_info(parsed_resume),
            "experience_detail": self.check_experience_depth(parsed_resume),
            "education_accuracy": self.validate_education(parsed_resume),
            "skills_relevance": self.assess_skill_extraction(parsed_resume),
            "date_consistency": self.validate_dates(parsed_resume)
        }
        return self.calculate_composite_score(scores)
```

### Data Validation Rules
- **Date Validation**: Chronological order, reasonable ranges
- **Contact Validation**: Email format, phone number format
- **Geographic Validation**: City/state/country consistency
- **Company Validation**: Known company database lookup
- **Skill Validation**: Standard skill taxonomy mapping

## Performance Optimization

### Parsing Performance
- **Async Processing**: Queue-based resume processing
- **Batch Processing**: Bulk resume parsing
- **Caching**: Frequently accessed parsing results
- **CDN**: Global distribution of resume files

### Database Optimization
- **Indexing Strategy**: Composite indexes for search queries
- **Partitioning**: Time-based partitioning for resume data
- **Read Replicas**: Separate read/write database instances
- **Connection Pooling**: Efficient database connections

## Security and Privacy

### Data Protection
- **PII Encryption**: Encrypt sensitive personal information
- **Access Logging**: Track all resume access and downloads
- **Retention Policies**: Automated data lifecycle management
- **Anonymization**: Remove PII for analytics and ML training

### Compliance
- **GDPR**: Right to be forgotten, data portability
- **CCPA**: Data deletion and access rights
- **SOX**: Audit trails for financial services companies
- **Industry Standards**: Sector-specific compliance requirements

## Monitoring and Analytics

### Processing Metrics
- **Parsing Success Rate**: Percentage of successfully parsed resumes
- **Processing Time**: Average time per resume processing
- **Quality Scores**: Distribution of parsing quality metrics
- **Error Rates**: Failed parsing categorization

### Usage Analytics
- **Search Patterns**: Most common search queries and filters
- **Resume Views**: Tracking of resume access patterns
- **Download Metrics**: Resume download frequency and patterns
- **User Behavior**: Recruiter interaction with parsed data

## API Design

### Resume Upload Endpoint
```http
POST /api/v1/resumes/upload
Content-Type: multipart/form-data

{
  "file": "binary",
  "source": "web|email|integration",
  "jobId": "uuid",
  "metadata": "object"
}
```

### Candidate Search Endpoint
```http
GET /api/v1/candidates/search
Query Parameters:
  - q: search query
  - skills: comma-separated skills
  - location: geographic filter
  - experience: years range
  - education: degree level
  - page: pagination
  - size: results per page
```

### Bulk Import Endpoint
```http
POST /api/v1/resumes/bulk-import
Content-Type: application/json

{
  "candidates": [
    {
      "resume_url": "string",
      "metadata": "object"
    }
  ],
  "job_id": "uuid",
  "source": "string"
}
```

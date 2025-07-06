from elasticsearch import AsyncElasticsearch
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from schemas import CandidateSearchRequest, CandidateSearchResponse, CandidateSearchHit
from models import CandidateProfile
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SearchService:
    """Elasticsearch-based candidate search service"""
    
    def __init__(self):
        self.es_client = None
        self.index_name = settings.elasticsearch_index
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Elasticsearch client"""
        try:
            self.es_client = AsyncElasticsearch([settings.elasticsearch_url])
            logger.info("Elasticsearch client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {e}")
    
    async def create_index_if_not_exists(self):
        """Create Elasticsearch index with proper mapping"""
        if not self.es_client:
            return
        
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "first_name": {"type": "text", "analyzer": "standard"},
                    "last_name": {"type": "text", "analyzer": "standard"},
                    "email": {"type": "keyword"},
                    "phone": {"type": "keyword"},
                    "location": {
                        "properties": {
                            "city": {"type": "text"},
                            "state": {"type": "text"},
                            "country": {"type": "text"},
                            "coordinates": {"type": "geo_point"}
                        }
                    },
                    "summary": {"type": "text", "analyzer": "standard"},
                    "experience": {
                        "type": "nested",
                        "properties": {
                            "company": {"type": "text", "analyzer": "standard"},
                            "position": {"type": "text", "analyzer": "standard"},
                            "description": {"type": "text", "analyzer": "standard"},
                            "skills": {"type": "keyword"},
                            "start_date": {"type": "date", "format": "yyyy-MM-dd||yyyy"},
                            "end_date": {"type": "date", "format": "yyyy-MM-dd||yyyy"}
                        }
                    },
                    "education": {
                        "type": "nested",
                        "properties": {
                            "institution": {"type": "text", "analyzer": "standard"},
                            "degree": {"type": "text", "analyzer": "standard"},
                            "field": {"type": "text", "analyzer": "standard"}
                        }
                    },
                    "skills": {
                        "properties": {
                            "technical": {
                                "type": "nested",
                                "properties": {
                                    "name": {"type": "keyword"},
                                    "level": {"type": "keyword"},
                                    "years_of_experience": {"type": "float"}
                                }
                            },
                            "soft": {"type": "keyword"},
                            "certifications": {
                                "type": "nested",
                                "properties": {
                                    "name": {"type": "keyword"},
                                    "issuer": {"type": "keyword"}
                                }
                            }
                        }
                    },
                    "total_years_experience": {"type": "float"},
                    "average_tenure": {"type": "float"},
                    "career_progression_score": {"type": "float"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }
        
        try:
            exists = await self.es_client.indices.exists(index=self.index_name)
            if not exists:
                await self.es_client.indices.create(index=self.index_name, body=mapping)
                logger.info(f"Created Elasticsearch index: {self.index_name}")
        except Exception as e:
            logger.error(f"Error creating Elasticsearch index: {e}")
    
    async def index_candidate(self, candidate: CandidateProfile):
        """Index a candidate profile in Elasticsearch"""
        if not self.es_client:
            return
        
        try:
            await self.create_index_if_not_exists()
            
            # Prepare document for indexing
            doc = {
                "id": str(candidate.id),
                "first_name": candidate.first_name,
                "last_name": candidate.last_name,
                "email": candidate.email,
                "phone": candidate.phone,
                "location": candidate.location,
                "summary": candidate.summary,
                "experience": candidate.experience or [],
                "education": candidate.education or [],
                "skills": candidate.skills or {},
                "total_years_experience": candidate.total_years_experience,
                "average_tenure": candidate.average_tenure,
                "career_progression_score": candidate.career_progression_score,
                "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
                "updated_at": candidate.updated_at.isoformat() if candidate.updated_at else None
            }
            
            await self.es_client.index(
                index=self.index_name,
                id=str(candidate.id),
                body=doc
            )
            
            logger.info(f"Indexed candidate {candidate.id} in Elasticsearch")
            
        except Exception as e:
            logger.error(f"Error indexing candidate {candidate.id}: {e}")
    
    async def remove_candidate(self, candidate_id: str):
        """Remove candidate from Elasticsearch index"""
        if not self.es_client:
            return
        
        try:
            await self.es_client.delete(
                index=self.index_name,
                id=candidate_id,
                ignore=[404]
            )
            logger.info(f"Removed candidate {candidate_id} from Elasticsearch")
        except Exception as e:
            logger.error(f"Error removing candidate {candidate_id}: {e}")
    
    async def search_candidates(self, search_request: CandidateSearchRequest) -> CandidateSearchResponse:
        """Search candidates using Elasticsearch"""
        if not self.es_client:
            return CandidateSearchResponse(
                candidates=[], total=0, page=search_request.page, 
                size=search_request.size, pages=0
            )
        
        try:
            query = self._build_search_query(search_request)
            
            from_offset = (search_request.page - 1) * search_request.size
            
            response = await self.es_client.search(
                index=self.index_name,
                body={
                    "query": query,
                    "from": from_offset,
                    "size": search_request.size,
                    "sort": [
                        {"_score": {"order": "desc"}},
                        {"updated_at": {"order": "desc"}}
                    ]
                }
            )
            
            hits = response["hits"]["hits"]
            total = response["hits"]["total"]["value"]
            pages = (total + search_request.size - 1) // search_request.size
            
            candidates = []
            for hit in hits:
                source = hit["_source"]
                candidate_hit = CandidateSearchHit(
                    id=source["id"],
                    first_name=source.get("first_name"),
                    last_name=source.get("last_name"),
                    email=source.get("email"),
                    summary=source.get("summary"),
                    location=source.get("location"),
                    total_years_experience=source.get("total_years_experience"),
                    skills=source.get("skills"),
                    score=hit["_score"]
                )
                candidates.append(candidate_hit)
            
            return CandidateSearchResponse(
                candidates=candidates,
                total=total,
                page=search_request.page,
                size=search_request.size,
                pages=pages
            )
            
        except Exception as e:
            logger.error(f"Error searching candidates: {e}")
            return CandidateSearchResponse(
                candidates=[], total=0, page=search_request.page, 
                size=search_request.size, pages=0
            )
    
    def _build_search_query(self, search_request: CandidateSearchRequest) -> Dict[str, Any]:
        """Build Elasticsearch query from search request"""
        must_queries = []
        filter_queries = []
        
        # Text search across multiple fields
        if search_request.query:
            must_queries.append({
                "multi_match": {
                    "query": search_request.query,
                    "fields": [
                        "first_name^2",
                        "last_name^2", 
                        "summary^1.5",
                        "experience.company",
                        "experience.position^1.5",
                        "experience.description",
                        "education.institution",
                        "education.degree",
                        "skills.technical.name^2"
                    ],
                    "type": "best_fields"
                }
            })
        
        # Skills filter
        if search_request.skills:
            skills_should = []
            for skill in search_request.skills:
                skills_should.extend([
                    {"nested": {
                        "path": "skills.technical",
                        "query": {"term": {"skills.technical.name": skill.lower()}}
                    }},
                    {"nested": {
                        "path": "experience",
                        "query": {"match": {"experience.skills": skill}}
                    }}
                ])
            
            must_queries.append({
                "bool": {"should": skills_should, "minimum_should_match": 1}
            })
        
        # Experience years filter
        if search_request.experience_years_min is not None or search_request.experience_years_max is not None:
            range_filter = {}
            if search_request.experience_years_min is not None:
                range_filter["gte"] = search_request.experience_years_min
            if search_request.experience_years_max is not None:
                range_filter["lte"] = search_request.experience_years_max
            
            filter_queries.append({
                "range": {"total_years_experience": range_filter}
            })
        
        # Location filter
        if search_request.location:
            filter_queries.append({
                "bool": {
                    "should": [
                        {"match": {"location.city": search_request.location}},
                        {"match": {"location.state": search_request.location}},
                        {"match": {"location.country": search_request.location}}
                    ],
                    "minimum_should_match": 1
                }
            })
        
        # Company filter
        if search_request.company:
            must_queries.append({
                "nested": {
                    "path": "experience",
                    "query": {"match": {"experience.company": search_request.company}}
                }
            })
        
        # Position filter
        if search_request.position:
            must_queries.append({
                "nested": {
                    "path": "experience",
                    "query": {"match": {"experience.position": search_request.position}}
                }
            })
        
        # Education level filter
        if search_request.education_level:
            must_queries.append({
                "nested": {
                    "path": "education",
                    "query": {"match": {"education.degree": search_request.education_level}}
                }
            })
        
        # Build final query
        if not must_queries and not filter_queries:
            return {"match_all": {}}
        
        query = {"bool": {}}
        
        if must_queries:
            query["bool"]["must"] = must_queries
        
        if filter_queries:
            query["bool"]["filter"] = filter_queries
        
        return query

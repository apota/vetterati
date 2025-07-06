# AHP-Based Candidate Matching Design

## Overview
This document outlines the design for the Analytic Hierarchy Process (AHP) based candidate matching system, including multi-profile matching, weighted scoring, and explainable AI components.

## Architecture

### AHP Matching Pipeline
```
Job Requirements → AHP Hierarchy → Pairwise Comparisons → Weight Calculation → Candidate Scoring → Ranking → Explanation
```

### Core Components

#### 1. AHP Calculation Engine
- **Matrix Operations**: Eigenvalue/eigenvector calculations
- **Consistency Checking**: Consistency ratio validation
- **Weight Derivation**: Priority vector computation
- **Sensitivity Analysis**: Impact assessment of weight changes

#### 2. Ideal Candidate Profile Manager
- **Profile Builder**: Visual hierarchy construction
- **Template Library**: Pre-built AHP structures for common roles
- **Comparison Interface**: Pairwise comparison matrix UI
- **Validation Engine**: Consistency ratio monitoring

#### 3. Matching Engine
- **Multi-Profile Scoring**: Simultaneous evaluation against multiple ideals
- **Composite Score Calculation**: Weighted combination of profile scores
- **Explanation Generator**: Detailed score breakdown and reasoning
- **Real-time Updates**: Dynamic recalculation as criteria change

## Data Models

### AHP Hierarchy Structure
```json
{
  "id": "uuid",
  "jobId": "uuid",
  "name": "string",
  "description": "string",
  "hierarchy": {
    "goal": {
      "name": "Best Candidate for Position",
      "criteria": [
        {
          "id": "technical_experience",
          "name": "Technical Experience",
          "weight": 0.4,
          "subcriteria": [
            {
              "id": "years_programming",
              "name": "Years of Programming",
              "weight": 0.6,
              "type": "numeric",
              "range": {"min": 0, "max": 20}
            },
            {
              "id": "tech_stack_match",
              "name": "Technology Stack Match",
              "weight": 0.3,
              "type": "categorical",
              "values": ["exact", "similar", "transferable", "none"]
            }
          ]
        }
      ]
    }
  },
  "pairwiseMatrices": {
    "root": [[1, 2, 5, 3], [0.5, 1, 3, 2], [0.2, 0.33, 1, 0.5], [0.33, 0.5, 2, 1]],
    "technical_experience": [[1, 2, 6], [0.5, 1, 3], [0.17, 0.33, 1]]
  },
  "consistencyRatios": {
    "root": 0.08,
    "technical_experience": 0.05
  },
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### Ideal Candidate Profile
```json
{
  "id": "uuid",
  "jobId": "uuid",
  "ahpHierarchyId": "uuid",
  "name": "string",
  "archetype": "tech_lead|ic_expert|generalist|specialist",
  "weight": 100,
  "targetValues": {
    "years_programming": 8,
    "tech_stack_match": "exact",
    "leadership_experience": 5,
    "education_level": "bachelors",
    "company_types": ["startup", "scale_up"],
    "career_pattern": "big_fish_little_pond"
  },
  "tolerances": {
    "years_programming": {"min": 6, "max": 12},
    "leadership_experience": {"min": 3, "max": 10}
  },
  "description": "string",
  "isActive": true,
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### Candidate Match Result
```json
{
  "id": "uuid",
  "candidateId": "uuid",
  "jobId": "uuid",
  "calculatedAt": "timestamp",
  "overallScore": 84.5,
  "profileMatches": [
    {
      "idealProfileId": "uuid",
      "profileName": "Tech Lead Archetype",
      "profileWeight": 100,
      "rawScore": 84.5,
      "weightedScore": 84.5,
      "attributeScores": [
        {
          "criteriaId": "technical_experience",
          "criteriaName": "Technical Experience",
          "criteriaWeight": 0.4,
          "score": 85,
          "weightedContribution": 34,
          "subcriteria": [
            {
              "id": "years_programming",
              "name": "Years of Programming",
              "weight": 0.6,
              "candidateValue": 7,
              "idealValue": 8,
              "score": 87.5,
              "contribution": 21
            }
          ]
        }
      ]
    }
  ],
  "explanation": {
    "topStrengths": ["Technical depth", "Leadership experience"],
    "improvementAreas": ["Education credentials", "Enterprise experience"],
    "overallFit": "Excellent match with strong technical background",
    "recommendations": ["Consider for senior technical roles"]
  },
  "metadata": {
    "ahpVersion": "1.2",
    "calculationTime": 150,
    "confidenceLevel": 0.92
  }
}
```

## AHP Mathematical Implementation

### Priority Vector Calculation
```python
class AHPCalculator:
    def calculate_priority_vector(self, pairwise_matrix):
        """
        Calculate priority vector using eigenvalue method
        """
        eigenvalues, eigenvectors = np.linalg.eig(pairwise_matrix)
        max_eigenvalue_index = np.argmax(eigenvalues.real)
        principal_eigenvector = eigenvectors[:, max_eigenvalue_index].real
        
        # Normalize to sum to 1
        priority_vector = principal_eigenvector / np.sum(principal_eigenvector)
        return priority_vector
    
    def calculate_consistency_ratio(self, pairwise_matrix):
        """
        Calculate consistency ratio for matrix validation
        """
        n = len(pairwise_matrix)
        eigenvalues, _ = np.linalg.eig(pairwise_matrix)
        lambda_max = np.max(eigenvalues.real)
        
        consistency_index = (lambda_max - n) / (n - 1)
        random_index = self.get_random_index(n)
        
        consistency_ratio = consistency_index / random_index
        return consistency_ratio
    
    def get_random_index(self, n):
        """Random index values for different matrix sizes"""
        ri_values = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
        return ri_values.get(n, 1.40)
```

### Scoring Algorithm
```python
class CandidateScorer:
    def score_candidate(self, candidate, ideal_profile, ahp_hierarchy):
        """
        Score candidate against ideal profile using AHP weights
        """
        total_score = 0
        attribute_scores = []
        
        for criteria in ahp_hierarchy.criteria:
            criteria_score = self.score_criteria(
                candidate, 
                ideal_profile, 
                criteria
            )
            
            weighted_score = criteria_score * criteria.weight
            total_score += weighted_score
            
            attribute_scores.append({
                'criteria': criteria.name,
                'score': criteria_score,
                'weight': criteria.weight,
                'contribution': weighted_score
            })
        
        return {
            'total_score': total_score,
            'attribute_scores': attribute_scores
        }
    
    def score_criteria(self, candidate, ideal_profile, criteria):
        """
        Score individual criteria with subcriteria handling
        """
        if criteria.subcriteria:
            return self.score_composite_criteria(candidate, ideal_profile, criteria)
        else:
            return self.score_atomic_criteria(candidate, ideal_profile, criteria)
```

## Pairwise Comparison Interface

### Matrix Builder Component
```typescript
interface PairwiseComparisonMatrix {
  criteria: Criterion[];
  comparisons: number[][];
  consistencyRatio: number;
  isValid: boolean;
}

class PairwiseMatrixBuilder {
  generateMatrix(criteria: Criterion[]): PairwiseComparisonMatrix {
    const n = criteria.length;
    const matrix = Array(n).fill(null).map(() => Array(n).fill(1));
    
    // Initialize diagonal to 1
    for (let i = 0; i < n; i++) {
      matrix[i][i] = 1;
    }
    
    return {
      criteria,
      comparisons: matrix,
      consistencyRatio: 0,
      isValid: false
    };
  }
  
  updateComparison(matrix: number[][], i: number, j: number, value: number): number[][] {
    const updated = [...matrix];
    updated[i][j] = value;
    updated[j][i] = 1 / value; // Reciprocal relationship
    
    return updated;
  }
  
  validateConsistency(matrix: number[][]): boolean {
    const cr = this.calculateConsistencyRatio(matrix);
    return cr <= 0.10; // 10% threshold for acceptable consistency
  }
}
```

### UI Components
```tsx
const PairwiseComparisonForm: React.FC<Props> = ({ criteria, onMatrixUpdate }) => {
  return (
    <div className="pairwise-matrix">
      <h3>Pairwise Comparisons</h3>
      <p>Compare the relative importance of each criterion pair</p>
      
      <div className="comparison-grid">
        {criteria.map((criterionA, i) =>
          criteria.slice(i + 1).map((criterionB, j) => (
            <ComparisonSlider
              key={`${i}-${i + j + 1}`}
              criterionA={criterionA}
              criterionB={criterionB}
              value={matrix[i][i + j + 1]}
              onChange={(value) => updateMatrix(i, i + j + 1, value)}
            />
          ))
        )}
      </div>
      
      <ConsistencyIndicator ratio={consistencyRatio} />
    </div>
  );
};
```

## Career Pattern Recognition

### Pattern Classification Engine
```python
class CareerPatternAnalyzer:
    def classify_pattern(self, work_history):
        """
        Classify candidate into career patterns
        """
        company_sizes = self.extract_company_sizes(work_history)
        role_levels = self.extract_role_levels(work_history)
        industry_diversity = self.calculate_industry_diversity(work_history)
        
        if self.is_big_fish_little_pond(company_sizes, role_levels):
            return "big_fish_little_pond"
        elif self.is_little_fish_big_pond(company_sizes, role_levels):
            return "little_fish_big_pond"
        else:
            return "consistent_growth"
    
    def adjust_weights_for_pattern(self, base_weights, pattern):
        """
        Adjust AHP weights based on career pattern
        """
        adjustments = {
            "big_fish_little_pond": {
                "leadership_weight": 1.2,
                "scope_weight": 1.15,
                "process_weight": 0.8
            },
            "little_fish_big_pond": {
                "process_weight": 1.25,
                "scale_weight": 1.3,
                "leadership_weight": 0.85
            }
        }
        
        pattern_adjustments = adjustments.get(pattern, {})
        return self.apply_weight_adjustments(base_weights, pattern_adjustments)
```

## Explainable AI Components

### Explanation Generator
```python
class MatchExplainer:
    def generate_explanation(self, match_result, candidate, ideal_profile):
        """
        Generate human-readable explanation for match score
        """
        explanation = {
            "overall_assessment": self.assess_overall_fit(match_result.overall_score),
            "key_strengths": self.identify_strengths(match_result.attribute_scores),
            "improvement_areas": self.identify_gaps(match_result.attribute_scores),
            "specific_recommendations": self.generate_recommendations(
                candidate, ideal_profile, match_result
            ),
            "score_breakdown": self.create_score_breakdown(match_result),
            "confidence_indicators": self.assess_confidence(match_result)
        }
        
        return explanation
    
    def create_score_breakdown(self, match_result):
        """
        Create visual score breakdown showing contribution of each factor
        """
        breakdown = []
        for attr_score in match_result.attribute_scores:
            breakdown.append({
                "attribute": attr_score.criteria_name,
                "score": attr_score.score,
                "weight": attr_score.criteria_weight,
                "contribution": attr_score.weighted_contribution,
                "impact": self.categorize_impact(attr_score.weighted_contribution),
                "explanation": self.explain_attribute_score(attr_score)
            })
        
        return sorted(breakdown, key=lambda x: x["contribution"], reverse=True)
```

### Visualization Components
```typescript
interface ScoreVisualization {
  radarChart: RadarChartData;
  contributionChart: ContributionChartData;
  sensitivityAnalysis: SensitivityData;
}

const MatchExplanationDashboard: React.FC<Props> = ({ matchResult }) => {
  return (
    <div className="explanation-dashboard">
      <div className="score-overview">
        <h3>Overall Match: {matchResult.overallScore}%</h3>
        <ConfidenceIndicator level={matchResult.confidenceLevel} />
      </div>
      
      <div className="score-breakdown">
        <RadarChart data={createRadarData(matchResult)} />
        <ContributionChart data={createContributionData(matchResult)} />
      </div>
      
      <div className="detailed-analysis">
        <StrengthsPanel strengths={matchResult.explanation.topStrengths} />
        <ImprovementAreasPanel areas={matchResult.explanation.improvementAreas} />
        <RecommendationsPanel recommendations={matchResult.explanation.recommendations} />
      </div>
      
      <div className="sensitivity-analysis">
        <SensitivityChart data={generateSensitivityData(matchResult)} />
      </div>
    </div>
  );
};
```

## Performance Optimization

### Caching Strategy
```python
class AHPCacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = 3600  # 1 hour
    
    def cache_ahp_weights(self, hierarchy_id, weights):
        """Cache calculated AHP weights"""
        key = f"ahp_weights:{hierarchy_id}"
        self.redis.setex(key, self.cache_ttl, json.dumps(weights))
    
    def cache_candidate_scores(self, candidate_id, job_id, scores):
        """Cache candidate scoring results"""
        key = f"candidate_scores:{candidate_id}:{job_id}"
        self.redis.setex(key, self.cache_ttl, json.dumps(scores))
    
    def invalidate_job_cache(self, job_id):
        """Invalidate all cached results for a job"""
        pattern = f"*{job_id}"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
```

### Batch Processing
```python
class BatchScoringEngine:
    def score_candidates_batch(self, candidate_ids, job_id):
        """
        Score multiple candidates in batch for efficiency
        """
        job_config = self.load_job_configuration(job_id)
        candidates = self.load_candidates_batch(candidate_ids)
        
        # Pre-calculate AHP weights once
        ahp_weights = self.calculate_ahp_weights(job_config.ahp_hierarchy)
        
        results = []
        for candidate in candidates:
            score_result = self.score_single_candidate(
                candidate, 
                job_config.ideal_profiles, 
                ahp_weights
            )
            results.append(score_result)
        
        # Bulk insert results
        self.bulk_insert_scores(results)
        
        return results
```

## Real-time Updates

### WebSocket Integration
```typescript
class RealTimeAHPUpdates {
  private ws: WebSocket;
  
  constructor(private jobId: string) {
    this.ws = new WebSocket(`wss://api.ats.com/jobs/${jobId}/ahp-updates`);
    this.setupEventHandlers();
  }
  
  private setupEventHandlers() {
    this.ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      
      switch (update.type) {
        case 'HIERARCHY_UPDATED':
          this.handleHierarchyUpdate(update.data);
          break;
        case 'SCORES_RECALCULATED':
          this.handleScoreUpdate(update.data);
          break;
        case 'NEW_CANDIDATE_SCORED':
          this.handleNewCandidateScore(update.data);
          break;
      }
    };
  }
  
  updateAHPWeights(hierarchyId: string, newWeights: object) {
    this.ws.send(JSON.stringify({
      type: 'UPDATE_AHP_WEIGHTS',
      hierarchyId,
      weights: newWeights
    }));
  }
}
```

## Quality Assurance

### AHP Validation
```python
class AHPValidator:
    def validate_hierarchy(self, hierarchy):
        """Validate AHP hierarchy structure and mathematics"""
        validations = [
            self.validate_hierarchy_structure(hierarchy),
            self.validate_pairwise_matrices(hierarchy),
            self.validate_consistency_ratios(hierarchy),
            self.validate_weight_derivation(hierarchy)
        ]
        
        return all(validations)
    
    def validate_consistency_ratios(self, hierarchy):
        """Ensure all consistency ratios are within acceptable limits"""
        for matrix_id, cr in hierarchy.consistency_ratios.items():
            if cr > 0.10:  # 10% threshold
                raise ValidationError(f"Consistency ratio {cr} exceeds threshold for {matrix_id}")
        
        return True
    
    def validate_score_calculation(self, candidate, ideal_profile, result):
        """Validate that scores are calculated correctly"""
        recalculated = self.recalculate_score(candidate, ideal_profile)
        
        if abs(recalculated.total_score - result.total_score) > 0.01:
            raise ValidationError("Score calculation mismatch detected")
        
        return True
```

## API Endpoints

### AHP Management
```http
POST /api/v1/jobs/{jobId}/ahp-hierarchy
Content-Type: application/json

{
  "name": "Senior Developer Hierarchy",
  "criteria": [...],
  "pairwise_matrices": {...}
}

GET /api/v1/jobs/{jobId}/ahp-hierarchy/{hierarchyId}

PUT /api/v1/jobs/{jobId}/ahp-hierarchy/{hierarchyId}/weights

POST /api/v1/jobs/{jobId}/ideal-profiles
{
  "name": "Tech Lead Archetype",
  "ahp_hierarchy_id": "uuid",
  "target_values": {...},
  "weight": 100
}
```

### Candidate Scoring
```http
POST /api/v1/candidates/{candidateId}/score
{
  "job_id": "uuid",
  "force_recalculate": false
}

GET /api/v1/jobs/{jobId}/candidate-rankings
Query Parameters:
  - sort_by: overall_score|profile_match
  - min_score: number
  - ideal_profile_id: uuid
  - page: number
  - size: number

GET /api/v1/candidates/{candidateId}/match-explanation/{jobId}
```

### Batch Operations
```http
POST /api/v1/jobs/{jobId}/score-candidates
{
  "candidate_ids": ["uuid1", "uuid2", ...],
  "options": {
    "include_explanation": true,
    "async": false
  }
}
```

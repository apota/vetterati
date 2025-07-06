from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class ReportType(str, Enum):
    HIRING_METRICS = "hiring_metrics"
    DIVERSITY_REPORT = "diversity_report"
    AHP_PERFORMANCE = "ahp_performance"
    TIME_TO_HIRE = "time_to_hire"
    CANDIDATE_FUNNEL = "candidate_funnel"
    CUSTOM = "custom"

class MetricType(str, Enum):
    HIRING = "hiring"
    DIVERSITY = "diversity"
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    QUALITY = "quality"

# Base schemas
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Metrics response schemas
class HiringMetric(BaseModel):
    metric_name: str
    value: float
    period_start: datetime
    period_end: datetime
    change_percentage: Optional[float] = None
    trend: Optional[str] = None  # up, down, stable

class HiringMetricsResponse(BaseResponse):
    total_applications: int
    total_hires: int
    hire_rate: float
    avg_time_to_hire: float
    cost_per_hire: Optional[float] = None
    quality_of_hire: Optional[float] = None
    metrics_by_department: List[Dict[str, Any]]
    metrics_by_job_level: List[Dict[str, Any]]
    time_series_data: List[HiringMetric]

class DiversityMetric(BaseModel):
    dimension: str
    category: str
    total_candidates: int
    hired_count: int
    percentage: float
    target_percentage: Optional[float] = None
    variance: Optional[float] = None

class DiversityReportResponse(BaseResponse):
    overall_diversity_score: float
    diversity_by_department: List[Dict[str, Any]]
    diversity_trends: List[Dict[str, Any]]
    metrics: List[DiversityMetric]
    recommendations: List[str]

class AhpPerformanceResponse(BaseResponse):
    total_predictions: int
    successful_hires: int
    accuracy_rate: float
    precision_score: float
    recall_score: float
    f1_score: float
    avg_prediction_confidence: float
    performance_by_job: List[Dict[str, Any]]
    model_drift_indicators: List[Dict[str, Any]]

class MetricsDashboardResponse(BaseResponse):
    active_job_postings: int
    total_applications_this_month: int
    interviews_scheduled: int
    offers_extended: int
    hires_this_month: int
    avg_time_to_hire: float
    top_performing_sources: List[Dict[str, Any]]
    hiring_velocity: List[Dict[str, Any]]
    diversity_summary: Dict[str, Any]
    ahp_performance_summary: Dict[str, Any]

# Request schemas
class CustomReportRequest(BaseModel):
    report_name: str
    report_type: ReportType
    date_range: Dict[str, datetime]
    filters: Dict[str, Any] = {}
    groupby_fields: List[str] = []
    metrics: List[str] = []
    export_format: str = Field(default="json", regex="^(json|csv|excel|pdf)$")
    include_charts: bool = False

class CustomReportResponse(BaseResponse):
    report_id: str
    report_name: str
    data: List[Dict[str, Any]]
    summary_statistics: Dict[str, Any]
    charts: Optional[List[Dict[str, Any]]] = None
    export_url: Optional[str] = None

# Predictive analytics schemas
class SuccessPrediction(BaseModel):
    candidate_id: str
    job_id: str
    success_probability: float
    confidence_interval: Dict[str, float]
    key_factors: List[Dict[str, Any]]
    risk_factors: List[str]

class HiringTrend(BaseModel):
    period: str
    predicted_hires: int
    confidence_level: float
    seasonal_factors: List[str]

class PredictiveAnalyticsResponse(BaseResponse):
    forecast_period: str
    hiring_trends: List[HiringTrend]
    demand_predictions: List[Dict[str, Any]]
    skill_gap_analysis: List[Dict[str, Any]]
    market_insights: List[str]

# Export schemas
class ExportRequest(BaseModel):
    format: str = Field(regex="^(csv|excel|pdf)$")
    data_type: str
    filters: Dict[str, Any] = {}
    date_range: Optional[Dict[str, datetime]] = None

class ExportResponse(BaseResponse):
    file_url: str
    file_size: int
    expires_at: datetime

# Real-time analytics schemas
class RealTimeMetric(BaseModel):
    metric_name: str
    current_value: Union[int, float, str]
    previous_value: Optional[Union[int, float, str]] = None
    change_percentage: Optional[float] = None
    last_updated: datetime

class InterviewSchedule(BaseModel):
    interview_id: str
    candidate_name: str
    job_title: str
    interviewer: str
    scheduled_time: datetime
    type: str  # phone, video, in_person
    status: str

# Report template schemas
class ReportTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    report_type: ReportType
    template_config: Dict[str, Any]
    is_public: bool = False

class ReportTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    report_type: ReportType
    template_config: Dict[str, Any]
    is_public: bool
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Data quality schemas
class DataQualityMetric(BaseModel):
    table_name: str
    column_name: Optional[str] = None
    metric_type: str
    metric_value: float
    threshold_value: Optional[float] = None
    is_passing: bool
    details: Optional[Dict[str, Any]] = None
    measured_at: datetime

class DataQualityReport(BaseResponse):
    overall_score: float
    passing_metrics: int
    failing_metrics: int
    metrics: List[DataQualityMetric]
    recommendations: List[str]

# Analytics configuration schemas
class AnalyticsConfig(BaseModel):
    metric_refresh_interval: int = 300  # seconds
    batch_processing_size: int = 1000
    data_retention_days: int = 365
    cache_ttl: int = 300
    max_concurrent_reports: int = 5

class AlertRule(BaseModel):
    metric_name: str
    condition: str  # >, <, =, !=
    threshold: float
    severity: str = Field(regex="^(low|medium|high|critical)$")
    notification_channels: List[str]
    is_enabled: bool = True

class AlertRuleResponse(BaseModel):
    id: int
    alert_rule: AlertRule
    created_at: datetime
    triggered_count: int
    last_triggered: Optional[datetime] = None

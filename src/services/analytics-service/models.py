from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
from typing import Optional, Dict, Any

class AnalyticsMetric(Base):
    """Store various analytics metrics"""
    __tablename__ = "analytics_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # hiring, diversity, performance, etc.
    value = Column(Numeric(10, 2), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    dimensions = Column(JSON)  # Store additional dimensions like department, job_level, etc.
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class HiringFunnel(Base):
    """Track candidates through hiring funnel"""
    __tablename__ = "hiring_funnel"
    
    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(String(36), ForeignKey("job_postings.id"), nullable=False)
    stage = Column(String(50), nullable=False)  # applied, screened, interviewed, offered, hired
    candidate_count = Column(Integer, nullable=False)
    conversion_rate = Column(Numeric(5, 2))  # Percentage
    avg_days_in_stage = Column(Numeric(10, 2))
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

class DiversityMetric(Base):
    """Track diversity metrics across different dimensions"""
    __tablename__ = "diversity_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    dimension = Column(String(50), nullable=False)  # gender, ethnicity, age_group, etc.
    category = Column(String(100), nullable=False)
    department = Column(String(100))
    job_level = Column(String(50))
    total_candidates = Column(Integer, nullable=False)
    hired_count = Column(Integer, nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

class AhpPerformanceMetric(Base):
    """Track AHP model performance metrics"""
    __tablename__ = "ahp_performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(String(36), ForeignKey("job_postings.id"), nullable=False)
    total_predictions = Column(Integer, nullable=False)
    successful_hires = Column(Integer, nullable=False)
    accuracy_rate = Column(Numeric(5, 2), nullable=False)
    precision_score = Column(Numeric(5, 2))
    recall_score = Column(Numeric(5, 2))
    f1_score = Column(Numeric(5, 2))
    avg_prediction_confidence = Column(Numeric(5, 2))
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

class TimeToHireMetric(Base):
    """Track time-to-hire metrics"""
    __tablename__ = "time_to_hire_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(String(36), ForeignKey("job_postings.id"), nullable=False)
    department = Column(String(100))
    job_level = Column(String(50))
    avg_time_to_hire_days = Column(Numeric(10, 2), nullable=False)
    median_time_to_hire_days = Column(Numeric(10, 2), nullable=False)
    min_time_to_hire_days = Column(Integer, nullable=False)
    max_time_to_hire_days = Column(Integer, nullable=False)
    total_hires = Column(Integer, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

class PredictiveModel(Base):
    """Store predictive model metadata and performance"""
    __tablename__ = "predictive_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # success_prediction, trend_analysis, etc.
    version = Column(String(20), nullable=False)
    model_path = Column(String(500))  # Path to saved model
    training_data_size = Column(Integer, nullable=False)
    accuracy_score = Column(Numeric(5, 2))
    precision_score = Column(Numeric(5, 2))
    recall_score = Column(Numeric(5, 2))
    f1_score = Column(Numeric(5, 2))
    is_active = Column(Boolean, default=False)
    hyperparameters = Column(JSON)
    feature_importance = Column(JSON)
    trained_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

class ReportTemplate(Base):
    """Store custom report templates"""
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    report_type = Column(String(50), nullable=False)
    template_config = Column(JSON, nullable=False)  # Report configuration
    is_public = Column(Boolean, default=False)
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class GeneratedReport(Base):
    """Track generated reports"""
    __tablename__ = "generated_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)
    parameters = Column(JSON)  # Report parameters used
    file_path = Column(String(500))
    file_format = Column(String(20))  # csv, excel, pdf
    file_size_bytes = Column(Integer)
    generated_by = Column(String(36), ForeignKey("users.id"))
    generated_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)  # When the file should be cleaned up
    download_count = Column(Integer, default=0)

class DataQualityMetric(Base):
    """Track data quality metrics"""
    __tablename__ = "data_quality_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)
    column_name = Column(String(100))
    metric_type = Column(String(50), nullable=False)  # completeness, accuracy, consistency
    metric_value = Column(Numeric(10, 4), nullable=False)
    threshold_value = Column(Numeric(10, 4))
    is_passing = Column(Boolean, nullable=False)
    details = Column(JSON)  # Additional details about the metric
    measured_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

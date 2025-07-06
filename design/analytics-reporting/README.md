# Analytics & Reporting Design

## Overview
This document outlines the design for the analytics and reporting subsystem, including hiring metrics, AHP model performance tracking, compliance reporting, and real-time dashboards.

## Architecture

### Analytics Pipeline
```
Data Collection → ETL Processing → Data Warehouse → Analytics Engine → Visualization → Reports
```

### Core Components

#### 1. Data Collection Service
- **Event Streaming**: Real-time event capture from all system components
- **Batch Processing**: Historical data processing and aggregation
- **Data Validation**: Quality checks and anomaly detection
- **Schema Evolution**: Backward-compatible data model changes

#### 2. Analytics Engine
- **OLAP Cube**: Multi-dimensional data analysis
- **Statistical Analysis**: Correlation, regression, trend analysis
- **Machine Learning**: Predictive analytics and pattern recognition
- **Real-time Processing**: Streaming analytics for live dashboards

#### 3. Reporting Service
- **Dashboard Engine**: Interactive visualization platform
- **Report Generator**: Automated report creation and distribution
- **Export Service**: Data export in multiple formats
- **Compliance Engine**: Regulatory reporting automation

## Data Models

### Analytics Event Schema
```json
{
  "event_id": "uuid",
  "event_type": "candidate_scored|interview_scheduled|hire_completed|workflow_advanced",
  "timestamp": "timestamp",
  "session_id": "uuid",
  "user_id": "uuid",
  "entity_type": "candidate|job|interview|workflow",
  "entity_id": "uuid",
  "action": "create|update|delete|view|score",
  "context": {
    "job_id": "uuid",
    "candidate_id": "uuid",
    "workflow_stage": "string",
    "ahp_hierarchy_id": "uuid",
    "ip_address": "string",
    "user_agent": "string"
  },
  "payload": {
    "before": "object",
    "after": "object",
    "metadata": "object"
  },
  "compliance_flags": {
    "contains_pii": true,
    "requires_audit": true,
    "retention_category": "hiring_data"
  }
}
```

### Hiring Metrics Aggregate
```json
{
  "id": "uuid",
  "period_type": "daily|weekly|monthly|quarterly",
  "period_start": "date",
  "period_end": "date",
  "job_id": "uuid",
  "department": "string",
  "location": "string",
  "metrics": {
    "applications_received": 125,
    "candidates_screened": 45,
    "interviews_conducted": 23,
    "offers_made": 3,
    "hires_completed": 2,
    "time_to_hire": {
      "avg_days": 28.5,
      "median_days": 25,
      "p90_days": 45,
      "p95_days": 52
    },
    "time_to_fill": {
      "avg_days": 35.2,
      "median_days": 32,
      "p90_days": 58,
      "p95_days": 67
    },
    "cost_per_hire": {
      "avg_cost": 3250.00,
      "total_cost": 6500.00,
      "breakdown": {
        "recruiter_time": 2400.00,
        "job_board_costs": 800.00,
        "interview_costs": 300.00
      }
    },
    "source_effectiveness": {
      "job_boards": {"applications": 80, "hires": 1},
      "referrals": {"applications": 30, "hires": 1},
      "direct": {"applications": 15, "hires": 0}
    },
    "conversion_rates": {
      "application_to_screen": 0.36,
      "screen_to_interview": 0.51,
      "interview_to_offer": 0.13,
      "offer_to_hire": 0.67
    }
  },
  "diversity_metrics": {
    "gender_distribution": {
      "male": 0.62,
      "female": 0.35,
      "non_binary": 0.02,
      "not_disclosed": 0.01
    },
    "ethnicity_distribution": {
      "white": 0.48,
      "asian": 0.25,
      "hispanic": 0.15,
      "black": 0.08,
      "other": 0.04
    },
    "hiring_rate_by_group": {
      "gender": {"male": 0.18, "female": 0.22},
      "ethnicity": {"underrepresented": 0.19, "non_underrepresented": 0.17}
    }
  },
  "calculated_at": "timestamp",
  "data_quality_score": 0.96
}
```

### AHP Model Performance
```json
{
  "id": "uuid",
  "ahp_hierarchy_id": "uuid",
  "job_id": "uuid",
  "evaluation_period": {
    "start_date": "date",
    "end_date": "date"
  },
  "model_metrics": {
    "total_candidates_scored": 156,
    "hires_made": 4,
    "prediction_accuracy": {
      "score_vs_performance": 0.73,
      "ranking_accuracy": 0.81,
      "top_10_precision": 0.89
    },
    "attribute_importance": {
      "technical_experience": {
        "ahp_weight": 0.40,
        "actual_importance": 0.35,
        "correlation_with_success": 0.68
      },
      "leadership_experience": {
        "ahp_weight": 0.30,
        "actual_importance": 0.38,
        "correlation_with_success": 0.72
      }
    },
    "ideal_profile_effectiveness": [
      {
        "profile_id": "uuid",
        "profile_name": "Tech Lead Archetype",
        "candidates_matched": 45,
        "hires_from_profile": 2,
        "success_rate": 0.044,
        "avg_performance_score": 4.2
      }
    ],
    "consistency_metrics": {
      "avg_consistency_ratio": 0.07,
      "matrices_above_threshold": 0.02,
      "decision_coherence_score": 0.92
    }
  },
  "recommendations": {
    "weight_adjustments": [
      {
        "attribute": "technical_experience",
        "current_weight": 0.40,
        "suggested_weight": 0.35,
        "confidence": 0.82,
        "reasoning": "Lower correlation with actual performance than expected"
      }
    ],
    "hierarchy_improvements": [
      "Consider adding 'adaptability' as a separate criterion",
      "Reduce granularity in education subcriteria"
    ]
  },
  "calculated_at": "timestamp"
}
```

### Compliance Report
```json
{
  "id": "uuid",
  "report_type": "eeoc|gdpr|ccpa|audit_trail",
  "period_start": "date",
  "period_end": "date",
  "organization_id": "uuid",
  "generated_at": "timestamp",
  "generated_by": "user_id",
  "data": {
    "eeoc_report": {
      "job_categories": [
        {
          "category": "Software Engineer",
          "total_applications": 500,
          "demographic_breakdown": {
            "race_ethnicity": {
              "hispanic_latino": {"applications": 75, "hires": 3},
              "white": {"applications": 250, "hires": 8},
              "black_african_american": {"applications": 50, "hires": 2},
              "asian": {"applications": 100, "hires": 4},
              "native_american": {"applications": 10, "hires": 0},
              "pacific_islander": {"applications": 5, "hires": 0},
              "two_or_more": {"applications": 10, "hires": 1}
            },
            "gender": {
              "male": {"applications": 300, "hires": 12},
              "female": {"applications": 180, "hires": 6},
              "not_disclosed": {"applications": 20, "hires": 0}
            }
          },
          "adverse_impact_analysis": {
            "selection_rate_by_race": {
              "white": 0.032,
              "hispanic_latino": 0.040,
              "black_african_american": 0.040,
              "asian": 0.040
            },
            "four_fifths_rule_compliance": true,
            "statistical_significance": 0.23
          }
        }
      ]
    },
    "gdpr_compliance": {
      "data_subject_requests": {
        "access_requests": 12,
        "deletion_requests": 8,
        "portability_requests": 3,
        "rectification_requests": 2
      },
      "processing_lawful_basis": {
        "consent": 234,
        "contract": 456,
        "legitimate_interest": 123
      },
      "data_retention_compliance": {
        "records_due_for_deletion": 45,
        "records_deleted": 42,
        "compliance_rate": 0.933
      }
    }
  },
  "certification": {
    "certified_by": "user_id",
    "certification_date": "timestamp",
    "digital_signature": "signature_hash",
    "compliance_attestation": true
  }
}
```

## Analytics Implementation

### Real-time Analytics Engine
```python
class RealTimeAnalyticsEngine:
    def __init__(self):
        self.kafka_consumer = KafkaConsumer("ats_events")
        self.redis_client = Redis()
        self.metric_calculators = {
            "candidate_scored": CandidateScoreMetrics(),
            "interview_completed": InterviewMetrics(),
            "hire_completed": HireMetrics()
        }
    
    def process_event_stream(self):
        """Process real-time events and update metrics"""
        for message in self.kafka_consumer:
            event = json.loads(message.value)
            
            try:
                # Update real-time metrics
                self.update_real_time_metrics(event)
                
                # Trigger alerts if thresholds exceeded
                self.check_alert_conditions(event)
                
                # Update live dashboards
                self.update_dashboard_cache(event)
                
            except Exception as e:
                self.log_processing_error(event, e)
    
    def update_real_time_metrics(self, event):
        """Update real-time metric counters"""
        event_type = event["event_type"]
        
        if event_type in self.metric_calculators:
            calculator = self.metric_calculators[event_type]
            metrics = calculator.calculate(event)
            
            # Update Redis counters
            for metric_name, value in metrics.items():
                key = f"metrics:{event['job_id']}:{metric_name}"
                self.redis_client.incr(key, value)
                self.redis_client.expire(key, 86400)  # 24 hour TTL
    
    def check_alert_conditions(self, event):
        """Check if event triggers any alert conditions"""
        alert_rules = self.get_alert_rules(event["job_id"])
        
        for rule in alert_rules:
            if self.evaluate_alert_rule(rule, event):
                self.trigger_alert(rule, event)
```

### Batch Analytics Processor
```python
class BatchAnalyticsProcessor:
    def __init__(self):
        self.spark = SparkSession.builder.appName("ATS_Analytics").getOrCreate()
        self.data_warehouse = DataWarehouseConnector()
    
    def calculate_daily_metrics(self, date):
        """Calculate comprehensive daily metrics"""
        # Load events for the day
        events_df = self.load_events_for_date(date)
        
        # Calculate hiring funnel metrics
        funnel_metrics = self.calculate_funnel_metrics(events_df)
        
        # Calculate time-based metrics
        time_metrics = self.calculate_time_metrics(events_df)
        
        # Calculate diversity metrics
        diversity_metrics = self.calculate_diversity_metrics(events_df)
        
        # Calculate cost metrics
        cost_metrics = self.calculate_cost_metrics(events_df)
        
        # Aggregate all metrics
        daily_metrics = {
            "date": date,
            "funnel": funnel_metrics,
            "time": time_metrics,
            "diversity": diversity_metrics,
            "cost": cost_metrics
        }
        
        # Store in data warehouse
        self.data_warehouse.store_daily_metrics(daily_metrics)
        
        return daily_metrics
    
    def calculate_ahp_model_performance(self, hierarchy_id, period_start, period_end):
        """Analyze AHP model performance over time period"""
        # Get all candidates scored with this hierarchy
        scored_candidates = self.get_scored_candidates(hierarchy_id, period_start, period_end)
        
        # Get actual hiring outcomes
        hiring_outcomes = self.get_hiring_outcomes(scored_candidates)
        
        # Calculate prediction accuracy
        accuracy_metrics = self.calculate_prediction_accuracy(
            scored_candidates, 
            hiring_outcomes
        )
        
        # Analyze attribute importance
        attribute_analysis = self.analyze_attribute_importance(
            scored_candidates, 
            hiring_outcomes
        )
        
        # Generate recommendations
        recommendations = self.generate_model_recommendations(
            accuracy_metrics, 
            attribute_analysis
        )
        
        return {
            "hierarchy_id": hierarchy_id,
            "period": {"start": period_start, "end": period_end},
            "accuracy": accuracy_metrics,
            "attributes": attribute_analysis,
            "recommendations": recommendations
        }
```

### Statistical Analysis Engine
```python
class StatisticalAnalysisEngine:
    def correlation_analysis(self, ahp_scores, performance_scores):
        """Analyze correlation between AHP scores and actual performance"""
        from scipy.stats import pearsonr, spearmanr
        
        pearson_corr, pearson_p = pearsonr(ahp_scores, performance_scores)
        spearman_corr, spearman_p = spearmanr(ahp_scores, performance_scores)
        
        return {
            "pearson": {"correlation": pearson_corr, "p_value": pearson_p},
            "spearman": {"correlation": spearman_corr, "p_value": spearman_p},
            "interpretation": self.interpret_correlation(pearson_corr)
        }
    
    def adverse_impact_analysis(self, hiring_data):
        """Perform adverse impact analysis for EEOC compliance"""
        selection_rates = {}
        
        # Calculate selection rates by demographic group
        for group in hiring_data.groups:
            applications = hiring_data[hiring_data.group == group].count()
            hires = hiring_data[(hiring_data.group == group) & (hiring_data.hired == True)].count()
            selection_rates[group] = hires / applications if applications > 0 else 0
        
        # Find highest selection rate (typically majority group)
        highest_rate = max(selection_rates.values())
        
        # Apply four-fifths rule
        four_fifths_threshold = highest_rate * 0.8
        
        compliance_results = {}
        for group, rate in selection_rates.items():
            compliance_results[group] = {
                "selection_rate": rate,
                "compliant": rate >= four_fifths_threshold,
                "ratio_to_highest": rate / highest_rate
            }
        
        return compliance_results
    
    def trend_analysis(self, time_series_data, metric_name):
        """Analyze trends in hiring metrics over time"""
        from scipy import stats
        import numpy as np
        
        x = np.arange(len(time_series_data))
        y = [point[metric_name] for point in time_series_data]
        
        # Linear regression for trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Seasonal decomposition
        seasonal_analysis = self.seasonal_decomposition(y)
        
        # Anomaly detection
        anomalies = self.detect_anomalies(y)
        
        return {
            "trend": {
                "slope": slope,
                "direction": "increasing" if slope > 0 else "decreasing",
                "significance": p_value,
                "r_squared": r_value ** 2
            },
            "seasonal": seasonal_analysis,
            "anomalies": anomalies,
            "forecast": self.forecast_next_period(y)
        }
```

## Dashboard and Visualization

### Real-time Dashboard
```typescript
interface DashboardMetrics {
  realTimeStats: {
    activeApplications: number;
    scheduledInterviews: number;
    pendingDecisions: number;
    offersOutstanding: number;
  };
  todayMetrics: {
    newApplications: number;
    interviewsCompleted: number;
    candidatesAdvanced: number;
    hiresCompleted: number;
  };
  trendData: {
    applicationTrend: TimeSeriesData[];
    conversionTrend: TimeSeriesData[];
    timeToHireTrend: TimeSeriesData[];
  };
  alerts: Alert[];
}

const RealTimeDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics>();
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  
  useEffect(() => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket('wss://api.ats.com/analytics/live');
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setMetrics(prev => ({
        ...prev,
        ...update
      }));
    };
    
    return () => ws.close();
  }, []);
  
  return (
    <div className="dashboard-grid">
      <MetricCards stats={metrics?.realTimeStats} />
      <TrendChart data={metrics?.trendData} timeRange={selectedTimeRange} />
      <FunnelChart conversionRates={metrics?.conversionRates} />
      <AlertPanel alerts={metrics?.alerts} />
      <PerformanceMatrix ahpMetrics={metrics?.ahpPerformance} />
    </div>
  );
};
```

### AHP Performance Dashboard
```typescript
const AHPPerformanceDashboard: React.FC<Props> = ({ hierarchyId }) => {
  const [performanceData, setPerformanceData] = useState<AHPPerformanceData>();
  
  return (
    <div className="ahp-dashboard">
      <div className="overview-section">
        <ModelAccuracyCard accuracy={performanceData?.prediction_accuracy} />
        <ConsistencyCard consistency={performanceData?.consistency_metrics} />
      </div>
      
      <div className="attribute-analysis">
        <AttributeImportanceChart 
          attributes={performanceData?.attribute_importance}
          showComparison={true}
        />
        <CorrelationMatrix 
          correlations={performanceData?.attribute_correlations}
        />
      </div>
      
      <div className="ideal-profiles">
        <IdealProfileEffectiveness 
          profiles={performanceData?.ideal_profile_effectiveness}
        />
      </div>
      
      <div className="recommendations">
        <RecommendationPanel 
          recommendations={performanceData?.recommendations}
          onApplyRecommendation={handleApplyRecommendation}
        />
      </div>
    </div>
  );
};
```

## Report Generation

### Automated Report Service
```python
class ReportGenerator:
    def __init__(self):
        self.template_engine = ReportTemplateEngine()
        self.data_service = AnalyticsDataService()
        self.export_service = ExportService()
    
    def generate_hiring_summary_report(self, period, departments=None):
        """Generate comprehensive hiring summary report"""
        # Gather data
        hiring_metrics = self.data_service.get_hiring_metrics(period, departments)
        diversity_metrics = self.data_service.get_diversity_metrics(period, departments)
        cost_analysis = self.data_service.get_cost_analysis(period, departments)
        trend_analysis = self.data_service.get_trend_analysis(period, departments)
        
        # Compile report data
        report_data = {
            "period": period,
            "departments": departments,
            "executive_summary": self.create_executive_summary(hiring_metrics),
            "hiring_metrics": hiring_metrics,
            "diversity_analysis": diversity_metrics,
            "cost_analysis": cost_analysis,
            "trends": trend_analysis,
            "recommendations": self.generate_recommendations(hiring_metrics, trend_analysis)
        }
        
        # Generate report
        report = self.template_engine.render_report("hiring_summary", report_data)
        
        return report
    
    def generate_compliance_report(self, report_type, period):
        """Generate compliance reports for regulatory requirements"""
        compliance_generators = {
            "eeoc": self.generate_eeoc_report,
            "gdpr": self.generate_gdpr_report,
            "ccpa": self.generate_ccpa_report,
            "audit_trail": self.generate_audit_trail_report
        }
        
        if report_type not in compliance_generators:
            raise ValueError(f"Unsupported compliance report type: {report_type}")
        
        generator = compliance_generators[report_type]
        return generator(period)
    
    def generate_eeoc_report(self, period):
        """Generate EEOC compliance report"""
        # Get demographic data for all hiring activities
        demographic_data = self.data_service.get_demographic_hiring_data(period)
        
        # Perform adverse impact analysis
        adverse_impact = self.statistical_engine.adverse_impact_analysis(demographic_data)
        
        # Calculate selection rates by job category
        selection_rates = self.calculate_selection_rates_by_category(demographic_data)
        
        # Generate report
        report_data = {
            "period": period,
            "job_categories": selection_rates,
            "adverse_impact_analysis": adverse_impact,
            "summary_statistics": self.calculate_eeoc_summary_stats(demographic_data),
            "certification": self.generate_compliance_certification()
        }
        
        return self.template_engine.render_report("eeoc_compliance", report_data)
```

### Export Service
```python
class ExportService:
    def __init__(self):
        self.exporters = {
            "pdf": PDFExporter(),
            "excel": ExcelExporter(),
            "csv": CSVExporter(),
            "json": JSONExporter()
        }
    
    def export_report(self, report_data, format_type, filename=None):
        """Export report in specified format"""
        if format_type not in self.exporters:
            raise ValueError(f"Unsupported export format: {format_type}")
        
        exporter = self.exporters[format_type]
        
        if filename is None:
            filename = self.generate_filename(report_data, format_type)
        
        exported_file = exporter.export(report_data, filename)
        
        # Store in file storage
        file_url = self.store_exported_file(exported_file)
        
        return {
            "filename": filename,
            "format": format_type,
            "size": exported_file.size,
            "url": file_url,
            "expires_at": datetime.utcnow() + timedelta(days=30)
        }
    
    def schedule_recurring_report(self, report_config):
        """Schedule automatic report generation and distribution"""
        schedule = {
            "report_type": report_config.type,
            "recipients": report_config.recipients,
            "frequency": report_config.frequency,  # daily, weekly, monthly
            "format": report_config.format,
            "filters": report_config.filters,
            "next_run": self.calculate_next_run(report_config.frequency)
        }
        
        # Store in scheduler
        self.scheduler.schedule_report(schedule)
        
        return schedule
```

## Data Privacy and Compliance

### GDPR Compliance Engine
```python
class GDPRComplianceEngine:
    def handle_data_subject_request(self, request_type, subject_email):
        """Handle GDPR data subject requests"""
        handlers = {
            "access": self.handle_access_request,
            "deletion": self.handle_deletion_request,
            "portability": self.handle_portability_request,
            "rectification": self.handle_rectification_request
        }
        
        if request_type not in handlers:
            raise ValueError(f"Unsupported request type: {request_type}")
        
        # Log the request
        self.log_data_subject_request(request_type, subject_email)
        
        # Execute request
        result = handlers[request_type](subject_email)
        
        # Update compliance tracking
        self.update_compliance_tracking(request_type, subject_email, result)
        
        return result
    
    def handle_deletion_request(self, subject_email):
        """Handle right to be forgotten request"""
        # Find all data related to the subject
        candidate_data = self.find_candidate_data(subject_email)
        
        if not candidate_data:
            return {"status": "no_data_found", "message": "No data found for the subject"}
        
        # Check for legal basis to retain data
        retention_check = self.check_retention_requirements(candidate_data)
        
        if retention_check.must_retain:
            return {
                "status": "retention_required",
                "reason": retention_check.reason,
                "retention_period": retention_check.period
            }
        
        # Perform deletion
        deletion_result = self.delete_candidate_data(candidate_data)
        
        # Anonymize analytics data
        self.anonymize_analytics_data(candidate_data.id)
        
        return {
            "status": "deleted",
            "deleted_records": deletion_result.count,
            "anonymized_records": deletion_result.anonymized_count
        }
    
    def automated_data_lifecycle_management(self):
        """Automatically manage data lifecycle based on retention policies"""
        # Get retention policies
        policies = self.get_retention_policies()
        
        for policy in policies:
            # Find data eligible for action
            eligible_data = self.find_data_for_lifecycle_action(policy)
            
            for data_record in eligible_data:
                if policy.action == "delete":
                    self.delete_expired_data(data_record)
                elif policy.action == "anonymize":
                    self.anonymize_expired_data(data_record)
                elif policy.action == "archive":
                    self.archive_expired_data(data_record)
```

## Performance Monitoring

### Analytics Performance Metrics
```python
class AnalyticsPerformanceMonitor:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alerting_service = AlertingService()
    
    def monitor_query_performance(self):
        """Monitor analytics query performance"""
        slow_queries = self.get_slow_queries(threshold_seconds=5)
        
        for query in slow_queries:
            # Log slow query
            self.log_slow_query(query)
            
            # Check if optimization needed
            if query.execution_time > 30:  # 30 seconds
                self.alert_slow_query(query)
                self.suggest_optimization(query)
    
    def monitor_data_freshness(self):
        """Monitor data freshness across analytics tables"""
        freshness_checks = [
            {"table": "daily_metrics", "max_age_hours": 2},
            {"table": "candidate_scores", "max_age_minutes": 30},
            {"table": "real_time_events", "max_age_minutes": 5}
        ]
        
        for check in freshness_checks:
            last_update = self.get_last_update_time(check["table"])
            age = datetime.utcnow() - last_update
            
            if "max_age_hours" in check and age.hours > check["max_age_hours"]:
                self.alert_stale_data(check["table"], age)
            elif "max_age_minutes" in check and age.seconds > check["max_age_minutes"] * 60:
                self.alert_stale_data(check["table"], age)
    
    def calculate_system_health_score(self):
        """Calculate overall analytics system health score"""
        metrics = {
            "query_performance": self.calculate_query_performance_score(),
            "data_freshness": self.calculate_data_freshness_score(),
            "error_rate": self.calculate_error_rate_score(),
            "availability": self.calculate_availability_score()
        }
        
        # Weighted average
        weights = {"query_performance": 0.3, "data_freshness": 0.3, "error_rate": 0.2, "availability": 0.2}
        
        health_score = sum(metrics[metric] * weights[metric] for metric in metrics)
        
        return {
            "overall_score": health_score,
            "component_scores": metrics,
            "status": self.get_health_status(health_score)
        }
```

## API Endpoints

### Analytics Data API
```http
GET /api/v1/analytics/hiring-metrics
Query Parameters:
  - start_date: ISO date
  - end_date: ISO date
  - department: string
  - job_ids: comma-separated UUIDs
  - metrics: comma-separated metric names

GET /api/v1/analytics/ahp-performance/{hierarchyId}
Query Parameters:
  - period_start: ISO date
  - period_end: ISO date
  - include_recommendations: boolean

GET /api/v1/analytics/diversity-metrics
Query Parameters:
  - start_date: ISO date
  - end_date: ISO date
  - breakdown_by: department|location|job_level

GET /api/v1/analytics/funnel-analysis/{jobId}
Query Parameters:
  - period: 30d|90d|1y
  - compare_to: previous_period|same_period_last_year
```

### Reporting API
```http
POST /api/v1/reports/generate
{
  "type": "hiring_summary|compliance|ahp_performance",
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "filters": {
    "departments": ["engineering", "sales"],
    "job_levels": ["senior", "staff"]
  },
  "format": "pdf|excel|csv",
  "delivery": {
    "method": "download|email",
    "recipients": ["user@company.com"]
  }
}

GET /api/v1/reports/{reportId}/status

GET /api/v1/reports/{reportId}/download

POST /api/v1/reports/schedule
{
  "name": "Monthly Hiring Report",
  "type": "hiring_summary",
  "frequency": "monthly",
  "recipients": ["hr@company.com"],
  "format": "pdf",
  "enabled": true
}
```

### Compliance API
```http
POST /api/v1/compliance/data-subject-request
{
  "type": "access|deletion|portability|rectification",
  "subject_email": "candidate@email.com",
  "requester_info": {
    "name": "John Doe",
    "relationship": "self|legal_representative",
    "verification_document": "document_id"
  }
}

GET /api/v1/compliance/retention-status
Query Parameters:
  - data_type: candidates|applications|interviews
  - age_threshold: 365 (days)

POST /api/v1/compliance/audit-trail/{entityType}/{entityId}
Query Parameters:
  - start_date: ISO date
  - end_date: ISO date
  - actions: comma-separated action types
```

### Real-time Analytics API
```http
GET /api/v1/analytics/real-time/dashboard
WebSocket: wss://api.ats.com/analytics/live

GET /api/v1/analytics/alerts/active

POST /api/v1/analytics/alerts/rules
{
  "name": "High Application Volume",
  "condition": "applications_per_hour > 50",
  "severity": "warning",
  "recipients": ["recruiter@company.com"]
}
```

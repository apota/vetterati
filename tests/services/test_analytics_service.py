import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Test the Analytics Service
class TestAnalyticsService:
    
    @pytest.mark.asyncio
    async def test_get_dashboard_data(self, mock_db_session):
        """Test dashboard data retrieval."""
        from src.services.analytics_service.services.analytics_service import AnalyticsService
        
        service = AnalyticsService()
        
        # Mock database responses
        mock_db_session.execute.return_value.scalar.return_value = 10
        mock_db_session.execute.return_value.first.return_value = Mock(
            total_predictions=100,
            avg_score=0.75,
            high_confidence_predictions=60
        )
        
        result = await service.get_dashboard_data(mock_db_session, "30d")
        
        assert result is not None
        assert hasattr(result, 'active_job_postings')
        assert hasattr(result, 'total_applications_this_month')

    @pytest.mark.asyncio
    async def test_get_active_workflows_count(self, mock_db_session):
        """Test active workflows count."""
        from src.services.analytics_service.services.analytics_service import AnalyticsService
        
        service = AnalyticsService()
        mock_db_session.execute.return_value.scalar.return_value = 25
        
        result = await service.get_active_workflows_count(mock_db_session)
        
        assert result == 25

class TestMetricsService:
    
    @pytest.mark.asyncio
    async def test_get_hiring_metrics(self, mock_db_session):
        """Test hiring metrics calculation."""
        from src.services.analytics_service.services.metrics_service import MetricsService
        
        service = MetricsService()
        
        # Mock database responses
        mock_results = [
            Mock(department="Engineering", applications=50, hires=10, avg_days=14.5),
            Mock(department="Marketing", applications=20, hires=5, avg_days=12.0)
        ]
        
        mock_db_session.execute.return_value.scalar.side_effect = [100, 25]  # total apps, total hires
        mock_db_session.execute.return_value.__iter__ = lambda x: iter(mock_results)
        
        result = await service.get_hiring_metrics(
            mock_db_session, 
            start_date="2024-01-01", 
            end_date="2024-01-31"
        )
        
        assert result is not None
        assert hasattr(result, 'total_applications')
        assert hasattr(result, 'total_hires')
        assert hasattr(result, 'hire_rate')

class TestReportingService:
    
    @pytest.mark.asyncio
    async def test_generate_custom_report(self, mock_db_session):
        """Test custom report generation."""
        from src.services.analytics_service.services.reporting_service import ReportingService
        from src.services.analytics_service.schemas import CustomReportRequest
        
        service = ReportingService()
        
        # Mock request
        request = CustomReportRequest(
            report_name="Test Report",
            report_type="hiring_metrics",
            date_range={
                "start": datetime(2024, 1, 1),
                "end": datetime(2024, 1, 31)
            },
            filters={"department": "Engineering"},
            groupby_fields=["department"],
            metrics=["applications", "hires"]
        )
        
        # Mock database response
        mock_db_session.execute.return_value.__iter__ = lambda x: iter([
            Mock(_mapping={"department": "Engineering", "applications": 50, "hires": 10})
        ])
        
        with patch('uuid.uuid4', return_value="test-report-id"):
            result = await service.generate_custom_report(mock_db_session, request)
        
        assert result is not None
        assert result.report_name == "Test Report"
        assert len(result.data) >= 0

class TestPredictiveService:
    
    @pytest.mark.asyncio
    async def test_calculate_success_probability(self, mock_db_session):
        """Test success probability calculation."""
        from src.services.analytics_service.services.predictive_service import PredictiveService
        
        service = PredictiveService()
        
        # Mock AHP score
        mock_db_session.execute.return_value.first.side_effect = [
            Mock(score=0.8, criteria_scores={}),  # AHP score
            Mock(total_candidates=100, successful_hires=20)  # Historical data
        ]
        
        result = await service.calculate_success_probability(
            mock_db_session,
            candidate_id="candidate-123",
            job_id="job-123"
        )
        
        assert 0 <= result <= 1
        assert isinstance(result, float)

    @pytest.mark.asyncio
    async def test_get_hiring_trends(self, mock_db_session):
        """Test hiring trends prediction."""
        from src.services.analytics_service.services.predictive_service import PredictiveService
        
        service = PredictiveService()
        
        # Mock historical data
        mock_historical_data = [
            Mock(month=datetime(2024, 1, 1), hires_count=10, department="Engineering"),
            Mock(month=datetime(2024, 2, 1), hires_count=12, department="Engineering"),
            Mock(month=datetime(2024, 3, 1), hires_count=15, department="Engineering")
        ]
        
        mock_db_session.execute.return_value.__iter__ = lambda x: iter(mock_historical_data)
        
        result = await service.get_hiring_trends(mock_db_session, forecast_months=3)
        
        assert result is not None
        assert hasattr(result, 'hiring_trends')
        assert hasattr(result, 'demand_predictions')
        assert len(result.hiring_trends) == 3

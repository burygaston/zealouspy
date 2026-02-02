"""Tests for AnalyticsService - PARTIAL COVERAGE for diff demo."""

import pytest
from zealous.services.analytics_service import AnalyticsService


class TestAnalyticsService:
    """Test AnalyticsService - only testing some methods."""

    def test_track_event(self):
        """Test tracking an event."""
        service = AnalyticsService()
        service.track_event("task_created", {"task_id": 1})

        assert service.get_event_count() == 1

    def test_track_multiple_events(self):
        """Test tracking multiple events."""
        service = AnalyticsService()
        service.track_event("task_created", {"task_id": 1})
        service.track_event("task_completed", {"task_id": 1})
        service.track_event("task_created", {"task_id": 2})

        assert service.get_event_count() == 3
        assert service.get_event_count("task_created") == 2
        assert service.get_event_count("task_completed") == 1

    def test_get_event_count_empty(self):
        """Test event count when empty."""
        service = AnalyticsService()
        assert service.get_event_count() == 0
        assert service.get_event_count("any_type") == 0

    def test_clear_events(self):
        """Test clearing events."""
        service = AnalyticsService()
        service.track_event("test", {"data": 1})
        service.track_event("test", {"data": 2})

        cleared = service.clear_events()
        assert cleared == 2
        assert service.get_event_count() == 0

    # NOTE: The following methods are NOT tested:
    # - get_events_by_type()
    # - get_events_since()
    # - get_event_summary()
    # - calculate_task_metrics()
    # - generate_weekly_report()
    # - export_to_csv()
    #
    # These will show as UNCOVERED in the diff coverage report!

"""Analytics service - NEW FILE for diff coverage testing."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsService:
    """Service for project and task analytics."""

    def __init__(self):
        self._events: List[Dict] = []

    # === TESTED METHODS (will show as covered in diff) ===

    def track_event(self, event_type: str, data: Dict) -> None:
        """Track an analytics event."""
        self._events.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_event_count(self, event_type: Optional[str] = None) -> int:
        """Get count of events."""
        if event_type is None:
            return len(self._events)
        return len([e for e in self._events if e["type"] == event_type])

    def clear_events(self) -> int:
        """Clear all events and return count cleared."""
        count = len(self._events)
        self._events = []
        return count

    # === UNTESTED METHODS (will show as NOT covered in diff) ===

    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """Get all events of a specific type - NOT TESTED."""
        return [e for e in self._events if e["type"] == event_type]

    def get_events_since(self, since: datetime) -> List[Dict]:
        """Get events since a specific time - NOT TESTED."""
        since_iso = since.isoformat()
        return [e for e in self._events if e["timestamp"] >= since_iso]

    def get_event_summary(self) -> Dict[str, int]:
        """Get summary of events by type - NOT TESTED."""
        summary: Dict[str, int] = defaultdict(int)
        for event in self._events:
            summary[event["type"]] += 1
        return dict(summary)

    def calculate_task_metrics(self, tasks: List[Dict]) -> Dict[str, float]:
        """Calculate task completion metrics - NOT TESTED."""
        if not tasks:
            return {"completion_rate": 0.0, "avg_duration": 0.0}

        completed = [t for t in tasks if t.get("status") == "done"]
        completion_rate = len(completed) / len(tasks) * 100

        durations = []
        for task in completed:
            if task.get("completed_at") and task.get("created_at"):
                duration = (task["completed_at"] - task["created_at"]).total_seconds()
                durations.append(duration)

        avg_duration = sum(durations) / len(durations) if durations else 0.0

        return {
            "completion_rate": completion_rate,
            "avg_duration": avg_duration,
            "total_tasks": len(tasks),
            "completed_tasks": len(completed),
        }

    def generate_weekly_report(self) -> Dict:
        """Generate weekly analytics report - NOT TESTED."""
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)

        recent_events = self.get_events_since(week_ago)
        summary = {}

        for event in recent_events:
            event_type = event["type"]
            if event_type not in summary:
                summary[event_type] = {"count": 0, "first": None, "last": None}

            summary[event_type]["count"] += 1
            timestamp = event["timestamp"]

            if summary[event_type]["first"] is None:
                summary[event_type]["first"] = timestamp
            summary[event_type]["last"] = timestamp

        return {
            "period_start": week_ago.isoformat(),
            "period_end": now.isoformat(),
            "total_events": len(recent_events),
            "by_type": summary,
        }

    def export_to_csv(self) -> str:
        """Export events to CSV format - NOT TESTED."""
        if not self._events:
            return "type,timestamp,data\n"

        lines = ["type,timestamp,data"]
        for event in self._events:
            data_str = str(event["data"]).replace(",", ";")
            lines.append(f"{event['type']},{event['timestamp']},{data_str}")

        return "\n".join(lines)

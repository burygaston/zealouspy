"""Project model - POORLY TESTED (low coverage expected)."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectSettings(BaseModel):
    allow_public_tasks: bool = False
    require_task_estimates: bool = True
    auto_assign_tasks: bool = False
    notification_email: Optional[str] = None
    slack_webhook: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

    def enable_slack_notifications(self, webhook_url: str) -> None:
        """Enable Slack notifications."""
        if not webhook_url.startswith("https://hooks.slack.com/"):
            raise ValueError("Invalid Slack webhook URL")
        self.slack_webhook = webhook_url

    def disable_slack_notifications(self) -> None:
        """Disable Slack notifications."""
        self.slack_webhook = None

    def add_custom_field(self, name: str, field_type: str, required: bool = False) -> None:
        """Add a custom field to the project."""
        self.custom_fields[name] = {
            "type": field_type,
            "required": required,
            "created_at": datetime.utcnow().isoformat(),
        }

    def remove_custom_field(self, name: str) -> None:
        """Remove a custom field."""
        if name in self.custom_fields:
            del self.custom_fields[name]


class Project(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    owner_id: int
    member_ids: List[int] = Field(default_factory=list)
    settings: ProjectSettings = Field(default_factory=ProjectSettings)
    budget: Optional[float] = None
    spent: float = 0.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if project is active."""
        return self.status == ProjectStatus.ACTIVE

    def is_over_budget(self) -> bool:
        """Check if project is over budget."""
        if self.budget is None:
            return False
        return self.spent > self.budget

    def get_budget_remaining(self) -> Optional[float]:
        """Get remaining budget."""
        if self.budget is None:
            return None
        return max(0, self.budget - self.spent)

    def get_budget_utilization(self) -> Optional[float]:
        """Get budget utilization percentage."""
        if self.budget is None or self.budget == 0:
            return None
        return (self.spent / self.budget) * 100

    def add_member(self, user_id: int) -> None:
        """Add a member to the project."""
        if user_id not in self.member_ids and user_id != self.owner_id:
            self.member_ids.append(user_id)
            self.updated_at = datetime.utcnow()

    def remove_member(self, user_id: int) -> None:
        """Remove a member from the project."""
        if user_id == self.owner_id:
            raise ValueError("Cannot remove project owner")
        if user_id in self.member_ids:
            self.member_ids.remove(user_id)
            self.updated_at = datetime.utcnow()

    def transfer_ownership(self, new_owner_id: int) -> None:
        """Transfer project ownership."""
        if new_owner_id == self.owner_id:
            return

        # Add old owner as member
        if self.owner_id not in self.member_ids:
            self.member_ids.append(self.owner_id)

        # Remove new owner from members if present
        if new_owner_id in self.member_ids:
            self.member_ids.remove(new_owner_id)

        self.owner_id = new_owner_id
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the project."""
        if self.status == ProjectStatus.ARCHIVED:
            raise ValueError("Cannot activate archived project")
        self.status = ProjectStatus.ACTIVE
        if self.start_date is None:
            self.start_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def put_on_hold(self) -> None:
        """Put project on hold."""
        if self.status not in (ProjectStatus.ACTIVE, ProjectStatus.PLANNING):
            raise ValueError(f"Cannot put {self.status} project on hold")
        self.status = ProjectStatus.ON_HOLD
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Mark project as completed."""
        self.status = ProjectStatus.COMPLETED
        self.end_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive the project."""
        self.status = ProjectStatus.ARCHIVED
        self.updated_at = datetime.utcnow()

    def calculate_duration_days(self) -> Optional[int]:
        """Calculate project duration in days."""
        if self.start_date is None:
            return None
        end = self.end_date or datetime.utcnow()
        return (end - self.start_date).days

    def get_team_size(self) -> int:
        """Get total team size including owner."""
        return len(self.member_ids) + 1

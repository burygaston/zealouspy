"""Task model - PARTIALLY TESTED (medium coverage expected)."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: Optional[int] = None
    project_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    subtask_ids: List[int] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date is None:
            return False
        if self.status == TaskStatus.DONE:
            return False
        return datetime.utcnow() > self.due_date

    def is_blocked(self) -> bool:
        """Check if task is blocked."""
        return self.status == TaskStatus.BLOCKED

    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.DONE

    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """Check if task can transition to new status."""
        valid_transitions = {
            TaskStatus.TODO: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
            TaskStatus.IN_PROGRESS: [TaskStatus.IN_REVIEW, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
            TaskStatus.IN_REVIEW: [TaskStatus.DONE, TaskStatus.IN_PROGRESS],
            TaskStatus.BLOCKED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
            TaskStatus.DONE: [],
            TaskStatus.CANCELLED: [],
        }
        return new_status in valid_transitions.get(self.status, [])

    def transition_to(self, new_status: TaskStatus) -> None:
        """Transition task to new status."""
        if not self.can_transition_to(new_status):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")

        self.status = new_status
        self.updated_at = datetime.utcnow()

        if new_status == TaskStatus.DONE:
            self.completed_at = datetime.utcnow()

    def add_subtask(self, subtask_id: int) -> None:
        """Add a subtask."""
        if subtask_id not in self.subtask_ids:
            self.subtask_ids.append(subtask_id)
            self.updated_at = datetime.utcnow()

    def remove_subtask(self, subtask_id: int) -> None:
        """Remove a subtask."""
        if subtask_id in self.subtask_ids:
            self.subtask_ids.remove(subtask_id)
            self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the task."""
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the task."""
        tag = tag.lower().strip()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def estimate_completion_date(self) -> Optional[datetime]:
        """Estimate when task will be completed based on progress."""
        if self.estimated_hours is None:
            return None
        if self.actual_hours is None:
            return datetime.utcnow() + timedelta(hours=self.estimated_hours)

        remaining = max(0, self.estimated_hours - self.actual_hours)
        return datetime.utcnow() + timedelta(hours=remaining)

    def calculate_progress(self) -> float:
        """Calculate task progress as percentage."""
        if self.status == TaskStatus.DONE:
            return 100.0
        if self.status == TaskStatus.TODO:
            return 0.0
        if self.estimated_hours is None or self.actual_hours is None:
            status_progress = {
                TaskStatus.IN_PROGRESS: 25.0,
                TaskStatus.IN_REVIEW: 75.0,
                TaskStatus.BLOCKED: 50.0,
            }
            return status_progress.get(self.status, 0.0)

        progress = (self.actual_hours / self.estimated_hours) * 100
        return min(99.0, progress)  # Cap at 99% until done

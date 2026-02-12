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
    """Task model representing a work item with status, priority, and tracking.

    Tasks follow a state machine for status transitions and support hierarchical
    relationships (parent/subtasks), time tracking, and tagging.

    Attributes:
        id: Unique task identifier, assigned by the system.
        title: Task title (required).
        description: Optional detailed description.
        status: Current task status in the workflow.
        priority: Task priority level for prioritization.
        assignee_id: ID of the user assigned to this task.
        project_id: ID of the project this task belongs to.
        parent_task_id: ID of parent task if this is a subtask.
        subtask_ids: List of IDs of tasks that are subtasks of this task.
        tags: List of tags for categorization and filtering.
        due_date: Optional deadline for task completion.
        estimated_hours: Estimated time to complete in hours.
        actual_hours: Actual time spent on the task in hours.
        created_at: Timestamp when the task was created.
        updated_at: Timestamp of the last update to task data.
        completed_at: Timestamp when the task was marked as DONE.
    """

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
        """Check if the task is past its due date.

        A task is overdue if it has a due_date set, is not completed, and the
        current time is past the due date.

        Returns:
            True if task is overdue, False otherwise.
        """
        if self.due_date is None:
            return False
        if self.status == TaskStatus.DONE:
            return False
        return datetime.utcnow() > self.due_date

    def is_blocked(self) -> bool:
        """Check if the task is in blocked status.

        Returns:
            True if task status is BLOCKED, False otherwise.
        """
        return self.status == TaskStatus.BLOCKED

    def is_completed(self) -> bool:
        """Check if the task is completed.

        Returns:
            True if task status is DONE, False otherwise.
        """
        return self.status == TaskStatus.DONE

    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """Check if the task can transition to a new status.

        Tasks follow a state machine with valid transitions. Terminal states
        (DONE, CANCELLED) cannot transition to any other state.

        Valid transitions:
            - TODO -> IN_PROGRESS, CANCELLED
            - IN_PROGRESS -> IN_REVIEW, BLOCKED, CANCELLED
            - IN_REVIEW -> DONE, IN_PROGRESS
            - BLOCKED -> IN_PROGRESS, CANCELLED
            - DONE -> (none)
            - CANCELLED -> (none)

        Args:
            new_status: The target status to transition to.

        Returns:
            True if the transition is valid, False otherwise.
        """
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
        """Transition the task to a new status.

        Validates the transition is allowed before applying. Automatically sets
        completed_at when transitioning to DONE.

        Args:
            new_status: The target status to transition to.

        Raises:
            ValueError: If the transition is not valid for the current status.
        """
        if not self.can_transition_to(new_status):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")

        self.status = new_status
        self.updated_at = datetime.utcnow()

        if new_status == TaskStatus.DONE:
            self.completed_at = datetime.utcnow()

    def add_subtask(self, subtask_id: int) -> None:
        """Add a subtask to this task's subtask list.

        Prevents duplicate subtask IDs.

        Args:
            subtask_id: ID of the task to add as a subtask.
        """
        if subtask_id not in self.subtask_ids:
            self.subtask_ids.append(subtask_id)
            self.updated_at = datetime.utcnow()

    def remove_subtask(self, subtask_id: int) -> None:
        """Remove a subtask from this task's subtask list.

        Args:
            subtask_id: ID of the subtask to remove.
        """
        if subtask_id in self.subtask_ids:
            self.subtask_ids.remove(subtask_id)
            self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the task for categorization.

        Tags are normalized to lowercase and trimmed. Prevents duplicate tags.

        Args:
            tag: Tag string to add.
        """
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the task.

        Tag matching is case-insensitive (normalized to lowercase).

        Args:
            tag: Tag string to remove.
        """
        tag = tag.lower().strip()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def estimate_completion_date(self) -> Optional[datetime]:
        """Estimate when the task will be completed based on time tracking.

        Uses estimated_hours and actual_hours to project completion date.
        If no actual hours are logged yet, assumes work starts now.

        Args:
            None

        Returns:
            Estimated completion datetime, or None if estimated_hours is not set.
        """
        if self.estimated_hours is None:
            return None
        if self.actual_hours is None:
            return datetime.utcnow() + timedelta(hours=self.estimated_hours)

        remaining = max(0, self.estimated_hours - self.actual_hours)
        return datetime.utcnow() + timedelta(hours=remaining)

    def calculate_progress(self) -> float:
        """Calculate task completion progress as a percentage.

        Progress calculation strategy:
        - DONE status: Always 100%
        - TODO status: Always 0%
        - With time tracking: (actual_hours / estimated_hours) * 100, capped at 99%
        - Without time tracking: Status-based estimate (IN_PROGRESS: 25%,
          IN_REVIEW: 75%, BLOCKED: 50%)

        Returns:
            Progress percentage from 0.0 to 100.0.
        """
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

"""Task service - POORLY TESTED (many coverage gaps)."""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from ..models.task import Task, TaskStatus, TaskPriority


class TaskService:
    """Business logic service for task management operations.

    Provides comprehensive task lifecycle management including creation, retrieval,
    updates, assignment, status transitions, and analytics. Acts as the primary
    interface for task-related operations in the application.

    Attributes:
        _tasks: Internal dictionary mapping task IDs to Task objects.
        _next_id: Counter for generating unique task IDs.
    """

    def __init__(self):
        """Initialize the task service with empty task storage."""
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee_id: Optional[int] = None,
        project_id: Optional[int] = None,
    ) -> Task:
        """Create a new task with the specified properties.

        Args:
            title: Task title (required).
            description: Optional detailed description of the task.
            priority: Task priority level (default: MEDIUM).
            assignee_id: Optional user ID to assign the task to.
            project_id: Optional project ID to associate the task with.

        Returns:
            Newly created Task object with assigned ID.
        """
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            priority=priority,
            assignee_id=assignee_id,
            project_id=project_id,
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by its ID.

        Args:
            task_id: Unique identifier of the task to retrieve.

        Returns:
            Task object if found, None otherwise.
        """
        return self._tasks.get(task_id)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assignee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Task]:
        """List tasks with optional filtering and pagination.

        Filters are applied cumulatively (AND logic). Results can be paginated
        using limit and offset parameters.

        Args:
            status: Filter by task status.
            priority: Filter by task priority.
            assignee_id: Filter by assigned user ID.
            project_id: Filter by project ID.
            limit: Maximum number of tasks to return (default: 100).
            offset: Number of tasks to skip for pagination (default: 0).

        Returns:
            List of Task objects matching the specified filters.
        """
        tasks = list(self._tasks.values())

        if status is not None:
            tasks = [t for t in tasks if t.status == status]

        if priority is not None:
            tasks = [t for t in tasks if t.priority == priority]

        if assignee_id is not None:
            tasks = [t for t in tasks if t.assignee_id == assignee_id]

        if project_id is not None:
            tasks = [t for t in tasks if t.project_id == project_id]

        return tasks[offset : offset + limit]

    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """Update specific fields of a task.

        Only updates fields that are in the allowed set. Automatically updates
        the task's updated_at timestamp.

        Args:
            task_id: Unique identifier of the task to update.
            **kwargs: Field names and new values to update. Allowed fields:
                title, description, priority, assignee_id, due_date, estimated_hours.

        Returns:
            Updated Task object if found, None if task doesn't exist.
        """
        task = self.get_task(task_id)
        if task is None:
            return None

        allowed_fields = {"title", "description", "priority", "assignee_id", "due_date", "estimated_hours"}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(task, field, value)

        task.updated_at = datetime.utcnow()
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task from the system.

        Args:
            task_id: Unique identifier of the task to delete.

        Returns:
            True if the task was found and deleted, False if not found.
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def assign_task(self, task_id: int, assignee_id: int) -> Optional[Task]:
        """Assign a task to a specific user.

        Args:
            task_id: Unique identifier of the task to assign.
            assignee_id: User ID to assign the task to.

        Returns:
            Updated Task object if found, None if task doesn't exist.
        """
        task = self.get_task(task_id)
        if task is None:
            return None
        task.assignee_id = assignee_id
        task.updated_at = datetime.utcnow()
        return task

    def unassign_task(self, task_id: int) -> Optional[Task]:
        """Remove the assignee from a task, leaving it unassigned.

        Args:
            task_id: Unique identifier of the task to unassign.

        Returns:
            Updated Task object if found, None if task doesn't exist.
        """
        task = self.get_task(task_id)
        if task is None:
            return None
        task.assignee_id = None
        task.updated_at = datetime.utcnow()
        return task

    def transition_task(self, task_id: int, new_status: TaskStatus) -> Optional[Task]:
        """Transition a task to a new status following valid state transitions.

        Uses the task's transition logic to ensure only valid status changes occur.

        Args:
            task_id: Unique identifier of the task to transition.
            new_status: Target status to transition to.

        Returns:
            Updated Task object if found, None if task doesn't exist.

        Raises:
            ValueError: If the transition is invalid for the current task status.
        """
        task = self.get_task(task_id)
        if task is None:
            return None
        task.transition_to(new_status)
        return task

    def get_overdue_tasks(self) -> List[Task]:
        """Retrieve all tasks that are past their due date.

        Only includes tasks that have a due_date set and are not completed.

        Returns:
            List of overdue Task objects.
        """
        return [t for t in self._tasks.values() if t.is_overdue()]

    def get_blocked_tasks(self) -> List[Task]:
        """Retrieve all tasks currently in blocked status.

        Returns:
            List of Task objects with status BLOCKED.
        """
        return [t for t in self._tasks.values() if t.is_blocked()]

    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Find all tasks with a specific tag.

        Tag matching is case-insensitive.

        Args:
            tag: Tag name to search for.

        Returns:
            List of Task objects containing the specified tag.
        """
        tag = tag.lower().strip()
        return [t for t in self._tasks.values() if tag in t.tags]

    def bulk_assign(self, task_ids: List[int], assignee_id: int) -> Dict[int, bool]:
        """Assign multiple tasks to the same user in a single operation.

        Args:
            task_ids: List of task IDs to assign.
            assignee_id: User ID to assign all tasks to.

        Returns:
            Dictionary mapping each task_id to True (success) or False (task not found).
        """
        results = {}
        for task_id in task_ids:
            task = self.get_task(task_id)
            if task:
                task.assignee_id = assignee_id
                task.updated_at = datetime.utcnow()
                results[task_id] = True
            else:
                results[task_id] = False
        return results

    def bulk_transition(self, task_ids: List[int], new_status: TaskStatus) -> Dict[int, bool]:
        """Transition multiple tasks to the same status in a single operation.

        Only transitions tasks where the status change is valid according to
        the task's state machine.

        Args:
            task_ids: List of task IDs to transition.
            new_status: Target status for all tasks.

        Returns:
            Dictionary mapping each task_id to True (success) or False
            (task not found or invalid transition).
        """
        results = {}
        for task_id in task_ids:
            task = self.get_task(task_id)
            if task and task.can_transition_to(new_status):
                task.transition_to(new_status)
                results[task_id] = True
            else:
                results[task_id] = False
        return results

    def get_task_stats(self, project_id: Optional[int] = None) -> Dict[str, int]:
        """Calculate task statistics, optionally filtered by project.

        Provides counts by status and includes overdue task count.

        Args:
            project_id: Optional project ID to filter statistics to a specific project.

        Returns:
            Dictionary containing:
                - total: Total task count
                - Counts for each status (todo, in_progress, in_review, done, blocked, cancelled)
                - overdue: Number of tasks past their due date
        """
        tasks = self._tasks.values()
        if project_id is not None:
            tasks = [t for t in tasks if t.project_id == project_id]

        stats = {
            "total": len(list(tasks)),
            "todo": 0,
            "in_progress": 0,
            "in_review": 0,
            "done": 0,
            "blocked": 0,
            "cancelled": 0,
            "overdue": 0,
        }

        for task in self._tasks.values():
            if project_id is not None and task.project_id != project_id:
                continue
            stats[task.status.value] = stats.get(task.status.value, 0) + 1
            if task.is_overdue():
                stats["overdue"] += 1

        return stats

    def calculate_velocity(self, days: int = 14) -> float:
        """Calculate team velocity based on completed tasks.

        Velocity is measured as the average number of tasks completed per week
        over the specified time period.

        Args:
            days: Number of days to look back for velocity calculation (default: 14).

        Returns:
            Average number of tasks completed per week.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        completed = 0
        for task in self._tasks.values():
            if task.completed_at and task.completed_at > cutoff:
                completed += 1
        return completed / (days / 7)  # Tasks per week

    def get_workload_distribution(self) -> Dict[int, int]:
        """Calculate current workload distribution across team members.

        Only counts active tasks (excludes DONE and CANCELLED status).

        Returns:
            Dictionary mapping assignee user IDs to their number of active tasks.
        """
        distribution: Dict[int, int] = {}
        for task in self._tasks.values():
            if task.assignee_id and task.status not in (TaskStatus.DONE, TaskStatus.CANCELLED):
                distribution[task.assignee_id] = distribution.get(task.assignee_id, 0) + 1
        return distribution

    def auto_assign_task(self, task_id: int, team_member_ids: List[int]) -> Optional[Task]:
        """Automatically assign a task to the team member with the lowest workload.

        Uses workload distribution to find the team member with fewest active tasks
        and assigns the specified task to them.

        Args:
            task_id: Unique identifier of the task to auto-assign.
            team_member_ids: List of user IDs representing available team members.

        Returns:
            Updated Task object if successful, None if task not found or no
            team members provided.
        """
        if not team_member_ids:
            return None

        task = self.get_task(task_id)
        if task is None:
            return None

        workload = self.get_workload_distribution()
        min_load = float("inf")
        assignee = team_member_ids[0]

        for member_id in team_member_ids:
            load = workload.get(member_id, 0)
            if load < min_load:
                min_load = load
                assignee = member_id

        task.assignee_id = assignee
        task.updated_at = datetime.utcnow()
        return task

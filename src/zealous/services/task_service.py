"""Task service - POORLY TESTED (many coverage gaps)."""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from ..models.task import Task, TaskStatus, TaskPriority


class TaskService:
    """Service for managing tasks."""

    def __init__(self):
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
        """Create a new task."""
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
        """Get task by ID."""
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
        """List tasks with optional filters - PARTIALLY TESTED."""
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
        """Update task fields - NOT TESTED."""
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
        """Delete a task - NOT TESTED."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def assign_task(self, task_id: int, assignee_id: int) -> Optional[Task]:
        """Assign task to user - NOT TESTED."""
        task = self.get_task(task_id)
        if task is None:
            return None
        task.assignee_id = assignee_id
        task.updated_at = datetime.utcnow()
        return task

    def unassign_task(self, task_id: int) -> Optional[Task]:
        """Unassign task - NOT TESTED."""
        task = self.get_task(task_id)
        if task is None:
            return None
        task.assignee_id = None
        task.updated_at = datetime.utcnow()
        return task

    def transition_task(self, task_id: int, new_status: TaskStatus) -> Optional[Task]:
        """Transition task to new status - NOT TESTED."""
        task = self.get_task(task_id)
        if task is None:
            return None
        task.transition_to(new_status)
        return task

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks - NOT TESTED."""
        return [t for t in self._tasks.values() if t.is_overdue()]

    def get_blocked_tasks(self) -> List[Task]:
        """Get all blocked tasks - NOT TESTED."""
        return [t for t in self._tasks.values() if t.is_blocked()]

    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Get tasks by tag - NOT TESTED."""
        tag = tag.lower().strip()
        return [t for t in self._tasks.values() if tag in t.tags]

    def bulk_assign(self, task_ids: List[int], assignee_id: int) -> Dict[int, bool]:
        """Bulk assign tasks - NOT TESTED."""
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
        """Bulk transition tasks - NOT TESTED."""
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
        """Get task statistics - NOT TESTED."""
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
        """Calculate team velocity - NOT TESTED."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        completed = 0
        for task in self._tasks.values():
            if task.completed_at and task.completed_at > cutoff:
                completed += 1
        return completed / (days / 7)  # Tasks per week

    def get_workload_distribution(self) -> Dict[int, int]:
        """Get workload by assignee - NOT TESTED."""
        distribution: Dict[int, int] = {}
        for task in self._tasks.values():
            if task.assignee_id and task.status not in (TaskStatus.DONE, TaskStatus.CANCELLED):
                distribution[task.assignee_id] = distribution.get(task.assignee_id, 0) + 1
        return distribution

    def auto_assign_task(self, task_id: int, team_member_ids: List[int]) -> Optional[Task]:
        """Auto-assign task to team member with lowest workload - NOT TESTED."""
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

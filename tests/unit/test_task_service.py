"""Tests for TaskService - LOW COVERAGE."""

import pytest
from zealous.services.task_service import TaskService
from zealous.models.task import TaskStatus, TaskPriority


class TestTaskService:
    """Test TaskService - minimal tests."""

    def test_create_task(self):
        """Test creating a task."""
        service = TaskService()
        task = service.create_task("Test Task", description="A test task")

        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "A test task"

    def test_get_task(self):
        """Test getting a task."""
        service = TaskService()
        created = service.create_task("Test Task")

        task = service.get_task(created.id)
        assert task is not None
        assert task.title == "Test Task"

    def test_list_tasks(self):
        """Test listing tasks."""
        service = TaskService()
        service.create_task("Task 1")
        service.create_task("Task 2")

        tasks = service.list_tasks()
        assert len(tasks) == 2

    # NOTE: update_task, delete_task, assign_task, unassign_task,
    # transition_task, get_overdue_tasks, get_blocked_tasks,
    # get_tasks_by_tag, bulk_assign, bulk_transition, get_task_stats,
    # calculate_velocity, get_workload_distribution, auto_assign_task
    # are ALL NOT TESTED

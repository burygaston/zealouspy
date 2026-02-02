"""Tests for Task model - MEDIUM COVERAGE."""

import pytest
from datetime import datetime, timedelta
from zealous.models.task import Task, TaskStatus, TaskPriority


class TestTask:
    """Test Task model."""

    def test_create_task_defaults(self):
        """Test creating task with defaults."""
        task = Task(title="Test Task")
        assert task.title == "Test Task"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM

    def test_is_overdue_no_due_date(self):
        """Test is_overdue with no due date."""
        task = Task(title="Test")
        assert task.is_overdue() is False

    def test_is_overdue_completed(self):
        """Test completed task is not overdue."""
        task = Task(
            title="Test",
            status=TaskStatus.DONE,
            due_date=datetime.utcnow() - timedelta(days=1),
        )
        assert task.is_overdue() is False

    def test_is_overdue_true(self):
        """Test overdue task."""
        task = Task(
            title="Test",
            due_date=datetime.utcnow() - timedelta(days=1),
        )
        assert task.is_overdue() is True

    def test_is_blocked(self):
        """Test is_blocked method."""
        task = Task(title="Test", status=TaskStatus.BLOCKED)
        assert task.is_blocked() is True

        task.status = TaskStatus.IN_PROGRESS
        assert task.is_blocked() is False

    def test_is_completed(self):
        """Test is_completed method."""
        task = Task(title="Test", status=TaskStatus.DONE)
        assert task.is_completed() is True

    def test_can_transition_to_valid(self):
        """Test valid transitions."""
        task = Task(title="Test", status=TaskStatus.TODO)
        assert task.can_transition_to(TaskStatus.IN_PROGRESS) is True
        assert task.can_transition_to(TaskStatus.CANCELLED) is True
        assert task.can_transition_to(TaskStatus.DONE) is False

    def test_transition_to_success(self):
        """Test successful transition."""
        task = Task(title="Test", status=TaskStatus.TODO)
        task.transition_to(TaskStatus.IN_PROGRESS)
        assert task.status == TaskStatus.IN_PROGRESS

    def test_transition_to_done_sets_completed_at(self):
        """Test transitioning to done sets completed_at."""
        task = Task(title="Test", status=TaskStatus.IN_REVIEW)
        task.transition_to(TaskStatus.DONE)
        assert task.completed_at is not None

    def test_transition_to_invalid_raises(self):
        """Test invalid transition raises error."""
        task = Task(title="Test", status=TaskStatus.TODO)
        with pytest.raises(ValueError):
            task.transition_to(TaskStatus.DONE)

    # NOTE: add_subtask, remove_subtask, add_tag, remove_tag are NOT tested
    # NOTE: estimate_completion_date, calculate_progress are NOT tested

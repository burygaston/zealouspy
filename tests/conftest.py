"""Pytest configuration and fixtures."""

import pytest
from zealous.models.user import User, UserRole, UserStatus
from zealous.models.task import Task, TaskStatus, TaskPriority
from zealous.services.user_service import UserService
from zealous.services.task_service import TaskService


@pytest.fixture
def user_service():
    """Create a fresh UserService instance."""
    return UserService()


@pytest.fixture
def task_service():
    """Create a fresh TaskService instance."""
    return TaskService()


@pytest.fixture
def sample_user():
    """Create a sample user."""
    return User(
        id=1,
        email="test@example.com",
        name="Test User",
        role=UserRole.DEVELOPER,
        status=UserStatus.ACTIVE,
    )


@pytest.fixture
def sample_admin():
    """Create a sample admin user."""
    return User(
        id=2,
        email="admin@example.com",
        name="Admin User",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )


@pytest.fixture
def sample_task():
    """Create a sample task."""
    return Task(
        id=1,
        title="Sample Task",
        description="A sample task for testing",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
    )

"""Tests for User model - HIGH COVERAGE."""

import pytest
from datetime import datetime
from zealous.models.user import User, UserRole, UserStatus


class TestUser:
    """Test User model."""

    def test_create_user_defaults(self):
        """Test creating user with defaults."""
        user = User(email="test@example.com", name="Test User")
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.role == UserRole.DEVELOPER
        assert user.status == UserStatus.PENDING

    def test_create_user_with_role(self):
        """Test creating user with specific role."""
        user = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
        assert user.role == UserRole.ADMIN

    def test_is_admin(self):
        """Test is_admin method."""
        admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
        developer = User(email="dev@example.com", name="Dev", role=UserRole.DEVELOPER)

        assert admin.is_admin() is True
        assert developer.is_admin() is False

    def test_is_active(self):
        """Test is_active method."""
        user = User(email="test@example.com", name="Test")
        assert user.is_active() is False

        user.status = UserStatus.ACTIVE
        assert user.is_active() is True

    def test_can_manage_users(self):
        """Test can_manage_users method."""
        admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
        manager = User(email="mgr@example.com", name="Manager", role=UserRole.MANAGER)
        developer = User(email="dev@example.com", name="Dev", role=UserRole.DEVELOPER)

        assert admin.can_manage_users() is True
        assert manager.can_manage_users() is True
        assert developer.can_manage_users() is False

    def test_can_edit_tasks(self):
        """Test can_edit_tasks method."""
        developer = User(email="dev@example.com", name="Dev", role=UserRole.DEVELOPER)
        viewer = User(email="view@example.com", name="Viewer", role=UserRole.VIEWER)

        assert developer.can_edit_tasks() is True
        assert viewer.can_edit_tasks() is False

    def test_activate_user(self):
        """Test activate method."""
        user = User(email="test@example.com", name="Test")
        user.activate()

        assert user.status == UserStatus.ACTIVE
        assert user.updated_at is not None

    def test_activate_suspended_user_raises(self):
        """Test that activating suspended user raises error."""
        user = User(email="test@example.com", name="Test", status=UserStatus.SUSPENDED)

        with pytest.raises(ValueError, match="Cannot activate suspended user"):
            user.activate()

    def test_deactivate_user(self):
        """Test deactivate method."""
        user = User(email="test@example.com", name="Test", status=UserStatus.ACTIVE)
        user.deactivate()

        assert user.status == UserStatus.INACTIVE
        assert user.updated_at is not None

    def test_suspend_user(self):
        """Test suspend method."""
        user = User(email="test@example.com", name="Test", status=UserStatus.ACTIVE)
        user.suspend()

        assert user.status == UserStatus.SUSPENDED

    # NOTE: promote_to_manager and demote_to_developer are NOT tested (coverage gap)

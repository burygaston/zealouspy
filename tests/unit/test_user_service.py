"""Tests for UserService - PARTIAL COVERAGE."""

import pytest
from zealous.services.user_service import UserService
from zealous.models.user import UserRole, UserStatus


class TestUserService:
    """Test UserService."""

    def test_create_user(self):
        """Test creating a user."""
        service = UserService()
        user = service.create_user("test@example.com", "Test User")

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.status == UserStatus.PENDING

    def test_create_user_duplicate_email_raises(self):
        """Test creating user with duplicate email raises."""
        service = UserService()
        service.create_user("test@example.com", "Test User")

        with pytest.raises(ValueError, match="already exists"):
            service.create_user("test@example.com", "Another User")

    def test_get_user(self):
        """Test getting a user."""
        service = UserService()
        created = service.create_user("test@example.com", "Test User")

        user = service.get_user(created.id)
        assert user is not None
        assert user.email == "test@example.com"

    def test_get_user_not_found(self):
        """Test getting non-existent user."""
        service = UserService()
        assert service.get_user(999) is None

    def test_get_user_by_email(self):
        """Test getting user by email."""
        service = UserService()
        service.create_user("test@example.com", "Test User")

        user = service.get_user_by_email("test@example.com")
        assert user is not None

    def test_list_users(self):
        """Test listing users."""
        service = UserService()
        service.create_user("user1@example.com", "User 1")
        service.create_user("user2@example.com", "User 2")

        users = service.list_users()
        assert len(users) == 2

    def test_list_users_with_filters(self):
        """Test listing users with status filter."""
        service = UserService()
        user1 = service.create_user("user1@example.com", "User 1")
        user1.status = UserStatus.ACTIVE
        service.create_user("user2@example.com", "User 2")

        active_users = service.list_users(status=UserStatus.ACTIVE)
        assert len(active_users) == 1

    def test_delete_user(self):
        """Test deleting a user."""
        service = UserService()
        user = service.create_user("test@example.com", "Test User")

        assert service.delete_user(user.id) is True
        assert service.get_user(user.id) is None

    def test_activate_user(self):
        """Test activating a user."""
        service = UserService()
        user = service.create_user("test@example.com", "Test User")

        activated = service.activate_user(user.id)
        assert activated is not None
        assert activated.status == UserStatus.ACTIVE

    # NOTE: suspend_user, get_inactive_users, bulk_deactivate,
    # search_users, get_user_stats are NOT tested

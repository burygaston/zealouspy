"""User service - PARTIALLY TESTED."""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from ..models.user import User, UserRole, UserStatus


class UserService:
    """Business logic service for user management operations.

    Handles user lifecycle including creation, retrieval, updates, activation,
    suspension, and user analytics. Enforces email uniqueness and manages
    user status transitions.

    Attributes:
        _users: Internal dictionary mapping user IDs to User objects.
        _next_id: Counter for generating unique user IDs.
    """

    def __init__(self):
        """Initialize the user service with empty user storage."""
        self._users: Dict[int, User] = {}
        self._next_id = 1

    def create_user(self, email: str, name: str, role: UserRole = UserRole.DEVELOPER) -> User:
        """Create a new user with the specified properties.

        Ensures email uniqueness across all users. New users start with PENDING status.

        Args:
            email: User's email address (must be unique).
            name: User's display name.
            role: User role defining permissions (default: DEVELOPER).

        Returns:
            Newly created User object with assigned ID.

        Raises:
            ValueError: If a user with the specified email already exists.
        """
        # Check for duplicate email
        for user in self._users.values():
            if user.email == email:
                raise ValueError(f"User with email {email} already exists")

        user = User(
            id=self._next_id,
            email=email,
            name=name,
            role=role,
            status=UserStatus.PENDING,
        )
        self._users[self._next_id] = user
        self._next_id += 1
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            user_id: Unique identifier of the user to retrieve.

        Returns:
            User object if found, None otherwise.
        """
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address.

        Args:
            email: Email address to search for.

        Returns:
            User object if found, None otherwise.
        """
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def list_users(
        self,
        status: Optional[UserStatus] = None,
        role: Optional[UserRole] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[User]:
        """List users with optional filtering and pagination.

        Filters are applied cumulatively (AND logic). Results can be paginated
        using limit and offset parameters.

        Args:
            status: Filter by user status.
            role: Filter by user role.
            limit: Maximum number of users to return (default: 100).
            offset: Number of users to skip for pagination (default: 0).

        Returns:
            List of User objects matching the specified filters.
        """
        users = list(self._users.values())

        if status is not None:
            users = [u for u in users if u.status == status]

        if role is not None:
            users = [u for u in users if u.role == role]

        return users[offset : offset + limit]

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update specific fields of a user.

        Only updates fields that are in the allowed set. Automatically updates
        the user's updated_at timestamp.

        Args:
            user_id: Unique identifier of the user to update.
            **kwargs: Field names and new values to update. Allowed fields:
                name, email, role, status.

        Returns:
            Updated User object if found, None if user doesn't exist.
        """
        user = self.get_user(user_id)
        if user is None:
            return None

        allowed_fields = {"name", "email", "role", "status"}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user from the system.

        Args:
            user_id: Unique identifier of the user to delete.

        Returns:
            True if the user was found and deleted, False if not found.
        """
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    def activate_user(self, user_id: int) -> Optional[User]:
        """Activate a user account, changing status from PENDING to ACTIVE.

        Args:
            user_id: Unique identifier of the user to activate.

        Returns:
            Updated User object if found, None if user doesn't exist.

        Raises:
            ValueError: If trying to activate a suspended user (from User.activate()).
        """
        user = self.get_user(user_id)
        if user is None:
            return None
        user.activate()
        return user

    def suspend_user(self, user_id: int, reason: str = "") -> Optional[User]:
        """Suspend a user account, preventing access to the system.

        Logs the suspension reason for audit purposes.

        Args:
            user_id: Unique identifier of the user to suspend.
            reason: Optional reason for suspension (for audit logging).

        Returns:
            Updated User object if found, None if user doesn't exist.
        """
        user = self.get_user(user_id)
        if user is None:
            return None
        user.suspend()
        # Log suspension reason (not tested)
        self._log_suspension(user_id, reason)
        return user

    def _log_suspension(self, user_id: int, reason: str) -> None:
        """Log user suspension to audit system.

        This is an internal method that would integrate with an audit logging
        system in production.

        Args:
            user_id: ID of the user being suspended.
            reason: Reason for the suspension.
        """
        # This would log to an audit system
        pass

    def get_inactive_users(self, days: int = 30) -> List[User]:
        """Find users who haven't had any activity for a specified period.

        A user is considered inactive if their updated_at timestamp (or created_at
        if never updated) is older than the specified number of days.

        Args:
            days: Number of days of inactivity to consider (default: 30).

        Returns:
            List of User objects that have been inactive.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        inactive = []
        for user in self._users.values():
            if user.updated_at and user.updated_at < cutoff:
                inactive.append(user)
            elif user.created_at < cutoff and user.updated_at is None:
                inactive.append(user)
        return inactive

    def bulk_deactivate(self, user_ids: List[int]) -> Dict[int, bool]:
        """Deactivate multiple users in a single operation.

        Args:
            user_ids: List of user IDs to deactivate.

        Returns:
            Dictionary mapping each user_id to True (success) or False (user not found).
        """
        results = {}
        for user_id in user_ids:
            user = self.get_user(user_id)
            if user:
                user.deactivate()
                results[user_id] = True
            else:
                results[user_id] = False
        return results

    def search_users(self, query: str) -> List[User]:
        """Search for users by name or email address.

        Search is case-insensitive and matches partial strings in both name and email.

        Args:
            query: Search string to match against user names and emails.

        Returns:
            List of User objects matching the search query.
        """
        query = query.lower()
        results = []
        for user in self._users.values():
            if query in user.name.lower() or query in user.email.lower():
                results.append(user)
        return results

    def get_user_stats(self) -> Dict[str, int]:
        """Calculate comprehensive user statistics.

        Returns:
            Dictionary containing:
                - total: Total user count
                - Counts by status (active, inactive, pending, suspended)
                - Counts by role (admins, managers, developers, viewers)
        """
        stats = {
            "total": len(self._users),
            "active": 0,
            "inactive": 0,
            "pending": 0,
            "suspended": 0,
            "admins": 0,
            "managers": 0,
            "developers": 0,
            "viewers": 0,
        }

        for user in self._users.values():
            stats[user.status.value] = stats.get(user.status.value, 0) + 1
            if user.role == UserRole.ADMIN:
                stats["admins"] += 1
            elif user.role == UserRole.MANAGER:
                stats["managers"] += 1
            elif user.role == UserRole.DEVELOPER:
                stats["developers"] += 1
            else:
                stats["viewers"] += 1

        return stats

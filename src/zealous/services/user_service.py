"""User service - PARTIALLY TESTED."""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from ..models.user import User, UserRole, UserStatus


class UserService:
    """Service for managing users."""

    def __init__(self):
        self._users: Dict[int, User] = {}
        self._next_id = 1

    def create_user(self, email: str, name: str, role: UserRole = UserRole.DEVELOPER) -> User:
        """Create a new user."""
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
        """Get user by ID."""
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
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
        """List users with optional filters."""
        users = list(self._users.values())

        if status is not None:
            users = [u for u in users if u.status == status]

        if role is not None:
            users = [u for u in users if u.role == role]

        return users[offset : offset + limit]

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
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
        """Delete a user."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    def activate_user(self, user_id: int) -> Optional[User]:
        """Activate a user."""
        user = self.get_user(user_id)
        if user is None:
            return None
        user.activate()
        return user

    def suspend_user(self, user_id: int, reason: str = "") -> Optional[User]:
        """Suspend a user."""
        user = self.get_user(user_id)
        if user is None:
            return None
        user.suspend()
        # Log suspension reason (not tested)
        self._log_suspension(user_id, reason)
        return user

    def _log_suspension(self, user_id: int, reason: str) -> None:
        """Log user suspension - NOT TESTED."""
        # This would log to an audit system
        pass

    def get_inactive_users(self, days: int = 30) -> List[User]:
        """Get users inactive for specified days - NOT TESTED."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        inactive = []
        for user in self._users.values():
            if user.updated_at and user.updated_at < cutoff:
                inactive.append(user)
            elif user.created_at < cutoff and user.updated_at is None:
                inactive.append(user)
        return inactive

    def bulk_deactivate(self, user_ids: List[int]) -> Dict[int, bool]:
        """Bulk deactivate users - NOT TESTED."""
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
        """Search users by name or email - NOT TESTED."""
        query = query.lower()
        results = []
        for user in self._users.values():
            if query in user.name.lower() or query in user.email.lower():
                results.append(user)
        return results

    def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics - NOT TESTED."""
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

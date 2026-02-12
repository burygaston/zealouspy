"""User model - WELL TESTED (high coverage expected)."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class User(BaseModel):
    """User model representing a system user with role and status.

    Users progress through status states (PENDING -> ACTIVE -> INACTIVE/SUSPENDED)
    and have roles that determine their permissions in the system.

    Attributes:
        id: Unique user identifier, assigned by the system.
        email: User's email address (must be unique).
        name: User's display name.
        role: User's role defining their permissions level.
        status: Current user account status.
        created_at: Timestamp when the user was created.
        updated_at: Timestamp of the last update to user data.
    """

    id: Optional[int] = None
    email: str
    name: str
    role: UserRole = UserRole.DEVELOPER
    status: UserStatus = UserStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def is_admin(self) -> bool:
        """Check if the user has administrator privileges.

        Returns:
            True if user role is ADMIN, False otherwise.
        """
        return self.role == UserRole.ADMIN

    def is_active(self) -> bool:
        """Check if the user account is active and usable.

        Returns:
            True if user status is ACTIVE, False otherwise.
        """
        return self.status == UserStatus.ACTIVE

    def can_manage_users(self) -> bool:
        """Check if the user has permission to manage other users.

        Returns:
            True if user is ADMIN or MANAGER, False otherwise.
        """
        return self.role in (UserRole.ADMIN, UserRole.MANAGER)

    def can_edit_tasks(self) -> bool:
        """Check if the user has permission to edit tasks.

        Returns:
            True if user is not a VIEWER, False for VIEWER role.
        """
        return self.role != UserRole.VIEWER

    def activate(self) -> None:
        """Activate the user account, changing status from PENDING to ACTIVE.

        Updates the status to ACTIVE and sets updated_at timestamp.

        Raises:
            ValueError: If attempting to activate a suspended user. Suspended
                users must be handled differently (e.g., unsuspend action).
        """
        if self.status == UserStatus.SUSPENDED:
            raise ValueError("Cannot activate suspended user")
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the user account, changing status to INACTIVE.

        Sets status to INACTIVE and updates the updated_at timestamp.
        """
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.utcnow()

    def suspend(self) -> None:
        """Suspend the user account, preventing system access.

        Sets status to SUSPENDED and updates the updated_at timestamp.
        """
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    def promote_to_manager(self) -> None:
        """Promote the user to manager role.

        Updates role to MANAGER and sets updated_at timestamp.

        Raises:
            ValueError: If attempting to change an admin's role (admins cannot
                be demoted to manager).
        """
        if self.role == UserRole.ADMIN:
            raise ValueError("Cannot demote admin to manager")
        self.role = UserRole.MANAGER
        self.updated_at = datetime.utcnow()

    def demote_to_developer(self) -> None:
        """Demote the user to developer role.

        Updates role to DEVELOPER and sets updated_at timestamp.

        Raises:
            ValueError: If attempting to change an admin's role (admins cannot
                be demoted).
        """
        if self.role == UserRole.ADMIN:
            raise ValueError("Cannot demote admin")
        self.role = UserRole.DEVELOPER
        self.updated_at = datetime.utcnow()

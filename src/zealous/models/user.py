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
    id: Optional[int] = None
    email: str
    name: str
    role: UserRole = UserRole.DEVELOPER
    status: UserStatus = UserStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE

    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role in (UserRole.ADMIN, UserRole.MANAGER)

    def can_edit_tasks(self) -> bool:
        """Check if user can edit tasks."""
        return self.role != UserRole.VIEWER

    def activate(self) -> None:
        """Activate the user."""
        if self.status == UserStatus.SUSPENDED:
            raise ValueError("Cannot activate suspended user")
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the user."""
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.utcnow()

    def suspend(self) -> None:
        """Suspend the user."""
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    def promote_to_manager(self) -> None:
        """Promote user to manager role."""
        if self.role == UserRole.ADMIN:
            raise ValueError("Cannot demote admin to manager")
        self.role = UserRole.MANAGER
        self.updated_at = datetime.utcnow()

    def demote_to_developer(self) -> None:
        """Demote user to developer role."""
        if self.role == UserRole.ADMIN:
            raise ValueError("Cannot demote admin")
        self.role = UserRole.DEVELOPER
        self.updated_at = datetime.utcnow()

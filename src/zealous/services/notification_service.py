"""Notification service - COMPLETELY UNTESTED (0% coverage expected)."""

from typing import List, Dict, Optional
from datetime import datetime
import asyncio


class NotificationChannel:
    """Abstract base class for notification delivery channels.

    Subclasses must implement the send method to handle their specific
    delivery mechanism (email, SMS, Slack, etc.).
    """

    async def send(self, recipient: str, subject: str, body: str) -> bool:
        """Send a notification through this channel.

        Args:
            recipient: Destination identifier (email address, phone number, etc.).
            subject: Notification subject/title.
            body: Notification message content.

        Returns:
            True if the notification was sent successfully, False otherwise.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError


class EmailChannel(NotificationChannel):
    """Email notification channel using SMTP.

    Attributes:
        smtp_host: SMTP server hostname.
        smtp_port: SMTP server port.
        username: SMTP authentication username.
        password: SMTP authentication password.
    """

    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        """Initialize the email channel with SMTP configuration.

        Args:
            smtp_host: SMTP server hostname.
            smtp_port: SMTP server port.
            username: SMTP authentication username.
            password: SMTP authentication password.
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    async def send(self, recipient: str, subject: str, body: str) -> bool:
        """Send an email notification.

        Args:
            recipient: Email address to send to.
            subject: Email subject line.
            body: Email body content.

        Returns:
            True if email was sent successfully.
        """
        # Simulate email sending
        await asyncio.sleep(0.1)
        return True


class SlackChannel(NotificationChannel):
    """Slack notification channel using webhooks.

    Attributes:
        webhook_url: Slack webhook URL for posting messages.
    """

    def __init__(self, webhook_url: str):
        """Initialize the Slack channel with webhook configuration.

        Args:
            webhook_url: Slack webhook URL for posting messages.
        """
        self.webhook_url = webhook_url

    async def send(self, recipient: str, subject: str, body: str) -> bool:
        """Send a Slack notification via webhook.

        Args:
            recipient: Slack channel or user identifier.
            subject: Message title.
            body: Message content.

        Returns:
            True if message was posted successfully.
        """
        # Simulate Slack API call
        await asyncio.sleep(0.05)
        return True


class SMSChannel(NotificationChannel):
    """SMS notification channel using SMS API.

    Attributes:
        api_key: API key for SMS service authentication.
        from_number: Phone number to send messages from.
    """

    def __init__(self, api_key: str, from_number: str):
        """Initialize the SMS channel with API configuration.

        Args:
            api_key: API key for SMS service authentication.
            from_number: Phone number to send messages from.
        """
        self.api_key = api_key
        self.from_number = from_number

    async def send(self, recipient: str, subject: str, body: str) -> bool:
        """Send an SMS notification.

        Args:
            recipient: Phone number to send to.
            subject: Message subject (may be ignored depending on SMS provider).
            body: SMS message content.

        Returns:
            True if SMS was sent successfully.
        """
        # Simulate SMS API call
        await asyncio.sleep(0.2)
        return True


class NotificationService:
    """Multi-channel notification service with user preferences and history.

    Manages notification delivery across multiple channels (email, SMS, Slack, etc.)
    with user-specific preferences, delivery tracking, and statistics.

    Attributes:
        _channels: Dictionary of registered notification channels by name.
        _notification_history: List of all sent notifications with results.
        _preferences: User-specific channel preferences.
    """

    def __init__(self):
        """Initialize the notification service with empty state."""
        self._channels: Dict[str, NotificationChannel] = {}
        self._notification_history: List[Dict] = []
        self._preferences: Dict[str, List[str]] = {}

    def register_channel(self, name: str, channel: NotificationChannel) -> None:
        """Register a notification channel for use by the service.

        Args:
            name: Unique identifier for the channel (e.g., "email", "slack").
            channel: NotificationChannel instance to register.
        """
        self._channels[name] = channel

    def unregister_channel(self, name: str) -> bool:
        """Remove a notification channel from the service.

        Args:
            name: Identifier of the channel to unregister.

        Returns:
            True if the channel was found and removed, False otherwise.
        """
        if name in self._channels:
            del self._channels[name]
            return True
        return False

    def set_user_preferences(self, user_id: str, channels: List[str]) -> None:
        """Set which notification channels a user wants to receive notifications on.

        Args:
            user_id: Unique identifier for the user.
            channels: List of channel names the user wants to use.
        """
        self._preferences[user_id] = channels

    def get_user_preferences(self, user_id: str) -> List[str]:
        """Get a user's preferred notification channels.

        Args:
            user_id: Unique identifier for the user.

        Returns:
            List of channel names, defaults to ["email"] if not set.
        """
        return self._preferences.get(user_id, ["email"])

    async def send_notification(
        self,
        user_id: str,
        subject: str,
        body: str,
        recipient: str,
        channels: Optional[List[str]] = None,
    ) -> Dict[str, bool]:
        """Send a notification to a user via one or more channels.

        Uses the user's preferred channels if none are specified. Logs all
        delivery attempts to notification history.

        Args:
            user_id: Unique identifier for the user.
            subject: Notification subject/title.
            body: Notification message content.
            recipient: Delivery address (email, phone, etc.).
            channels: Optional list of specific channels to use, defaults to
                user preferences if not provided.

        Returns:
            Dictionary mapping each channel name to True (success) or False (failure).
        """
        if channels is None:
            channels = self.get_user_preferences(user_id)

        results = {}
        for channel_name in channels:
            if channel_name not in self._channels:
                results[channel_name] = False
                continue

            channel = self._channels[channel_name]
            try:
                success = await channel.send(recipient, subject, body)
                results[channel_name] = success
            except Exception:
                results[channel_name] = False

        # Log notification
        self._notification_history.append({
            "user_id": user_id,
            "subject": subject,
            "channels": channels,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return results

    async def send_bulk_notification(
        self,
        user_ids: List[str],
        subject: str,
        body: str,
        recipients: Dict[str, str],
    ) -> Dict[str, Dict[str, bool]]:
        """Send the same notification to multiple users.

        Args:
            user_ids: List of user IDs to send notifications to.
            subject: Notification subject/title.
            body: Notification message content.
            recipients: Dictionary mapping user IDs to their delivery addresses.

        Returns:
            Dictionary mapping each user_id to their delivery results (dict of
            channel names to success/failure booleans).
        """
        results = {}
        tasks = []

        for user_id in user_ids:
            recipient = recipients.get(user_id, "")
            if recipient:
                task = self.send_notification(user_id, subject, body, recipient)
                tasks.append((user_id, task))

        for user_id, task in tasks:
            results[user_id] = await task

        return results

    def get_notification_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Retrieve notification history, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter history to a specific user.
            limit: Maximum number of history entries to return (default: 100).

        Returns:
            List of notification history dictionaries, most recent last.
        """
        history = self._notification_history
        if user_id:
            history = [n for n in history if n["user_id"] == user_id]
        return history[-limit:]

    def get_delivery_stats(self) -> Dict[str, Dict[str, int]]:
        """Calculate delivery statistics across all channels.

        Returns:
            Dictionary mapping channel names to their stats:
                - sent: Number of successful deliveries
                - failed: Number of failed deliveries
        """
        stats: Dict[str, Dict[str, int]] = {}

        for notification in self._notification_history:
            for channel, success in notification["results"].items():
                if channel not in stats:
                    stats[channel] = {"sent": 0, "failed": 0}
                if success:
                    stats[channel]["sent"] += 1
                else:
                    stats[channel]["failed"] += 1

        return stats

    async def send_task_assigned_notification(
        self,
        assignee_email: str,
        task_title: str,
        assigner_name: str,
    ) -> bool:
        """Send a notification when a task is assigned to a user.

        Convenience method for the common task assignment notification pattern.

        Args:
            assignee_email: Email address of the user being assigned the task.
            task_title: Title of the task being assigned.
            assigner_name: Name of the person who assigned the task.

        Returns:
            True if at least one channel delivered successfully, False otherwise.
        """
        subject = f"New Task Assigned: {task_title}"
        body = f"You have been assigned a new task by {assigner_name}: {task_title}"
        results = await self.send_notification(
            user_id=assignee_email,
            subject=subject,
            body=body,
            recipient=assignee_email,
        )
        return any(results.values())

    async def send_task_due_reminder(
        self,
        assignee_email: str,
        task_title: str,
        due_date: str,
    ) -> bool:
        """Send a reminder notification for an upcoming task due date.

        Convenience method for task due date reminders.

        Args:
            assignee_email: Email address of the task assignee.
            task_title: Title of the task that's due soon.
            due_date: Formatted due date string.

        Returns:
            True if at least one channel delivered successfully, False otherwise.
        """
        subject = f"Task Due Soon: {task_title}"
        body = f"Your task '{task_title}' is due on {due_date}"
        results = await self.send_notification(
            user_id=assignee_email,
            subject=subject,
            body=body,
            recipient=assignee_email,
        )
        return any(results.values())

    async def send_project_update(
        self,
        member_emails: List[str],
        project_name: str,
        update_message: str,
    ) -> int:
        """Broadcast a project update to all team members.

        Convenience method for sending the same update to multiple project members.

        Args:
            member_emails: List of email addresses for project team members.
            project_name: Name of the project being updated.
            update_message: The update message to send.

        Returns:
            Number of users who received the notification successfully on at least
            one channel.
        """
        subject = f"Project Update: {project_name}"
        recipients = {email: email for email in member_emails}
        results = await self.send_bulk_notification(
            user_ids=member_emails,
            subject=subject,
            body=update_message,
            recipients=recipients,
        )
        return sum(1 for r in results.values() if any(r.values()))

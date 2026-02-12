"""API middleware - COMPLETELY UNTESTED (0% coverage)."""

from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib


class AuthMiddleware:
    """Session-based authentication middleware.

    Manages user sessions with token-based authentication, including session
    creation, validation, revocation, and automatic cleanup of expired sessions.

    Attributes:
        secret_key: Secret key used for token generation.
        _sessions: Internal dictionary storing active sessions keyed by token.
    """

    def __init__(self, secret_key: str):
        """Initialize the authentication middleware.

        Args:
            secret_key: Secret key used to generate secure session tokens.
        """
        self.secret_key = secret_key
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, user_id: int, expires_in: int = 3600) -> str:
        """Create a new authenticated session for a user.

        Args:
            user_id: Unique identifier of the user.
            expires_in: Session lifetime in seconds (default: 3600 = 1 hour).

        Returns:
            Generated session token string.
        """
        token = hashlib.sha256(
            f"{user_id}{datetime.utcnow().isoformat()}{self.secret_key}".encode()
        ).hexdigest()

        self._sessions[token] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
        }

        return token

    def validate_session(self, token: str) -> Optional[int]:
        """Validate a session token and return the associated user ID.

        Automatically removes expired sessions during validation.

        Args:
            token: Session token to validate.

        Returns:
            User ID if the session is valid and not expired, None otherwise.
        """
        session = self._sessions.get(token)
        if session is None:
            return None

        if datetime.utcnow() > session["expires_at"]:
            del self._sessions[token]
            return None

        return session["user_id"]

    def revoke_session(self, token: str) -> bool:
        """Revoke a specific session, invalidating the token.

        Args:
            token: Session token to revoke.

        Returns:
            True if the session was found and revoked, False if token not found.
        """
        if token in self._sessions:
            del self._sessions[token]
            return True
        return False

    def revoke_all_sessions(self, user_id: int) -> int:
        """Revoke all active sessions for a specific user.

        Useful for forced logout scenarios or security incidents.

        Args:
            user_id: Unique identifier of the user whose sessions to revoke.

        Returns:
            Number of sessions that were revoked.
        """
        tokens_to_remove = [
            token for token, session in self._sessions.items()
            if session["user_id"] == user_id
        ]
        for token in tokens_to_remove:
            del self._sessions[token]
        return len(tokens_to_remove)

    def cleanup_expired_sessions(self) -> int:
        """Remove all expired sessions from storage.

        Should be called periodically to prevent memory leaks.

        Returns:
            Number of expired sessions that were removed.
        """
        now = datetime.utcnow()
        tokens_to_remove = [
            token for token, session in self._sessions.items()
            if now > session["expires_at"]
        ]
        for token in tokens_to_remove:
            del self._sessions[token]
        return len(tokens_to_remove)


class RateLimitMiddleware:
    """Rate limiting middleware using sliding window algorithm.

    Tracks request counts per client to enforce rate limits and prevent abuse.
    Uses a sliding window approach where old requests are automatically cleaned up.

    Attributes:
        requests_per_minute: Maximum number of requests allowed per client per minute.
        _request_counts: Internal dictionary storing request timestamps per client.
    """

    def __init__(self, requests_per_minute: int = 60):
        """Initialize the rate limiting middleware.

        Args:
            requests_per_minute: Maximum requests allowed per client per minute
                (default: 60).
        """
        self.requests_per_minute = requests_per_minute
        self._request_counts: Dict[str, list] = defaultdict(list)

    def is_rate_limited(self, client_id: str) -> bool:
        """Check if a client has exceeded the rate limit.

        This method automatically cleans up old requests, checks the limit, and
        records the current request if not rate limited.

        Args:
            client_id: Unique identifier for the client (e.g., IP address, user ID).

        Returns:
            True if the client is rate limited, False if the request is allowed.
        """
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)

        # Clean old requests
        self._request_counts[client_id] = [
            ts for ts in self._request_counts[client_id]
            if ts > minute_ago
        ]

        # Check limit
        if len(self._request_counts[client_id]) >= self.requests_per_minute:
            return True

        # Record request
        self._request_counts[client_id].append(now)
        return False

    def get_remaining_requests(self, client_id: str) -> int:
        """Get the number of remaining requests available for a client.

        Args:
            client_id: Unique identifier for the client.

        Returns:
            Number of requests remaining in the current window (0 or positive).
        """
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)

        current_count = len([
            ts for ts in self._request_counts[client_id]
            if ts > minute_ago
        ])

        return max(0, self.requests_per_minute - current_count)

    def reset_client(self, client_id: str) -> None:
        """Reset the rate limit counter for a specific client.

        Useful for administrative actions or testing scenarios.

        Args:
            client_id: Unique identifier for the client to reset.
        """
        if client_id in self._request_counts:
            del self._request_counts[client_id]

    def get_stats(self) -> Dict[str, Any]:
        """Get current rate limiting statistics across all clients.

        Returns:
            Dictionary containing:
                - active_clients: Number of clients with requests in the last minute
                - total_requests_last_minute: Total request count across all clients
                - limit_per_minute: Configured rate limit
        """
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)

        active_clients = 0
        total_requests = 0

        for client_id, timestamps in self._request_counts.items():
            recent = [ts for ts in timestamps if ts > minute_ago]
            if recent:
                active_clients += 1
                total_requests += len(recent)

        return {
            "active_clients": active_clients,
            "total_requests_last_minute": total_requests,
            "limit_per_minute": self.requests_per_minute,
        }


class LoggingMiddleware:
    """Request logging middleware for tracking and analyzing API requests.

    Captures request details including timing, status codes, and paths. Provides
    both detailed logs and aggregate statistics for monitoring and debugging.

    Attributes:
        log_function: Callable used to output log messages (default: print).
        _request_log: Internal list storing request log entries.
    """

    def __init__(self, log_function: Optional[Callable] = None):
        """Initialize the logging middleware.

        Args:
            log_function: Optional callable for outputting logs. Defaults to print
                if not provided.
        """
        self.log_function = log_function or print
        self._request_log: list = []

    def log_request(
        self,
        method: str,
        path: str,
        client_id: str,
        status: int,
        duration_ms: float,
    ) -> None:
        """Log a completed API request with its details.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            path: Request path/endpoint.
            client_id: Unique identifier for the client making the request.
            status: HTTP status code returned.
            duration_ms: Request processing time in milliseconds.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "path": path,
            "client_id": client_id,
            "status": status,
            "duration_ms": duration_ms,
        }

        self._request_log.append(entry)
        self.log_function(
            f"[{entry['timestamp']}] {method} {path} - {status} ({duration_ms:.2f}ms)"
        )

    def get_recent_requests(self, limit: int = 100) -> list:
        """Retrieve the most recent request log entries.

        Args:
            limit: Maximum number of entries to return (default: 100).

        Returns:
            List of log entry dictionaries, most recent last.
        """
        return self._request_log[-limit:]

    def get_request_stats(self) -> Dict[str, Any]:
        """Calculate aggregate statistics from the request log.

        Returns:
            Dictionary containing:
                - total_requests: Total number of logged requests
                - avg_duration_ms: Average request duration
                - min_duration_ms: Fastest request duration
                - max_duration_ms: Slowest request duration
                - error_rate: Proportion of requests with status >= 400
        """
        if not self._request_log:
            return {
                "total_requests": 0,
                "avg_duration_ms": 0,
                "error_rate": 0,
            }

        total = len(self._request_log)
        durations = [r["duration_ms"] for r in self._request_log]
        errors = len([r for r in self._request_log if r["status"] >= 400])

        return {
            "total_requests": total,
            "avg_duration_ms": sum(durations) / total,
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "error_rate": errors / total if total > 0 else 0,
        }

    def clear_log(self) -> int:
        """Clear all entries from the request log.

        Returns:
            Number of log entries that were cleared.
        """
        count = len(self._request_log)
        self._request_log = []
        return count

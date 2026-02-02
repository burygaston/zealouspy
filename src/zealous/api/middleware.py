"""API middleware - COMPLETELY UNTESTED (0% coverage)."""

from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib


class AuthMiddleware:
    """Authentication middleware."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, user_id: int, expires_in: int = 3600) -> str:
        """Create a new session."""
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
        """Validate session and return user_id."""
        session = self._sessions.get(token)
        if session is None:
            return None

        if datetime.utcnow() > session["expires_at"]:
            del self._sessions[token]
            return None

        return session["user_id"]

    def revoke_session(self, token: str) -> bool:
        """Revoke a session."""
        if token in self._sessions:
            del self._sessions[token]
            return True
        return False

    def revoke_all_sessions(self, user_id: int) -> int:
        """Revoke all sessions for a user."""
        tokens_to_remove = [
            token for token, session in self._sessions.items()
            if session["user_id"] == user_id
        ]
        for token in tokens_to_remove:
            del self._sessions[token]
        return len(tokens_to_remove)

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions."""
        now = datetime.utcnow()
        tokens_to_remove = [
            token for token, session in self._sessions.items()
            if now > session["expires_at"]
        ]
        for token in tokens_to_remove:
            del self._sessions[token]
        return len(tokens_to_remove)


class RateLimitMiddleware:
    """Rate limiting middleware."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._request_counts: Dict[str, list] = defaultdict(list)

    def is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited."""
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
        """Get remaining requests for client."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)

        current_count = len([
            ts for ts in self._request_counts[client_id]
            if ts > minute_ago
        ])

        return max(0, self.requests_per_minute - current_count)

    def reset_client(self, client_id: str) -> None:
        """Reset rate limit for a client."""
        if client_id in self._request_counts:
            del self._request_counts[client_id]

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
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
    """Request logging middleware."""

    def __init__(self, log_function: Optional[Callable] = None):
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
        """Log a request."""
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
        """Get recent requests."""
        return self._request_log[-limit:]

    def get_request_stats(self) -> Dict[str, Any]:
        """Get request statistics."""
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
        """Clear request log."""
        count = len(self._request_log)
        self._request_log = []
        return count

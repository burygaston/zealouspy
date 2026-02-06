"""Slow test demonstration for testing timeout policies."""

import time
import pytest


def test_slow_analytics_process():
    """Simulate a slow-running integration or heavy processing test."""
    time.sleep(3)
    assert True

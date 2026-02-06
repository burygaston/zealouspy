"""Flaky test demonstration - these tests intentionally have non-deterministic behavior.

This module contains tests that will randomly pass or fail to demonstrate CI flake detection.
"""

import pytest
import random
import time
from datetime import datetime


class TestFlakyBehavior:
    """Tests that demonstrate flaky behavior - will randomly pass or fail."""

    def test_random_flaky(self):
        """This test fails ~30% of the time due to random chance."""
        random_value = random.random()
        # Fails when random value is below 0.3 (roughly 30% of runs)
        assert random_value > 0.3, f"Flaky failure! Random value was {random_value}"

    def test_timing_flaky(self):
        """This test is sensitive to timing and may flake under load."""
        start = time.perf_counter()

        # Simulate some work with variable duration
        time.sleep(random.uniform(0.001, 0.015))

        elapsed = time.perf_counter() - start
        # This threshold is tight enough to occasionally fail
        assert elapsed < 0.01, f"Timing flake! Took {elapsed:.4f}s"

    def test_microsecond_race(self):
        """This test depends on microsecond timing - classic flakiness source."""
        timestamp1 = datetime.utcnow()
        timestamp2 = datetime.utcnow()

        # Sometimes these are equal, sometimes not - depends on execution speed
        # Fails roughly 20-40% of the time depending on system load
        assert timestamp1 != timestamp2, "Timestamps were identical - timing flake!"
# Trigger test 1770342025

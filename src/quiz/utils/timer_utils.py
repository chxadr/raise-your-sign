"""Monotonic timer utilities.

This module provides a simple monotonic timer class useful for implementing
delays, cooldowns and stability checks without blocking execution loops.
"""

import time


class Timer:
    """A simple monotonic timer for non-blocking time tracking.

    The timer uses `time.monotonic()` to ensure reliable duration measurement
    that is unaffected by system clock changes.

    Attributes:
        duration: The total duration of the timer in seconds.
        _start: The monotonic start time in seconds, or None
            if the timer is not running.
    """

    def __init__(self, duration: float):
        """Initialize the timer with a fixed duration.

        Args:
            duration: The timer duration in seconds.
        """
        self.duration = duration
        self._start = None

    def start(self) -> None:
        """Start or restart the timer.

        This records the current monotonic time as the start point.
        """
        self._start = time.monotonic()

    def reset(self) -> None:
        """Reset the timer to start from the current time.

        This is an alias for `start()`.
        """
        self.start()

    def stop(self) -> None:
        """Stop the timer and clear its start time."""
        self._start = None

    def running(self) -> bool:
        """Check whether the timer is currently running.

        Returns:
            True if the timer has been started and not stopped
            otherwise False.
        """
        return self._start is not None

    def expired(self) -> bool:
        """Determine whether the timer duration has elapsed.

        Returns:
            True if the timer is running and the elapsed time is greater than
            or equal to the configured duration, False otherwise.
        """
        return (
            self._start is not None
            and time.monotonic() - self._start >= self.duration
        )

    def remaining(self) -> float:
        """Get the remaining time before expiration.

        Returns:
            The remaining time in seconds. Returns 0.0 if the timer is stopped
            or has already expired.
        """
        if self._start is None:
            return 0.0
        return max(0.0, self.duration - (time.monotonic() - self._start))

    def progress(self) -> float:
        """Get the normalized progress of the timer.

        Returns:
            A float between 0.0 and 1.0 representing how much of the duration
            has elapsed. Returns 0.0 if the timer is not running.
        """
        if self._start is None:
            return 0.0
        return min(1.0, (
            time.monotonic() - self._start) / self.duration
        )

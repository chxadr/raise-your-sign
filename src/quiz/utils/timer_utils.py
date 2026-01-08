import time


class Timer:
    """Simple monotonic timer.

    Useful for delays, cooldowns and stability checks without blocking loops.
    """

    def __init__(self, duration: float):
        """
        Args:
            duration: Duration in seconds.
        """
        self.duration = duration
        self._start = None

    def start(self) -> None:
        """Start or restart the timer."""
        self._start = time.monotonic()

    def reset(self) -> None:
        """Reset the timer (alias for start)."""
        self.start()

    def stop(self) -> None:
        """Stop the timer."""
        self._start = None

    def running(self) -> bool:
        """Return True if the timer is running."""
        return self._start is not None

    def expired(self) -> bool:
        """Return True if the timer has expired."""
        return (
            self._start is not None
            and time.monotonic() - self._start >= self.duration
        )

    def remaining(self) -> float:
        """Return remaining time in seconds (0 if expired or stopped)."""
        if self._start is None:
            return 0.0
        return max(0.0, self.duration - (time.monotonic() - self._start))

    def progress(self) -> float:
        """Return progress in range 0.0 to 1.0."""
        if self._start is None:
            return 0.0
        return min(1.0, (
            time.monotonic() - self._start) / self.duration
        )

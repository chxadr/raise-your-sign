"""Abstract event listener interface for quiz systems.

This module defines the `QuizListener` abstract base class which
represents the Listener component in an MVC-based quiz architecture.
Listeners react to quiz events emitted by the model and can be used to
update views, trigger side effects or log quiz activity.
"""

from quiz.core.quiz_event import QuizEvent

from abc import ABC, abstractmethod
from typing import Any


class QuizListener(ABC):
    """Abstract base class for reacting to quiz events.

    Implementations of this class receive notifications when quiz events
    occur and define how those events should be handled.
    """

    @abstractmethod
    def on_event(self, e: QuizEvent, args: Any | None = None) -> None:
        """Handle a quiz event.

        Args:
            e: The quiz event that occurred.
            args: Optional event-specific data which may be processed.
        """
        pass

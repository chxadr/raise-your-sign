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

    Attributes:
         label_names: Optional list of names used to label answer
                options (e.g. ["Green", "Red", "Yellow"]).
    """

    def __init__(self, label_names: list[str] | None = None, **kwargs):
        """Initialize the quiz listener."""
        super().__init__(**kwargs)
        self.label_names = label_names

    def set_answer_labels(self, label_names: list[str]):
        """Optional list of names used to label answer

        Args:
            label_names: Optional list of names used to label answer
                options (e.g. ["Green", "Red", "Yellow"]).
        """
        self.label_names = label_names

    @abstractmethod
    def on_event(self, e: QuizEvent, args: Any | None = None) -> None:
        """Handle a quiz event.

        Args:
            e: The quiz event that occurred.
            args: Optional event-specific data which may be processed.
        """
        pass

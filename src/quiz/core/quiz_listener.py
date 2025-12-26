from abc import ABC, abstractmethod
from quiz.core.quiz_event import QuizEvent


class QuizListener(ABC):

    @abstractmethod
    def on_event(self, e: QuizEvent, args: list[str] | None = None) -> None:
        """React to quiz events."""
        pass

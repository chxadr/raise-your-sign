"""Abstract quiz model definition for MVC-based quiz systems.

This module defines the `QuizModel` abstract base class
which represents the Model component in an MVC architecture.
The model is responsible for maintaining quiz state, managing players,
handling questions and answers and notifying listeners of quiz-related events.
"""

from quiz.core.quiz_listener import QuizListener
from quiz.core.quiz_event import QuizEvent

from abc import ABC, abstractmethod
from typing import Any


class QuizModel(ABC):
    """Abstract base class representing a quiz model.

    The quiz model encapsulates quiz data and state, including players,
    questions, answers and quiz progression. It also manages event listeners
    and emits events to notify other components (such as controllers or views)
    about changes in quiz state.

    Subclasses must implement the abstract methods to define concrete quiz
    behavior.

    Attributes:
        listeners: Registered listeners that will be notified of quiz events.
        quiz_file: Reference to the quiz definition source.
        output_file: Reference to the output destination for quiz results.
        players: Object representing all players participating in the quiz.
    """

    def __init__(self, **kwargs):
        """Initialize the quiz model."""
        super().__init__(**kwargs)
        self.listeners: list[QuizListener] = []
        self.quiz_file: Any | None = None
        self.output_file: Any | None = None
        self.players: Any | None = None

    def requires_players(self):
        if self.players is None:
            raise RuntimeError("QuizModel.players must be set before use")

    def set_players(self, players: Any):
        """Set players for the quiz.

        Args:
            players: Players for the quiz.
        """
        self.players = players

    def notify_listeners(self, e: QuizEvent,
                         args: Any | None = None) -> None:
        """Notify all registered listeners of a quiz event.

        Args:
            e: The quiz event to emit.
            arg: Optional event-specific arguments the listeners may process.
        """
        for listener in self.listeners:
            listener.on_event(e, args)

    def add_listener(self,
                     listener: QuizListener | list[QuizListener]) -> None:
        """Add one or more listeners to the quiz model.

        Args:
            listener: A single `QuizListener` instance or a list of
                listeners to register.
        """
        if isinstance(listener, list):
            self.listeners += listener
        else:
            self.listeners.append(listener)

    def begin(self) -> None:
        """Signal the beginning of the quiz."""
        self.notify_listeners(QuizEvent.BEGIN)

    def end(self, args: Any | None = None) -> None:
        """Signal the end of the quiz.

        Args:
            args: Optional data associated with the end of the quiz.
        """
        self.notify_listeners(QuizEvent.END, args)

    def inform_player(self, args: Any) -> None:
        """Send informational messages to players.

        Args:
            args: Informational data for players.
        """
        self.notify_listeners(QuizEvent.INFO, args)

    def set_quiz_file(self, path: str) -> None:
        """Set the path to the quiz definition file.

        Args:
            path: Path to the quiz file.
        """
        self.quiz_file = path

    @abstractmethod
    def get_player_name(self) -> str:
        """Return the name of the current player.

        Returns:
            The name of the current player.
        """
        pass

    @abstractmethod
    def get_question(self) -> Any:
        """Return the current quiz question.

        Returns:
            The current question.
        """
        pass

    @abstractmethod
    def get_options(self) -> Any:
        """Return the available answer options for the current question.

        Returns:
            All possible answer options.
        """
        pass

    @abstractmethod
    def record_answer(self, answer: Any) -> None:
        """Record an answer for the current player and question.

        Args:
            answer: Something representing the selected answer option.
        """
        pass

    @abstractmethod
    def next_question(self) -> bool:
        """Advance to the next question.

        Returns:
            True if a next question exists, False otherwise.
        """
        pass

    @abstractmethod
    def ask_next_player(self) -> bool:
        """Advance to the next player for the current question.

        Returns:
            True if a next player exists, False otherwise.
        """
        pass

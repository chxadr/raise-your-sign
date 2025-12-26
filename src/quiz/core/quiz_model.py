from quiz.core.quiz_listener import QuizListener
from quiz.core.quiz_event import QuizEvent
from abc import ABC, abstractmethod


class QuizModel(ABC):

    def __init__(self, quiz_file: str, player_names: list[str]):
        self.listeners: list[QuizListener] = []
        self.quiz_file: str = quiz_file
        self.player_names = player_names

    def notify_listeners(self, e: QuizEvent, arg: str | None = None) -> None:
        for listener in self.listeners:
            listener.on_event(e, arg)

    def add_listener(self,
                     listener: QuizListener | list[QuizListener]) -> None:
        """Add one or many listeners to the quiz."""
        if isinstance(listener, list):
            self.listeners += listener
        else:
            self.listeners.append(listener)

    def begin(self) -> None:
        self.notify_listeners(QuizEvent.BEGIN)

    def end(self) -> None:
        self.notify_listeners(QuizEvent.END)

    def inform_player(self, args: list[str]) -> None:
        self.notify_listeners(QuizEvent.INFO, args)

    @abstractmethod
    def get_player_name(self) -> str:
        """Return all player names as a list."""
        pass

    @abstractmethod
    def get_question(self) -> str:
        """Return the current question."""
        pass

    @abstractmethod
    def get_options(self) -> list[str]:
        """Return the current available options."""
        pass

    @abstractmethod
    def record_answer(self, answer_index: int) -> None:
        """Record the answer for a specific player and question."""
        pass

    @abstractmethod
    def next_question(self) -> bool:
        """Go to the next question"""
        pass

    @abstractmethod
    def ask_next_player(self) -> bool:
        """Ask the next player to answer a specific question."""
        pass

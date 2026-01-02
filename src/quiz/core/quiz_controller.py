"""Abstract controller interface for quiz systems.

This module defines the `QuizController` abstract base class which
represents the Controller component in an MVC-based quiz architecture.
Controllers coordinate the interaction between the quiz model and the
outside world such as user interfaces or input mechanisms.
"""

from quiz.core.quiz_model import QuizModel
from abc import ABC, abstractmethod


class QuizController(ABC):
    """Abstract base class for controlling quiz execution.

    The controller is responsible for driving the quiz flow, invoking
    operations on the model and handling user interaction logic.

    Attributes:
        quiz: The quiz model instance to control.
    """

    def __init__(self, quiz: QuizModel):
        """Initialize the quiz controller.

        Args:
            quiz: The quiz model instance to control.
        """
        self.quiz = quiz

    @abstractmethod
    def run_quiz(self) -> None:
        """Run the quiz.

        This method defines the main execution loop or workflow of the quiz.
        Concrete implementations may determine how the quiz is started,
        progressed and terminated.
        """
        pass

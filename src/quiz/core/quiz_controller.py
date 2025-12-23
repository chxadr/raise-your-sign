from abc import ABC, abstractmethod


class QuizControllerInterface(ABC):
    @abstractmethod
    def start_quiz(self):
        """Start the quiz and handle user input."""
        pass

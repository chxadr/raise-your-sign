from quiz.core.quiz_model import QuizModel
from abc import ABC, abstractmethod


class QuizController(ABC):

    def __init__(self, quiz: QuizModel):
        self.quiz = quiz

    @abstractmethod
    def run_quiz(self):
        """Run the quiz."""
        pass

from abc import ABC, abstractmethod


class QuizViewInterface(ABC):
    @abstractmethod
    def display_question(self, question, options=None):
        """Display a question with options."""
        pass

    @abstractmethod
    def get_player_answer(self, player, question):
        """Ask the player for an answer."""
        pass

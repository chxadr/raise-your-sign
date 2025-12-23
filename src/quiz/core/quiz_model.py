from abc import ABC, abstractmethod


class QuizModelInterface(ABC):
    @abstractmethod
    def load_quiz_data(self):
        """Load quiz data from a JSON file."""
        pass

    @abstractmethod
    def get_question(self, index):
        """Return the question at a specific index."""
        pass

    @abstractmethod
    def record_answer(self, player, question_index, answer):
        """Record the answer for a specific player and question."""
        pass

    @abstractmethod
    def save_answers_to_csv(self, output_file):
        """Save the answers to a CSV file."""
        pass

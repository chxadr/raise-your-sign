from quiz.core import QuizViewInterface


class QuizViewTUI(QuizViewInterface):
    def display_question(self, question, options=None):
        """Display a question with options."""
        print(f"Question: {question}")
        if options:
            for idx, option in enumerate(options, 1):
                print(f"{idx}. {option}")

    def get_player_answer(self, player, question):
        """Ask the player for an answer."""
        answer = input(f"{player}, enter your answer (yes/no or a/b/c/d): ").strip()
        return answer

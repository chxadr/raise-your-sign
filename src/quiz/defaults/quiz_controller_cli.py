from quiz.core.quiz_controller import QuizController
from typing import override


continue_str = "\nPress ENTER to continue"


class QuizControllerCLI(QuizController):

    def wait_player(self):
        self.quiz.inform_player([continue_str])
        input()

    @override
    def run_quiz(self):
        """Run the quiz."""
        self.quiz.begin()
        self.wait_player()

        while self.quiz.next_question():
            n_opts = len(self.quiz.get_options())

            while self.quiz.ask_next_player():
                player = self.quiz.get_player_name()

                while True:
                    self.quiz.inform_player([
                        f"{player}, enter your answer digit:"
                    ])
                    answer = input()
                    if answer.isdigit() and 1 <= int(answer) <= n_opts:
                        answer_index = int(answer) - 1
                        self.quiz.record_answer(answer_index)
                        break
                    self.quiz.inform_player([
                        f"Input a digit within the range 1-{n_opts}"
                    ])
                    continue

        self.wait_player()

        self.quiz.end()

"""Command-line interface (CLI) quiz controller.

This module provides a concrete implementation of the `QuizController`
abstract base class. It drives the quiz flow in the terminal, interacting
with players via input prompts, validating responses and coordinating
quiz events with the quiz model.
"""

from quiz.core.quiz_controller import QuizController
from quiz.core.quiz_model import QuizModel

from typing import override
import os


class QuizControllerCLI(QuizController):
    """CLI-based quiz controller that manages quiz flow in the terminal."""

    def __init__(self, quiz: QuizModel):
        super().__init__(quiz)

    def wait_player(self):
        """Pause the quiz until the player presses ENTER."""
        self.quiz.inform_player(["\nPress ENTER to continue"])
        input()

    @override
    def run_quiz(self):
        """Run the quiz, handling file selection, questions, and player input.

        Workflow:
            1. Prompt the user for a JSONL quiz file and validate it.
            2. Iterate over questions.
            3. Iterate over players for each question.
            4. Validate player input and record answers.
            5. Handle KeyboardInterrupt to allow graceful exit.
        """
        try:
            self.quiz.begin()
            while True:
                # Ask for a JSONL file.
                self.quiz.inform_player(["Specify a quiz file (.jsonl): "])
                path = input()
                if os.path.isfile(path) \
                        and os.access(path, os.R_OK) \
                        and path.endswith('.jsonl'):
                    # The file has the a `.jsonl` extension and is readable.
                    self.quiz.set_quiz_file(path)
                    self.wait_player()
                    break
                # Ask for a file again.
                self.quiz.inform_player(["Invalid path or file extension"])

            while self.quiz.next_question():
                # A question is available.
                n_opts = len(self.quiz.get_options())

                while self.quiz.ask_next_player():
                    # A player is available.
                    player = self.quiz.get_player_name()

                    while True:
                        # Ask the player to answer with a valid option number.
                        self.quiz.inform_player([
                            f"{player}, enter your answer number:"
                        ])
                        answer = input()
                        if answer.isdigit() and 1 <= int(answer) <= n_opts:
                            # The answered option number is valid.
                            answer_index = int(answer) - 1
                            self.quiz.record_answer(answer_index)
                            break
                        # Ask for a valid number again.
                        self.quiz.inform_player([
                            f"Input a number within the range 1-{n_opts}"
                        ])

            self.quiz.end([self.quiz.output_file])
            self.wait_player()

        except KeyboardInterrupt:
            self.quiz.inform_player(["\nQuiz exited with ^C"])
            return

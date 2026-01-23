"""Default quiz model implementation using JSONL files and CSV results.

This module provides a concrete implementation of the `QuizModel`
abstract base class. It loads questions from a JSONL file, tracks players
and their answers and writes results to a CSV file. It also emits quiz
events to registered listeners during the quiz lifecycle.

Quiz JSONL file example ::

{"question":"Are violets blue?","options":["Yes","No"],"correct_answer":"Yes"}
{"question":"How are roses?","options":["Red","Pink","Blue"],"correct_answer":"Red"}
...
"""

from quiz.core.quiz_model import QuizModel
from quiz.core.quiz_event import QuizEvent

from typing import override
import sys

import json
import pandas as pd
import os
import datetime


class Quiz(QuizModel):
    """Concrete quiz model that manages questions, players, and answers.

    Questions are read from a JSONL file and each player answers in turn.
    Results are recorded to a CSV file. Quiz events are emitted to listeners
    for integration with controllers, views or other side effects.

    Attributes:
        player_index: Index of the current player in the list of player names.
        line_index: Index of the current question line in the JSONL file.
        line: The currently loaded question dictionary.
        output_file: Path to the CSV file where results are saved.
    """

    @staticmethod
    def load_jsonl_line(path: str | None,
                        index: int) -> dict[str, list[str], str]:
        """Load a specific question line from a JSONL file.

        Args:
            path: Path to the JSONL quiz file.
            index: Zero-based index of the line (question) to load.

        Returns:
            A dictionary containing:
                - "question": The question text.
                - "options": List of answer options.
                - "correct_answer": The correct answer string.

            Returns a fallback dictionary with empty values if the index is
            invalid or the file cannot be read.
        """
        fallback = {
            "question": "",
            "options": [""],
            "correct_answer": ""
        }
        if index < 0:
            print(f"Index {index} is invalid", file=sys.stderr)
            return fallback
        if path is None:
            print(f"Path {path} is invalid", file=sys.stderr)
            return fallback
        try:
            with open(path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i == index:
                        return json.loads(line)
                return fallback
        except Exception as e:
            print(e, file=sys.stderr)
            return fallback

    def __init__(self):
        """Initialize the quiz with a list of player names.

        Args:
            player_names: List of player names participating in the quiz.
        """
        super().__init__()
        self.player_index = -1
        self.line_index = -1
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.output_file = f"{timestamp}-quiz_results.csv"

    @override
    def get_question(self) -> str:
        """Return the current question.

        Returns:
            The text of the current question.
        """
        return self.line["question"]

    @override
    def get_options(self) -> list[str]:
        """Return the options for the current question.

        Returns:
            A list of answer options.
        """
        return self.line["options"]

    @override
    def get_player_name(self) -> str:
        """Return the name of the current player.

        Returns:
            The current player's name, or an empty string if out of bounds.
        """
        self.requires_players()
        try:
            return self.players[self.player_index]
        except IndexError:
            return ""

    @override
    def record_answer(self, answer_index: int) -> None:
        """Record a player's answer for the current question in a CSV file.

        Args:
            answer_index: Index of the selected answer option.
        """
        self.requires_players()
        n_opts = len(self.line["options"])
        if 0 <= answer_index < n_opts:
            question = self.get_question()
            answer = self.get_options()[answer_index]
            correct_answer = self.line["correct_answer"]
            data = [{
                "player": self.players[self.player_index],
                "question": question,
                "answer": answer,
                "expected": correct_answer,
                "result": str(answer == correct_answer)
            }]
            df = pd.DataFrame(data)
            df.to_csv(
                self.output_file,
                mode='a',
                index=False,
                header=not os.path.exists(self.output_file)
            )

    @override
    def next_question(self) -> bool:
        """Advance to the next question in the quiz.

        Resets the current player index, loads the next question, and
        notifies listeners with a QUESTION event.

        Returns:
            True if a next question exists, False otherwise.
        """
        self.player_index = -1
        self.line_index += 1
        # Get the next question from the JSONL file.
        self.line = self.load_jsonl_line(self.quiz_file, self.line_index)
        if self.get_question() == "":
            return False
        # Send the following payload to all listeners :
        #   `["Question", "Opt1", ... ,"OptN"]`.
        self.notify_listeners(
            QuizEvent.QUESTION,
            [self.get_question()] + self.get_options()
        )
        return True

    @override
    def ask_next_player(self) -> bool:
        """Advance to the next player for the current question.

        Notifies listeners with an ASK_PLAYER event.

        Returns:
            True if a next player exists, False otherwise.
        """
        self.requires_players()
        self.player_index += 1
        if self.get_player_name() == "":
            return False
        # Send the player's name to all listeners.
        self.notify_listeners(
           QuizEvent.ASK_PLAYER,
           [self.get_player_name()]
        )
        return True

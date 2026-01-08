"""Command-line interface (CLI) quiz event listener.

This module provides a concrete implementation of a quiz event listener
that displays questions and players in the terminal. It also
generates simple textual and graphical summaries of quiz results.
"""

from quiz.core.quiz_listener import QuizListener
from quiz.core.quiz_event import QuizEvent

from typing import override

import pandas as pd
from tabulate import tabulate
import plotext as plt


class QuizListenerCLI(QuizListener):
    """CLI-based quiz listener for displaying questions and results.

    This listener reacts to quiz events by printing questions, prompting
    players and showing results using tables and terminal plots.

    Attributes:
        question_string: A formatted string representing the current question
            and its answer options for display.
        color_names: Optional list of color names used to label answer options
            (e.g. ["Green", "Red", "Yellow"]).
    """

    def __init__(self, color_names: list[str] | None = None):
        """Initialize the CLI listener.

        Args:
            color_names: Optional list of color names used to label answer options
                (e.g. ["Green", "Red", "Yellow"]).
        """
        self.question_string = ""
        self.color_names = color_names

    def build_question_string(self, args: list[str]) -> None:
        """Build a formatted string for the current question and its options.

        Args:
            args: List containing the question as the first element and
                subsequent elements as answer options.
        """
        self.question_string = f"Question: {args[0]}"
        if len(args) > 1:
            for i, option in enumerate(args[1:]):
                index = i + 1
                indication = index if self.color_names is None \
                    or len(self.color_names) < index \
                    else self.color_names[i]
                self.question_string += f"\n{indication}. {option}"

    def print_question_string(self):
        """Print the currently built question string."""
        print(self.question_string)

    def clear(self) -> None:
        """Clear the terminal screen using ANSI escape sequences."""
        print("\033[H\033[2J")

    def print_results_table(self, path: str) -> None:
        """Print a table of quiz results from a CSV file.

        Print a table of quiz results from a CSV file
        using the `tabulate` module.

        Args:
            path: Path to the CSV file containing quiz results.
        """
        print(tabulate(
            pd.read_csv(path),
            headers="keys",
            tablefmt="rounded_outline",
            showindex=False
        ))

    def print_results_plots(self, path: str) -> None:
        """Print simple terminal bar plots.

        Print simple terminal bar plots for scores, accuracy, and
        per-question results using the `plotext` module. The file
        is loaded with the `pandas` module.

        Args:
            path: Path to the CSV file containing quiz results.
        """
        df = pd.read_csv(path)
        scores = df.groupby("player")["result"].sum()
        plt.simple_bar(
            scores.index,
            scores.values,
            width=100,
            title="Scores"
        )
        print("\n")
        plt.show()
        accuracy = df.groupby("player")["result"].mean() * 100
        plt.simple_bar(
            accuracy.index,
            accuracy.values,
            width=100,
            title="Accuracy (%)"
        )
        print("\n")
        plt.show()
        question_score = df.groupby("question")["result"].sum()
        plt.simple_bar(
            question_score.index,
            question_score.values,
            width=100,
            title="Correct Answer per Question"
        )
        print("\n")
        plt.show()

    @override
    def on_event(self, e: QuizEvent, args: list[str] | None = None) -> None:
        match e:

            case QuizEvent.BEGIN:
                self.clear()
                print("Welcome to the quiz!")

            case QuizEvent.QUESTION:
                if args is not None:
                    # Process `args` as `["Question", "Opt1", ... ,"OptN"]`.
                    self.build_question_string(args)

            case QuizEvent.ASK_PLAYER:
                if args is not None:
                    self.clear()
                    self.print_question_string()

            case QuizEvent.INFO:
                if args is not None:
                    for arg in args:
                        print(arg)

            case QuizEvent.END:
                self.clear()
                print("The quiz is over. Thanks!")
                if args is not None:
                    # Only process `args[0]` as a filename.
                    self.print_results_table(args[0])
                    self.print_results_plots(args[0])

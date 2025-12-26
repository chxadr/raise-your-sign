from quiz.core.quiz_listener import QuizListener
from quiz.core.quiz_event import QuizEvent
from typing import override
import pandas as pd
from tabulate import tabulate
import plotext as plt


class QuizListenerCLI(QuizListener):

    def __init__(self):
        self.question_string = ""

    def build_question_string(self, args: list[str]) -> None:
        self.question_string = f"Question: {args[0]}"
        if len(args) > 1:
            for i, option in enumerate(args[1:]):
                self.question_string += f"\n{i+1}. {option}"

    def print_question_string(self):
        print(self.question_string)

    def clear(self) -> None:
        print("\033[H\033[2J")

    def print_results_table(self, path: str):
        print(tabulate(
            pd.read_csv(path),
            headers="keys",
            tablefmt="rounded_outline",
            showindex=False
        ))

    def print_results_plots(self, path: str):
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
        """React to quiz events."""
        match e:

            case QuizEvent.BEGIN:
                self.clear()
                print("Welcome to the quiz!")

            case QuizEvent.QUESTION:
                if args is not None:
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
                    self.print_results_table(args[0])
                    self.print_results_plots(args[0])

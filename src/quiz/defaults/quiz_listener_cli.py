from quiz.core.quiz_listener import QuizListener
from quiz.core.quiz_event import QuizEvent
from typing import override


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

    @override
    def on_event(self, e: QuizEvent, args: list[str] | None = None):
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
                    print(f"Answer for {args[0]}: ")
                pass

            case QuizEvent.INFO:
                if args is not None:
                    for arg in args:
                        print(arg)

            case QuizEvent.END:
                self.clear()
                print("The quiz is over. Thanks!")

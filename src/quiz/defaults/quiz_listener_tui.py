from quiz.core.quiz_listener import QuizListener
from quiz.core.quiz_event import QuizEvent
from typing import override


class QuizListenerCLI(QuizListener):

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
                    self.clear()
                    print(f"\nQuestion: {args[0]}")
                    if len(args) > 1:
                        for i, option in enumerate(args[1:]):
                            print(f"{i+1}. {option}")

            case QuizEvent.ASK_PLAYER:
                if args is not None:
                    print(f"\nAnswer for {args[0]}: ")
                pass

            case QuizEvent.INFO:
                if args is not None:
                    print(args[0])

            case QuizEvent.END:
                self.clear()
                print("\nThe quiz is over. Thanks!")

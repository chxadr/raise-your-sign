"""Abstractions and event definitions for building quizzes using MVC patterns.

The `quiz.core` package provides the foundational building blocks required
to implement quizzes following a Model–View–Controller (MVC) architecture.
It also defines a simple event system to enable loose coupling between
components.

These abstractions are intended to be subclassed or composed by concrete
implementations such as those provided in `quiz.defaults` or by
user-defined quiz systems.

Typical usage example::

    from quiz.core import QuizModel, QuizListener, QuizController
    from quiz.core import QuizEvent
    from typing import override


    class MyQuizModel(QuizModel):

        def __init__(self, player_names: list[str]):
            ...

        @override
        def get_question(self) -> str:
            ...

        @override
        def get_options(self) -> list[str]:
            ...

        ...


    class MyQuizListener(QuizListener):

        def __init___(self, var: str | None = None):
            self.my_var = var

        def bar(self):
            ...

        def bazz(self):
            ...

        @override
        def on_event(self, e: QuizEvent,
                     args: list[str] | None = None) -> None:
            match event:
                case QuizEvent.BEGIN:
                    foo(self.my_var)
                case QuizEvent.QUESTION:
                    self.bar()
                case QuizEvent.END:
                    self.bazz()


    class MyQuizController(QuizController):

        def get_player_input(self) -> Any:
            ...

        @override
        def run_quiz(self) -> None:
            self.quiz.begin()

            while self.quiz.next_question():
                while self.quiz.ask_next_player():
                    answer = self.get_player_input()
                    self.quiz.record_answer(answer)

            self.quiz.end()

Modules:
    quiz_model: Model abstraction for representing quiz state and logic
    quiz_controller: Controller abstraction for handling user actions
                 and flow control.
    quiz_listener: Listener abstraction for reacting to quiz events.
    quiz_event: Event definitions used for communication between components.
"""

from .quiz_controller import *
from .quiz_model import *
from .quiz_listener import *
from .quiz_event import *

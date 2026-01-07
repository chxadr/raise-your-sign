"""Default implementations for quickly building or testing quizzes.

The `quiz.defaults` package provides ready-to-use
implementations of the abstract interfaces defined in `quiz.core`.
These defaults are intended for experimentation, prototyping and
demonstration purposes. They can also serve as reference implementations
for building custom quiz systems.

Included implementations cover common interaction styles such as
command-line interfaces (CLI) and graphical user interfaces (GUI),
along with basic utilities like sound playback.

Typical usage example::

    import quiz.defaults as qd

    def main():
        quiz = qd.Quiz(["Player 1", "Player 2"])

        root = tk.Tk()
        view = qd.QuizListenerGUI(root)
        sounds = qd.SoundPlayer()
        controller = qd.QuizControllerGUI(quiz, view)

        quiz.add_listener([view, sounds])
        controller.run_quiz()


    if __name__ == "__main__":
        main()

These components can be mixed and matched with custom implementations
as long as they conform to the interfaces defined in `quiz.core`.

Modules:
    quiz_controller_cli: Command-line quiz controller implementation.
    quiz_controller_gui: Graphical quiz controller implementation.
    quiz_listener_cli: Command-line quiz event listener.
    quiz_listener_gui: Graphical quiz event listener.
    quiz_model: Default quiz model implementation.
    sound_player: Utility for playing sounds during quizzes.
"""

from .quiz_controller_cli import *
from .quiz_model import *
from .quiz_listener_cli import *
from .quiz_controller_gui import *
from .quiz_listener_gui import *
from .sound_player import *
from .quiz_controller_vision import *
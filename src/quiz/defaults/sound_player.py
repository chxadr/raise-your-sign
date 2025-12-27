from quiz.core.quiz_listener import QuizListener
from quiz.core.quiz_event import QuizEvent

from typing import override
from pathlib import Path

import nava


HERE = Path(__file__).resolve().parent
RESOURCES = str(HERE) + "/resources/"


class SoundPlayer(QuizListener):

    def play(self, path: str) -> None:
        try:
            nava.play(path, async_mode=True)
        except Exception as e:
            print(e)

    @override
    def on_event(self, e: QuizEvent, args: list[str] | None = None) -> None:
        """React to quiz events."""
        match e:

            case QuizEvent.BEGIN:
                self.play(RESOURCES + "begin.wav")

            case QuizEvent.QUESTION:
                self.play(RESOURCES + "hint.wav")

            case QuizEvent.ASK_PLAYER:
                self.play(RESOURCES + "valid.wav")

            case QuizEvent.INFO:
                pass

            case QuizEvent.END:
                self.play(RESOURCES + "won.wav")

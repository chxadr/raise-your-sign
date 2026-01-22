"""Sound-based quiz event listener.

This module provides a concrete implementation of a quiz event listener
that plays sound effects in response to quiz events. It can be used as a
lightweight feedback mechanism for both CLI and GUI-based quiz systems.
"""

from quiz.core.quiz_listener import QuizListener
from quiz.core.quiz_event import QuizEvent

from typing import override
from pathlib import Path
import sys

import nava


def resource_path(relative: str) -> Path:
    """Return absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller temp folder
        return Path(sys._MEIPASS) / relative
    return Path(__file__).resolve().parent / relative


RESOURCES = resource_path("resources")


class SoundPlayer(QuizListener):
    """Quiz event listener that plays sounds for quiz events.

    This listener reacts to quiz lifecycle and interaction events by
    playing corresponding audio cues using the `nava` library.
    """

    def play(self, path: Path) -> None:
        """Play a sound file asynchronously.

        The provided path is converted to a string before being passed
        to the audio backend. Any exceptions raised during playback are
        caught and printed to stderr so that audio errors do not
        interrupt the quiz flow.

        Args:
            path: Filesystem path to the sound file to play.
        """
        try:
            nava.play(str(path), async_mode=True)
        except Exception as e:
            print(e, file=sys.stderr)

    @override
    def on_event(self, e: QuizEvent, args: list[str] | None = None) -> None:
        match e:

            case QuizEvent.BEGIN:
                self.play(RESOURCES / "begin.wav")

            case QuizEvent.QUESTION:
                self.play(RESOURCES / "hint.wav")

            case QuizEvent.ASK_PLAYER:
                self.play(RESOURCES / "valid.wav")

            case QuizEvent.INFO:
                pass

            case QuizEvent.END:
                self.play(RESOURCES / "won.wav")

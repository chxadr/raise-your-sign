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


HERE = Path(__file__).resolve().parent
RESOURCES = f"{HERE}/resources"


class SoundPlayer(QuizListener):
    """Quiz event listener that plays sounds for quiz events.

    This listener reacts to quiz lifecycle and interaction events by
    playing corresponding audio cues using the `nava` library.
    """

    def play(self, path: str) -> None:
        """Play a sound file asynchronously.

        Errors raised during playback are caught and printed to avoid
        interrupting quiz execution.

        Args:
            path: Path to the sound file to play.
        """
        try:
            # `async_mode=True` is required for a non-blocking behaviour.
            nava.play(path, async_mode=True)
        except Exception as e:
            print(e, file=sys.stderr)

    @override
    def on_event(self, e: QuizEvent, args: list[str] | None = None) -> None:
        match e:

            case QuizEvent.BEGIN:
                self.play(f"{RESOURCES}/begin.wav")

            case QuizEvent.QUESTION:
                self.play(f"{RESOURCES}/hint.wav")

            case QuizEvent.ASK_PLAYER:
                self.play(f"{RESOURCES}/valid.wav")

            case QuizEvent.INFO:
                pass

            case QuizEvent.END:
                self.play(f"{RESOURCES}/won.wav")

"""Quiz event definitions used for communication between quiz components.

This module defines the `QuizEvent` enumeration which represents
the different events that can occur during the lifecycle of a quiz.
These events are emitted by the quiz model and consumed by listeners
to react to changes in quiz state.
"""

from enum import Enum


class QuizEvent(Enum):
    """Enumeration of quiz lifecycle and interaction events."""

    BEGIN = 0
    """Signal that the quiz has started."""

    QUESTION = 1
    """Signal that a new question is available."""

    ASK_PLAYER = 2
    """Signal that a player is being prompted to answer."""

    INFO = 3
    """Signal that informational data should be presented to players."""

    END = 4
    """Signal that the quiz has ended."""

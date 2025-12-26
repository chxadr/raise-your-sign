from enum import Enum


class QuizEvent(Enum):
    BEGIN = 0
    QUESTION = 1
    ASK_PLAYER = 2
    INFO = 3
    END = 4

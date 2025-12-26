from quiz.core.quiz_model import QuizModel
from quiz.core.quiz_event import QuizEvent
from typing import override
import json
import pandas as pd
import os
import datetime


class Quiz(QuizModel):

    @staticmethod
    def load_jsonl_line(path: str | None, index: int) -> dict[str, list[str], str]:
        fallback = {
            "question": "",
            "options": [""],
            "correct_answer": ""
        }
        if index < 0 or path is None:
            return fallback
        try:
            with open(path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i == index:
                        return json.loads(line)
                return fallback
        except Exception:
            return fallback

    def __init__(self, player_names: list[str]):
        super().__init__(player_names)
        self.player_index = -1
        self.line_index = -1
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.output_file = f"{timestamp}-quiz_results.csv"

    @override
    def get_question(self) -> str:
        return self.line["question"]

    @override
    def get_options(self) -> list[str]:
        return self.line["options"]

    @override
    def get_player_name(self) -> str:
        try:
            return self.player_names[self.player_index]
        except IndexError:
            return ""

    @override
    def record_answer(self, answer_index: int) -> None:
        n_opts = len(self.line["options"])
        if 0 <= answer_index < n_opts:
            question = self.get_question()
            answer = self.get_options()[answer_index]
            correct_answer = self.line["correct_answer"]
            data = [{
                "player": self.player_names[self.player_index],
                "question": question,
                "answer": answer,
                "result": str(answer == correct_answer)
            }]
            df = pd.DataFrame(data)
            df.to_csv(
                self.output_file,
                mode='a',
                index=False,
                header=not os.path.exists(self.output_file)
            )

    @override
    def next_question(self) -> bool:
        self.player_index = -1
        self.line_index += 1
        self.line = self.load_jsonl_line(self.quiz_file, self.line_index)
        if self.get_question() == "":
            return False
        self.notify_listeners(
            QuizEvent.QUESTION,
            [self.get_question()] + self.get_options()
        )
        return True

    @override
    def ask_next_player(self) -> bool:
        self.player_index += 1
        if self.get_player_name() == "":
            return False
        self.notify_listeners(
           QuizEvent.ASK_PLAYER,
           [self.get_player_name()]
        )
        return True

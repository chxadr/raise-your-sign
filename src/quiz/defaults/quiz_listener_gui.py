from quiz.core.quiz_listener import QuizListener
from quiz.core.quiz_event import QuizEvent
from typing import override
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class QuizListenerGUI(ttk.Frame, QuizListener):

    def __init__(self, master: ttk.Frame):
        super().__init__(master, padding=20)
        master.title("Quiz")
        master.minsize(700, 300)
        master.attributes('-type', 'dialog')
        self.pack(expand=True, fill="both")

        self.selected_index = tk.IntVar(value=-1)
        self.question_string = ""

        self.question_label = ttk.Label(self)
        self.question_label.pack(expand=True, fill="both")

        self.player_frame = ttk.Frame(self)
        self.player_label = ttk.Label(self.player_frame)
        self.player_label.pack(side="left", fill="y")

    def build_question_string(self, args: list[str]) -> None:
        self.question_string = f"Question: {args[0]}"
        if len(args) > 1:
            for i, option in enumerate(args[1:]):
                self.question_string += f"\n{i+1}. {option}"

    @override
    def on_event(self, e: QuizEvent, args: list[str] | None = None) -> None:
        """React to quiz events."""
        match e:

            case QuizEvent.BEGIN:
                self.question_label.config(text="Welcome to the quiz!")
                self.player_frame.pack(side="bottom", fill="x")

            case QuizEvent.QUESTION:
                if args is not None:
                    self.build_question_string(args)
                    self.question_label.config(text=self.question_string)

            case QuizEvent.ASK_PLAYER:
                if args is not None:
                    self.player_label.config(text=f"Answere for {args[0]}")

            case QuizEvent.INFO:
                if args is not None:
                    messagebox.showinfo(
                        message="".join([arg + "\n" for arg in args])
                    )

            case QuizEvent.END:
                self.player_frame.destroy()
                self.question_label.config(text="The quiz is over. Thanks!")

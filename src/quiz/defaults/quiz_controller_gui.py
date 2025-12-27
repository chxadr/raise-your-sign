from quiz.core.quiz_model import QuizModel
from quiz.core.quiz_controller import QuizController
from quiz.core.quiz_event import QuizEvent

from typing import override

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd


class QuizControllerGUI(QuizController):

    def __init__(self, quiz: QuizModel, view: ttk.Frame):
        super().__init__(quiz)
        self.view = view
        self.radio_btns: list[ttk.Button] = []
        self.selected_index = tk.IntVar(value=-1)
        self.current_state = QuizEvent.BEGIN

        self.interactive_frame = ttk.Frame(view)
        self.radio_frame = ttk.Frame(self.interactive_frame)
        self.next_btn = ttk.Button(
            self.interactive_frame,
            text="Next",
            command=self.on_next_btn
        )

        self.next_btn.pack(side="right", fill="y")
        self.interactive_frame.pack(side="bottom", fill="x")

    def create_radio_buttons(self) -> None:
        """Create radio buttons based on quiz options list."""
        if self.radio_btns:
            for btn in self.radio_btns:
                btn.destroy()
            self.radio_btns: list[ttk.Radiobutton] = []
        self.selected_index.set(-1)
        options = self.quiz.get_options()
        if options is not None:
            for i, name in enumerate(options):
                btn = ttk.Radiobutton(
                    self.radio_frame,
                    text=name,
                    value=i,
                    variable=self.selected_index
                )
                btn.pack(side="left", padx=6)
                self.radio_btns.append(btn)

    def select_file(self) -> str | tuple[str]:
        self.quiz.inform_player(["Select a quiz file (.jsonl)"])
        filetypes = [("JSON Line", "*.jsonl")]
        filename = fd.askopenfilename(
            title="Open a file",
            initialdir="./",
            filetypes=filetypes
        )
        return filename

    def on_next_btn(self) -> None:
        match self.current_state:

            case QuizEvent.BEGIN:

                quiz_file = self.select_file()
                if isinstance(quiz_file, str):
                    if quiz_file.endswith(".jsonl"):
                        self.quiz.set_quiz_file(quiz_file)
                    elif quiz_file == "":
                        return
                    else:
                        self.quiz.inform_player(["Invalid file type"])
                        return
                else:
                    return

                if self.quiz.next_question() and self.quiz.ask_next_player():
                    self.create_radio_buttons()
                    self.radio_frame.pack(expand=True, fill="both")
                    self.current_state = QuizEvent.ASK_PLAYER
                else:
                    self.interactive_frame.destroy()
                    self.quiz.end()

            case QuizEvent.ASK_PLAYER:

                answer_index = self.selected_index.get()
                if answer_index < 0:
                    self.quiz.inform_player([
                        "Please select an answer"
                    ])
                    return
                else:
                    self.selected_index.set(-1)
                    self.quiz.record_answer(answer_index)
                    if not self.quiz.ask_next_player():
                        if not self.quiz.next_question():
                            self.interactive_frame.destroy()
                            self.quiz.end([self.quiz.output_file])
                        else:
                            self.quiz.ask_next_player()
                            self.create_radio_buttons()

    @override
    def run_quiz(self) -> None:
        """Run the quiz."""
        self.quiz.begin()
        self.view.mainloop()

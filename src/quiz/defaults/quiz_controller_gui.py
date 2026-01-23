"""Graphical user interface (GUI) quiz controller.

This module provides a concrete implementation of the `QuizController`
abstract base class. It drives quiz flow in a `tkinter` GUI by handling
question display, player input through buttons and file selection.
"""

from quiz.core.quiz_model import QuizModel
from quiz.core.quiz_controller import QuizController
from quiz.core.quiz_event import QuizEvent
from quiz.utils.username_dialog import UsernameDialog

from typing import override

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd


class QuizControllerGUI(QuizController):
    """GUI-based quiz controller using Tkinter for player interaction.

    Attributes:
        view: The `tkinter` frame used as the main GUI container.
        radio_btns: List of Radiobutton widgets representing answer options.
        selected_index: `tkinter` variable tracking the selected answer index.
        current_state: Current quiz state, tracking the event being handled.
        interactive_frame: Frame containing radio buttons
            and the "Next" button.
        radio_frame: Frame specifically holding the radio buttons.
        next_btn: Button widget used to proceed to the next question or player.
    """

    def __init__(self, quiz: QuizModel, view: ttk.Frame):
        """Initialize the GUI controller.

        Args:
            quiz: The quiz model instance being controlled.
            view: The main `tkinter` frame for the quiz GUI.
        """
        super().__init__(quiz)
        self.view = view
        self.radio_btns: list[ttk.Button] = []
        self.selected_index = tk.IntVar(value=-1)

        # Frame containing a control pannel to place on
        # another `tkinter` frame which is either empty or already containing
        # widgets.
        self.interactive_frame = ttk.Frame(view)

        self.radio_frame = ttk.Frame(self.interactive_frame)

        # "Next" button to update the quiz control flow.
        # TODO: use distinct buttons for next question
        #    and next player to make the code clearer.
        self.next_btn = ttk.Button(
            self.interactive_frame,
            text="Next",
            command=self.on_next_btn
        )

        # Usage of `QuizEvent` states to change the "Next" button
        # behaviour depending on the expected quiz control flow.
        # TODO: use distinct buttons to make the code clearer and to remove
        #    the need of keeping track of an internal state that is completely
        #    independent from `QuizEvent` states.
        self.current_state = QuizEvent.BEGIN

        self.next_btn.pack(side="right", fill="y")
        self.interactive_frame.pack(side="bottom", fill="x")

    def create_radio_buttons(self) -> None:
        """Create radio buttons for the current quiz options.

        Removes existing radio buttons and generates new buttons based on
        the options returned by the quiz model.
        """
        if self.radio_btns:
            # Remove old radio buttons.
            for btn in self.radio_btns:
                btn.destroy()
            self.radio_btns: list[ttk.Radiobutton] = []

        # Get current answer options
        options = self.quiz.get_options()
        if options is not None:
            # Create new radio buttons labeled with the options.
            for i, name in enumerate(options):
                btn = ttk.Radiobutton(
                    self.radio_frame,
                    text=name,
                    value=i,
                    variable=self.selected_index
                )
                btn.pack(side="left", padx=6)
                self.radio_btns.append(btn)

    def select_file(self) -> str:
        """Prompt the user to select a JSONL quiz file.

        Returns:
            The selected file path as a string, or an empty string
            if canceled or invalid.
        """
        self.quiz.inform_player(["Select a quiz file (.jsonl)"])
        filetypes = [("JSON Line", "*.jsonl")]
        filename = fd.askopenfilename(
            title="Open a file",
            initialdir="./",
            filetypes=filetypes
        )
        if isinstance(filename, str):
            if filename.endswith(".jsonl") or filename == "":
                # Expected format found.
                return filename
            else:
                self.quiz.inform_player(["Invalid file type"])
                return ""
        else:
            # Multiple files have been selected. Only one file is allowed.
            return ""

    def on_next_btn(self) -> None:
        """Handle the "Next" button click event.

        Advances quiz state based on the current event:
            - BEGIN: Prompts for file selection and starts the first question.
            - ASK_PLAYER: Records the selected answer and moves
                  to the next player or next question.

        TODO: split this single bloated button into distinct ones to make the
        code clearer and to avoid weird implementations.
        """
        match self.current_state:

            case QuizEvent.BEGIN:

                # Ask for a JSONL file.
                quiz_file = self.select_file()
                if quiz_file == "":
                    return
                self.quiz.set_quiz_file(quiz_file)

                # Ask for players participating in the quiz
                dialog = UsernameDialog(self.view)
                self.quiz.set_players(dialog.usernames)

                if self.quiz.next_question() and self.quiz.ask_next_player():
                    # Show the first question
                    # and ask the first player to answer.
                    self.create_radio_buttons()
                    self.radio_frame.pack(expand=True, fill="both")
                    self.current_state = QuizEvent.ASK_PLAYER
                else:
                    # There is nothing to do. Exit.
                    self.interactive_frame.destroy()
                    self.quiz.end()

            case QuizEvent.ASK_PLAYER:

                # Get radio buttons input.
                answer_index = self.selected_index.get()
                if answer_index < 0:
                    self.quiz.inform_player([
                        "Please select an answer"
                    ])
                    return
                else:
                    # Reset radio buttons and record answer.
                    self.selected_index.set(-1)
                    self.quiz.record_answer(answer_index)
                    if not self.quiz.ask_next_player():
                        # No player to ask anymore.
                        if not self.quiz.next_question():
                            # No question anymore: end of the quiz.
                            self.interactive_frame.destroy()
                            self.quiz.end([self.quiz.output_file])
                        else:
                            # Another question is available.
                            # Ask the first player.
                            self.quiz.ask_next_player()
                            self.create_radio_buttons()

    @override
    def run_quiz(self) -> None:
        self.quiz.begin()
        self.view.mainloop()

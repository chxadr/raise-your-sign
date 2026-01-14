"""Graphical user interface (GUI) quiz event listener.

This module provides a concrete implementation of a quiz event listener
using `tkinter` for GUI display and `matplotlib` for plotting results.
It reacts to quiz events by updating labels, prompting players and
showing visual summaries of scores and accuracy.
"""

from quiz.core.quiz_listener import QuizListener
from quiz.core.quiz_event import QuizEvent

from typing import override, Any
import sys

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
import textwrap

import pandas as pd


class QuizListenerGUI(ttk.Frame, QuizListener):
    """GUI-based quiz listener for displaying questions, players and results.

    Attributes:
        master: The parent `tkinter` frame.
        selected_index: `tkinter` variable tracking selected option index.
        question_string: Formatted string of the current question and options.
        question_label: Label widget displaying the question text.
        player_frame: Frame containing player-related widgets.
        player_label: Label displaying the current player's name.
        canvas: `matplotlib` canvas used for plotting results
            (initialized during plots).
        plot_window: Toplevel window for displaying result plots.
        color_names: Optional list of color names used to label answer options
            (e.g. ["Green", "Red", "Yellow"]).
    """

    def __init__(
            self,
            master: ttk.Frame,
            min_w: int = 700,
            min_h: int = 300,
            color_names: list[str] | None = None
    ):
        """Initialize the GUI listener and configure the main window.

        Args:
            master: The parent `tkinter` frame.
            min_w: Minium width for the display window.
            min_h: Minimum height for the display window.
            color_names: Optional list of color names used to label answer
                options (e.g. ["Green", "Red", "Yellow"]).
        """
        super().__init__(master, padding=20)
        self.color_names = color_names
        self.master = master
        self.master.wm_title("Quiz")
        self.master.minsize(min_w, min_h)

        if sys.platform != "win32":
            # Allows good integration with tiled window managers on UNIX systems.
            self.master.attributes('-type', 'dialog')
        self.master.protocol("WM_DELETE_WINDOW", self.destroy_all)

        self.pack(expand=True, fill="both")

        self.selected_index = tk.IntVar(value=-1)
        self.question_string = ""

        self.question_label = ttk.Label(self)
        self.question_label.pack(expand=True, fill="both")

        self.player_frame = ttk.Frame(self)
        self.player_label = ttk.Label(self.player_frame)
        self.player_label.pack(side="left", fill="y")

    def build_question_string(self, args: list[str]) -> None:
        """Format the current question and its options for display.

        Args:
            args: List containing the question as the first element and
                subsequent elements as answer options.
        """
        self.question_string = f"Question: {args[0]}"
        if len(args) > 1:
            for i, option in enumerate(args[1:]):
                index = i + 1
                indication = index if self.color_names is None \
                    or len(self.color_names) < index \
                    else self.color_names[i]
                self.question_string += f"\n{indication}. {option}"

    def wrap_labels(self, ax: Any, width: int,
                    break_long_words: bool = False) -> None:
        """Wrap y-axis labels for `matplotlib` plots to a given width.

        Args:
            ax: The `matplotlib` axes object.
            width: Maximum character width before wrapping.
            break_long_words: Whether to break long words if needed.
        """
        labels = [label.get_text() for label in ax.get_yticklabels()]

        wrapped_labels = [
            textwrap.fill(text, width=width, break_long_words=break_long_words)
            for text in labels
        ]

        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels(wrapped_labels)

    def display_results_plots(self, path: str) -> None:
        """Display bar plots for scores, accuracy and question results.

        Display bar plots for scores, accuracy and question results using
        `matplotlib` inside a separate `tkinter`window.
        The CSV file is loaded with `pandas`.

        Args:
            path: Path to the CSV file containing quiz results.
        """
        try:
            df = pd.read_csv(path)
        except Exception as e:
            print(e, file=sys.stderr)
            return
        scores = df.groupby("player")["result"].sum()
        accuracy = df.groupby("player")["result"].mean() * 100
        question_score = df.groupby("question")["result"].sum()

        self.plot_window = tk.Toplevel(self)
        self.plot_window.title("Quiz Results")
        fig, axs = plt.subplots(3, 1, figsize=(1, 12), dpi=100)
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_window)

        axs[0].barh(scores.index, scores.values)
        axs[0].set_title("Scores")

        axs[1].barh(accuracy.index, accuracy.values)
        axs[1].set_title("Accuracy (%)")
        axs[1].set_xlim(0, 100)

        axs[2].barh(question_score.index, question_score.values)
        axs[2].set_title("Correct Answer per Question")

        for ax in axs:
            ax.invert_yaxis()
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            self.wrap_labels(ax, 20)

        self.canvas.draw()
        quit_button = ttk.Button(
            self.plot_window,
            text="Close",
            command=self.plot_window.destroy
        )
        quit_button.pack(side="bottom", pady=10)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")

    def destroy_all(self) -> None:
        """Quit and destroy the main GUI window."""
        #
        # Calling the `quit()` method on the master's `tkinter` window breaks
        # the main loop and force to garbage collect any `tkinter` resources.
        # Without it, closing the main window may leave the program running
        # in the background due to interactions with `matplotlib`.
        # This might be an issue related to the code quality.
        #
        # TODO: replace `quit()` with a production-friendly alternative.
        self.master.quit()
        self.master.destroy()

    @override
    def on_event(self, e: QuizEvent, args: list[str] | None = None) -> None:
        match e:

            case QuizEvent.BEGIN:
                self.question_label.config(text="Welcome to the quiz!")
                self.player_frame.pack(side="bottom", fill="x")

            case QuizEvent.QUESTION:
                if args is not None:
                    # Process `args` as `["Question", "Opt1", ... ,"OptN"]`.
                    self.build_question_string(args)
                    self.question_label.config(text=self.question_string)

            case QuizEvent.ASK_PLAYER:
                if args is not None:
                    # Process `args[0]` as a player's name.
                    self.player_label.config(text=f"Answer for {args[0]}")

            case QuizEvent.INFO:
                if args is not None:
                    # Process `args` as a list of strings.
                    messagebox.showinfo(
                        message="".join([arg + "\n" for arg in args])
                    )

            case QuizEvent.END:
                self.player_frame.destroy()
                self.question_label.config(text="The quiz is over. Thanks!")
                quit_button = ttk.Button(
                    self,
                    text="Close",
                    command=self.destroy_all
                )
                quit_button.pack(pady=10)
                if args is not None:
                    # Process `args[0]` as a filename.
                    self.display_results_plots(args[0])

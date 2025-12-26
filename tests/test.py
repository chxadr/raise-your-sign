import quiz.defaults as qd
import quiz.core as qc
import tkinter as tk


def main():
    quiz = qd.Quiz("quiz_data.jsonl", ["Julia", "Adrien"])
    controller: qc.QuizController | None = None
    view: qc.QuizListener | None = None
    style = int(input("(1) CLI\t(2) GUI (TKinter): "))

    if style == 1:
        view = qd.QuizListenerCLI()
        controller = qd.QuizControllerCLI(quiz)
    else:
        root = tk.Tk()
        view = qd.QuizListenerGUI(root)
        controller = qd.QuizControllerGUI(quiz, view)

    quiz.add_listener(view)
    controller.run_quiz()


if __name__ == "__main__":
    main()

import quiz.core as qc
import quiz.defaults as qd
import quiz.cv as qcv
import tkinter as tk


def main():
    n_opts = 3

    quiz = qd.Quiz(["Julia", "Adrien"])
    controller: qc.QuizController | None = None
    view: qc.QuizListener | None = None
    sounds = qd.SoundPlayer()

    controller: qc.QuizController | None = None
    view: qc.QuizListener | None = None

    print("--- RAISE YOUR SIGN ---")
    style: int | str | None = None
    while True:
        style = input("(1) CLI   (2) GUI (TKinter)   (3) CLI & CV (OpenCV): ")
        if style.isdigit() and 1 <= int(style) <= n_opts:
            style = int(style)
            break
        else:
            print(f"Input a number within the range 1-{n_opts}")

    if style == 1:
        view = qd.QuizListenerCLI()
        controller = qd.QuizControllerCLI(quiz)
    elif style == 2:
        root = tk.Tk()
        view = qd.QuizListenerGUI(root)
        controller = qd.QuizControllerGUI(quiz, view)
    elif style == 3:
        view = qd.QuizListenerCLI()
        controller = qcv.QuizControllerCVCLI(quiz)

    quiz.add_listener([view, sounds])
    controller.run_quiz()


if __name__ == "__main__":
    main()

import quiz.defaults as qd
import quiz.cv as qcv
import tkinter as tk


def main():
    quiz = qd.Quiz()
    sounds = qd.SoundPlayer()
    root = tk.Tk()

    view = qd.QuizListenerGUI(root)
    controller = qcv.QuizControllerCVGUI(quiz, view)
    quiz.add_listener([view, sounds])
    controller.run_quiz()


if __name__ == "__main__":
    main()

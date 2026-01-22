import quiz.defaults as qd
import quiz.cv as qcv
import tkinter as tk


def main():
    custom_colors = [
        "Green", "Red", "Yellow", "Blue", "Magenta"
    ]

    quiz = qd.Quiz(["Julia", "Adrien"])
    sounds = qd.SoundPlayer()
    root = tk.Tk()

    view = qd.QuizListenerGUI(root, color_names=custom_colors)
    controller = qcv.QuizControllerCVGUI(quiz, view)
    quiz.add_listener([view, sounds])
    controller.run_quiz()


if __name__ == "__main__":
    main()

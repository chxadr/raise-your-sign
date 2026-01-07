import quiz.defaults as qd
import quiz.core as qc
import tkinter as tk

def main():
    quiz = qd.Quiz(["Julia", "Adrien"])
    controller: qc.QuizController | None = None
    view: qc.QuizListener | None = None
    sounds = qd.SoundPlayer()

    controller: qc.QuizController | None = None
    view: qc.QuizListener | None = None

    # Ajout de l'option Vision dans le menu
    print("--- RAISE YOUR SIGN ---")
    style = int(input("(1) CLI\t(2) GUI (TKinter)\t(3) VISION (Caméra): "))

    if style == 1:
        view = qd.QuizListenerCLI()
        controller = qd.QuizControllerCLI(quiz)
    elif style == 2:
        root = tk.Tk()
        view = qd.QuizListenerGUI(root)
        controller = qd.QuizControllerGUI(quiz, view)
    elif style == 3:
        view = qd.QuizListenerCLI()
        controller = qd.QuizControllerVision(quiz)
    else:
        print("Choix invalide.")
        return
    
    quiz.add_listener([view, sounds])
    controller.run_quiz()


if __name__ == "__main__":
    main()

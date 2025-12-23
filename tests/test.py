from quiz.defaults import Quiz, QuizControllerTUI, QuizViewTUI


def main():
    # Initialize the model with the quiz file
    quiz = Quiz("quiz_data.json")

    # Initialize the view
    view = QuizViewTUI()

    # Initialize the controller
    controller = QuizControllerTUI(quiz, view)

    # Start the quiz
    controller.start_quiz()


if __name__ == "__main__":
    main()

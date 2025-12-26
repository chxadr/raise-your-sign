from quiz.defaults import Quiz, QuizControllerCLI, QuizListenerCLI


def main():
    quiz = Quiz("quiz_data.jsonl", ["Julia", "Adrien"])
    view = QuizListenerCLI()
    quiz.add_listener(view)
    controller = QuizControllerCLI(quiz)

    controller.run_quiz()


if __name__ == "__main__":
    main()

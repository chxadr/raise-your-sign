from quiz.core import QuizControllerInterface


class QuizControllerTUI(QuizControllerInterface):
    def __init__(self, quiz, view):
        self.quiz = quiz
        self.view = view

    def start_quiz(self):
        """Start the quiz and handle user input."""
        print("Welcome to the 2-Player Quiz!")

        # Loop through the questions
        for idx, question_data in enumerate(self.quiz.questions):
            question = question_data["question"]
            options = question_data.get("options", None)

            # Display the question to both players
            self.view.display_question(question, options)

            # Get answers from Player 1 and Player 2
            player_1_answer = self.view.get_player_answer("Player 1", question)
            player_2_answer = self.view.get_player_answer("Player 2", question)

            # Record answers
            self.quiz.record_answer("Player 1", idx, player_1_answer)
            self.quiz.record_answer("Player 2", idx, player_2_answer)

        # Save the answers to CSV after the quiz ends
        self.quiz.save_answers_to_csv("quiz_results.csv")
        print("Quiz complete! Results saved.")

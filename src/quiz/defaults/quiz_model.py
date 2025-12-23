from quiz.core import QuizModelInterface

import json
import pandas as pd


class Quiz(QuizModelInterface):
    def __init__(self, quiz_file):
        self.quiz_file = quiz_file
        self.questions = []
        self.load_quiz_data()
        self.answers = {"Player 1": [], "Player 2": []}

    def load_quiz_data(self):
        """Load quiz data from a JSON file."""
        try:
            with open(self.quiz_file, 'r') as file:
                self.questions = json.load(file)
        except FileNotFoundError:
            print(f"Error: The file {self.quiz_file} does not exist.")

    def get_question(self, index):
        """Return the question at a specific index."""
        return self.questions[index]

    def record_answer(self, player, question_index, answer):
        """Record the answer for a specific player and question."""
        if player in self.answers:
            self.answers[player].append({
                "Question": self.questions[question_index]["question"],
                "Answer": answer
            })

    def save_answers_to_csv(self, output_file):
        """Save the answers to a CSV file using pandas."""
        # Flatten the answers into a format suitable for a dataframe
        data = []
        for player, answers in self.answers.items():
            for answer in answers:
                data.append({
                    "Player": player,
                    "Question": answer["Question"],
                    "Answer": answer["Answer"]
                })

        # Create a DataFrame
        df = pd.DataFrame(data)

        # Save the DataFrame to a CSV file
        df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")

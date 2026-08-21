from clarification.engine import generate_clarification
from query_analyzer import analyze_query
from validation.schema_validator import validate_query_analysis


class ClarificationSession:

    def __init__(self, original_question):

        self.original_question = original_question

        self.current_analysis = analyze_query(
            original_question
        )

        self.validation_result = validate_query_analysis(
            self.current_analysis
        )

        self.clarification_history = []

    def needs_clarification(self):

        return (
            self.current_analysis.is_ambiguous
            or not self.validation_result["valid"]
        )

    def get_clarification_question(self):

        print("\n--- DEBUG ---")
        print("Analysis ambiguous:", self.current_analysis.is_ambiguous)
        print("Validation result:", self.validation_result)
        print("--- END DEBUG ---\n")

        # Schema validation errors have highest priority
        if not self.validation_result["valid"]:

            questions = []

            for error in self.validation_result["errors"]:

                if error["type"] == "missing_column":

                    questions.append(
                        f"The column '{error['column']}' "
                        "does not exist in the database schema. "
                        "Which valid column should be used instead?"
                    )

                elif error["type"] == "missing_table":

                    questions.append(
                        f"The table '{error['table']}' "
                        "does not exist in the database schema. "
                        "Which valid table should be used instead?"
                    )

                else:

                    questions.append(error["message"])

            return " ".join(questions)

        if self.current_analysis.is_ambiguous:

            result = generate_clarification(
                self.current_analysis
            )

            return result["question"]

        return None

    def process_answer(self, user_answer):

        question = self.get_clarification_question()

        self.clarification_history.append({
            "question": question,
            "answer": user_answer
        })

        updated_question = (
            self.original_question
            + " "
            + user_answer
        )

        self.current_analysis = analyze_query(
            updated_question
        )

        self.validation_result = validate_query_analysis(
            self.current_analysis
        )

        return self.current_analysis

if __name__ == "__main__":

    session = ClarificationSession(
        "Show me students with GPA above 8."
    )

    print("Needs clarification:")
    print(session.needs_clarification())

    if session.needs_clarification():

        question = session.get_clarification_question()

        print("\nClarification:")
        print(question)

        answer = input("\nYour answer: ")

        analysis = session.process_answer(answer)

        print("\nUpdated analysis:")
        print(
            analysis.model_dump_json(
                indent=2
            )
        )
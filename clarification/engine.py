from clarification.question_templates import QUESTION_TEMPLATES


def generate_clarification(query_analysis):

    if not query_analysis.is_ambiguous:
        return {
            "needs_clarification": False,
            "question": None,
            "missing_information": []
        }

    missing_information = query_analysis.missing_information

    questions = []

    for missing in missing_information:

        missing_lower = missing.lower()

        if "department" in missing_lower:
            questions.append(
                QUESTION_TEMPLATES["department"]
            )

        elif (
            "rank" in missing_lower
            or "criterion" in missing_lower
        ):
            questions.append(
                QUESTION_TEMPLATES["ranking_criterion"]
            )

        elif (
            "aggregation" in missing_lower
            or "calculation" in missing_lower
        ):
            questions.append(
                QUESTION_TEMPLATES["aggregation_column"]
            )

        elif "date" in missing_lower:
            questions.append(
                QUESTION_TEMPLATES["date_range"]
            )

        elif "group" in missing_lower:
            questions.append(
                QUESTION_TEMPLATES["grouping_column"]
            )

        elif "order" in missing_lower:
            questions.append(
                QUESTION_TEMPLATES["ordering_column"]
            )

        else:
            questions.append(
                f"Could you provide more information about: {missing}?"
            )

    return {
        "needs_clarification": True,
        "question": " ".join(questions),
        "missing_information": missing_information
    }

if __name__ == "__main__":

    class MockAnalysis:

        is_ambiguous = False

        missing_information = []


    result = generate_clarification(MockAnalysis())

    print(result)
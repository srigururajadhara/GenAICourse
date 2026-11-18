def validate_question(question: str):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Please enter a question.")
    if len(question) > 3000:
        raise ValueError("Question is too long. Please keep it under 3,000 characters.")


def validate_answer(answer: str):
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("The answer model returned an empty response.")

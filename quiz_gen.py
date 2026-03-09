import json
import os
from anthropic import Anthropic


class QuizGenerationError(Exception):
    pass


def generate_quiz(bucket_name: str, documents_text: list[str], num_questions: int = 10) -> list[dict]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or api_key == "sk-ant-REPLACE_ME":
        raise QuizGenerationError("ANTHROPIC_API_KEY is not configured. Set it in your .env file.")

    combined = "\n\n---\n\n".join(documents_text)
    max_chars = 80000
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n\n[Content truncated for length]"

    num_mc = max(num_questions - 2, 1)
    num_tf = num_questions - num_mc

    prompt = f"""You are a quiz generator. Generate a quiz based ONLY on the following source material for the topic: "{bucket_name}".

SOURCE MATERIAL:
{combined}

Generate exactly {num_questions} quiz questions: {num_mc} multiple choice and {num_tf} true/false.

Respond with ONLY valid JSON (no markdown fences, no extra text) in this exact format:
{{
  "questions": [
    {{
      "question_text": "Your question here?",
      "question_type": "multiple_choice",
      "options": {{"A": "First option", "B": "Second option", "C": "Third option", "D": "Fourth option"}},
      "answer_key": "B",
      "explanation": "Brief explanation of why this is correct based on the source material."
    }},
    {{
      "question_text": "Your true/false question here?",
      "question_type": "true_false",
      "options": {{}},
      "answer_key": "True",
      "explanation": "Brief explanation based on the source material."
    }}
  ]
}}

Rules:
- Every question MUST be answerable from the source material ONLY. Do not use general knowledge.
- For multiple_choice: answer_key must be exactly one of: A, B, C, D
- For true_false: answer_key must be exactly "True" or "False"
- Each explanation should reference the source material
- Return ONLY the JSON object, nothing else"""

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()

    # Strip markdown code fences if Claude included them
    if text.startswith("```"):
        lines = text.split("\n")
        end = next((i for i in range(len(lines) - 1, 0, -1) if lines[i].strip() == "```"), len(lines))
        text = "\n".join(lines[1:end])

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise QuizGenerationError(f"Claude returned invalid JSON: {e}")

    questions = data.get("questions", [])
    if not questions:
        raise QuizGenerationError("Claude returned no questions.")

    for i, q in enumerate(questions):
        for field in ("question_text", "question_type", "options", "answer_key"):
            if field not in q:
                raise QuizGenerationError(f"Question {i + 1} is missing field: {field}")
        if q["question_type"] not in ("multiple_choice", "true_false"):
            raise QuizGenerationError(f"Question {i + 1} has invalid type: {q['question_type']}")

    return questions

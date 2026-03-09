import json
import os
from anthropic import Anthropic


class QuizGenerationError(Exception):
    pass


DIFFICULTY_LABELS = {
    "easy": "Easy",
    "medium": "Medium",
    "hard": "Hard",
}

_DIFFICULTY_INSTRUCTIONS = {
    "easy": """\
Difficulty: EASY
- Test broad recall of definitions, facts, and core concepts stated directly in the material.
- Questions should be answerable by someone who read the material once and paid attention.
- Prefer "what is", "which of the following defines", and "which statement is true" style questions.
- Avoid ambiguity — each question should have one clearly correct answer with no close calls.
- True/false questions should test clear, explicit factual claims.""",

    "medium": """\
Difficulty: MEDIUM
- Test applied understanding, not just recall.
- Questions should require connecting ideas across the material, understanding context and relationships, and reasoning about how concepts work together.
- Include scenario-based questions: "given this situation, what would be true?" or "which approach best fits this requirement?"
- Surface-level reading is not enough — the reader must understand the material, not just recognize keywords.
- True/false questions should test claims that require understanding, not just memorization.""",

    "hard": """\
Difficulty: HARD
- Test deep mastery: nuanced distinctions, edge cases, exceptions, and situations where multiple concepts interact.
- Questions should probe the "why" and "under what conditions", not just the "what".
- Include questions where multiple answers seem plausible but only one is correct given careful reading.
- A reader who only skimmed the material should struggle. Only someone who studied it carefully should succeed.
- True/false questions should test subtle or easily misunderstood claims.
- Explanations should clearly justify why the correct answer is right and why plausible alternatives are wrong.""",
}


def generate_quiz(bucket_name: str, documents_text: list[str], difficulty: str = "medium", num_questions: int = 10) -> list[dict]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or api_key == "sk-ant-REPLACE_ME":
        raise QuizGenerationError("ANTHROPIC_API_KEY is not configured. Set it in your .env file.")

    combined = "\n\n---\n\n".join(documents_text)
    max_chars = 80000
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n\n[Content truncated for length]"

    num_mc = max(num_questions - 2, 1)
    num_tf = num_questions - num_mc

    difficulty_instructions = _DIFFICULTY_INSTRUCTIONS.get(difficulty, _DIFFICULTY_INSTRUCTIONS["medium"])

    prompt = f"""You are a quiz generator. Generate a quiz based ONLY on the following source material for the topic: "{bucket_name}".

SOURCE MATERIAL:
{combined}

Generate exactly {num_questions} quiz questions: {num_mc} multiple choice and {num_tf} true/false.

{difficulty_instructions}

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

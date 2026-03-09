import json
from datetime import datetime
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Quiz, QuizAttempt, QuizAttemptAnswer, User
from app_templates import render

router = APIRouter()


@router.get("/{quiz_id}/take")
async def take_quiz_get(
    quiz_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        return RedirectResponse("/?msg=not_found", status_code=302)

    questions = quiz.questions
    # Deserialize options for template rendering
    questions_with_options = []
    for q in questions:
        questions_with_options.append({
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": json.loads(q.options_json),
            "answer_key": q.answer_key,
            "position": q.position,
        })

    attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=user.id,
        total_questions=len(questions),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return render(request, "quiz_take.html", {
        "quiz": quiz,
        "questions": questions_with_options,
        "attempt_id": attempt.id,
    }, current_user=user)


@router.post("/{quiz_id}/submit/{attempt_id}")
async def submit_quiz(
    quiz_id: int,
    attempt_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.user_id == user.id,
    ).first()

    if not quiz or not attempt:
        return RedirectResponse("/?msg=not_found", status_code=302)
    if attempt.submitted_at:
        return RedirectResponse(f"/quizzes/{quiz_id}/results/{attempt_id}", status_code=302)

    form_data = await request.form()
    questions = quiz.questions
    correct = 0

    for q in questions:
        user_answer = form_data.get(f"q_{q.id}", "").strip()
        is_correct = user_answer.upper() == q.answer_key.upper()
        if is_correct:
            correct += 1
        answer = QuizAttemptAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            user_answer=user_answer,
            is_correct=is_correct,
        )
        db.add(answer)

    attempt.score = (correct / len(questions) * 100) if questions else 0.0
    attempt.submitted_at = datetime.utcnow()
    db.commit()
    return RedirectResponse(f"/quizzes/{quiz_id}/results/{attempt_id}", status_code=302)


@router.get("/{quiz_id}/results/{attempt_id}")
async def quiz_results(
    quiz_id: int,
    attempt_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.user_id == user.id,
    ).first()

    if not quiz or not attempt or not attempt.submitted_at:
        return RedirectResponse("/?msg=not_found", status_code=302)

    answer_map = {a.question_id: a for a in attempt.answers}
    questions_data = []
    for q in quiz.questions:
        options = json.loads(q.options_json)
        answer = answer_map.get(q.id)
        questions_data.append({
            "question": q,
            "options": options,
            "user_answer": answer.user_answer if answer else "",
            "is_correct": answer.is_correct if answer else False,
        })

    correct_count = sum(1 for qd in questions_data if qd["is_correct"])

    return render(request, "quiz_results.html", {
        "quiz": quiz,
        "attempt": attempt,
        "questions_data": questions_data,
        "correct_count": correct_count,
        "total": len(questions_data),
        "score_pct": round(attempt.score or 0),
    }, current_user=user)

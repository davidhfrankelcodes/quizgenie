import json
import os
import re
import uuid
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Bucket, Document, Quiz, QuizQuestion, User
from text_extract import extract_text
from quiz_gen import generate_quiz, QuizGenerationError, DIFFICULTY_LABELS
from app_templates import render

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf": "pdf", ".docx": "docx", ".txt": "txt"}
UPLOAD_DIR = "uploads"


def safe_filename(name: str) -> str:
    name = os.path.basename(name)
    name = re.sub(r"[^\w.\-]", "_", name)
    return name or "file"


@router.get("/new")
async def new_bucket_get(request: Request, user: User = Depends(get_current_user)):
    return render(request, "new_bucket.html", {}, current_user=user)


@router.post("/new")
async def new_bucket_post(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    name = name.strip()
    if not name:
        return render(request, "new_bucket.html", {"error": "Bucket name is required."}, current_user=user)
    bucket = Bucket(name=name, description=description.strip() or None, created_by=user.id)
    db.add(bucket)
    db.commit()
    db.refresh(bucket)
    return RedirectResponse(f"/buckets/{bucket.id}", status_code=302)


@router.get("/{bucket_id}")
async def bucket_detail(
    bucket_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bucket = db.query(Bucket).filter(Bucket.id == bucket_id).first()
    if not bucket:
        return RedirectResponse("/?msg=not_found", status_code=302)
    return render(request, "bucket_detail.html", {
        "bucket": bucket,
        "documents": bucket.documents,
        "quizzes": bucket.quizzes,
    }, current_user=user)


@router.post("/{bucket_id}/upload")
async def upload_document(
    bucket_id: int,
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bucket = db.query(Bucket).filter(Bucket.id == bucket_id).first()
    if not bucket:
        return RedirectResponse("/?msg=not_found", status_code=302)

    original_name = file.filename or "upload"
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return RedirectResponse(f"/buckets/{bucket_id}?msg=bad_file_type", status_code=302)

    content_type = ALLOWED_EXTENSIONS[ext]
    safe_name = safe_filename(original_name)
    bucket_dir = os.path.join(UPLOAD_DIR, str(bucket_id))
    os.makedirs(bucket_dir, exist_ok=True)
    stored_filename = f"{uuid.uuid4().hex}_{safe_name}"
    stored_path = os.path.join(bucket_dir, stored_filename)

    contents = await file.read()
    with open(stored_path, "wb") as f:
        f.write(contents)

    doc = Document(
        bucket_id=bucket_id,
        filename=safe_name,
        stored_path=stored_path,
        content_type=content_type,
        processing_status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        text = extract_text(stored_path, content_type)
        doc.extracted_text = text
        doc.processing_status = "done"
    except Exception:
        doc.processing_status = "error"
    db.commit()

    return RedirectResponse(f"/buckets/{bucket_id}?msg=uploaded", status_code=302)


@router.post("/{bucket_id}/generate")
async def generate_quiz_route(
    bucket_id: int,
    request: Request,
    difficulty: str = Form("medium"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if difficulty not in DIFFICULTY_LABELS:
        difficulty = "medium"

    bucket = db.query(Bucket).filter(Bucket.id == bucket_id).first()
    if not bucket:
        return RedirectResponse("/?msg=not_found", status_code=302)

    docs = [d for d in bucket.documents if d.processing_status == "done" and d.extracted_text]
    if not docs:
        return RedirectResponse(f"/buckets/{bucket_id}?msg=no_docs", status_code=302)

    texts = [d.extracted_text for d in docs]
    try:
        questions = generate_quiz(bucket.name, texts, difficulty=difficulty)
    except QuizGenerationError:
        return RedirectResponse(f"/buckets/{bucket_id}?msg=quiz_failed", status_code=302)

    label = DIFFICULTY_LABELS[difficulty]
    quiz = Quiz(
        bucket_id=bucket_id,
        created_by=user.id,
        title=f"Quiz: {bucket.name} — {label}",
        difficulty=difficulty,
    )
    db.add(quiz)
    db.flush()

    for i, q in enumerate(questions):
        question = QuizQuestion(
            quiz_id=quiz.id,
            question_text=q["question_text"],
            question_type=q["question_type"],
            options_json=json.dumps(q.get("options", {})),
            answer_key=q["answer_key"],
            explanation=q.get("explanation", ""),
            position=i,
        )
        db.add(question)

    db.commit()
    db.refresh(quiz)
    return RedirectResponse(f"/quizzes/{quiz.id}/take", status_code=302)

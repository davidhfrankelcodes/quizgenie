# QuizGenie

A document-to-quiz platform. Upload your documents into a **bucket**, generate a quiz from the content using Claude AI, take the quiz, and see how well you know the material.

## How it works

1. Create a **bucket** — a named collection of related documents (e.g. "Biology Unit 3", "Q2 Compliance Training")
2. Upload documents into the bucket (PDF, DOCX, or TXT)
3. Click **Generate Quiz with AI** — Claude reads your documents and writes questions grounded in that content
4. Take the quiz and review your results with explanations

Quizzes are always based on *your* documents, not general model knowledge.

---

## Running with Docker (recommended)

### Prerequisites

- Docker and Docker Compose
- An [Anthropic API key](https://console.anthropic.com/)

### Setup

```bash
cp .env.template .env
# Edit .env and set your ANTHROPIC_API_KEY and a strong SECRET_KEY
```

```bash
docker compose up
```

The app will be available at **http://localhost:8000**.

Data and uploads are persisted to `./data/` and `./uploads/` on your host machine, so they survive container rebuilds.

---

## Running locally

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (or pip)

### Setup

```bash
cp .env.template .env
# Edit .env — set ANTHROPIC_API_KEY and SECRET_KEY

uv venv .venv
uv pip install -r requirements.txt

source .venv/bin/activate
uvicorn main:app --reload
```

The app will be available at **http://localhost:8000**.

---

## Configuration

All configuration is via environment variables (or the `.env` file):

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `SECRET_KEY` | Yes | Secret used to sign session cookies — use a long random string in production |

---

## Default credentials

On first run, an admin account is bootstrapped automatically:

| Username | Password |
|----------|----------|
| `admin` | `changeme` |

**Change this password immediately.** The app will show a warning in the admin panel until you do.

---

## Project structure

```
quizgenie-claude/
├── main.py               # App entry point, routes, startup bootstrap
├── database.py           # SQLAlchemy engine (SQLite at data/quizgenie.db)
├── models.py             # ORM models
├── auth.py               # Password hashing, session cookies, auth dependencies
├── quiz_gen.py           # Claude API quiz generation
├── text_extract.py       # Text extraction for PDF, DOCX, TXT
├── app_templates.py      # Shared Jinja2 templates instance
├── routes/               # Route handlers (auth, buckets, quizzes, admin)
├── templates/            # Jinja2 HTML templates
├── static/               # CSS and favicon
├── requirements.txt      # Python dependencies
├── .env.template         # Environment variable template — copy to .env
├── data/                 # SQLite database (created at runtime, mount as volume)
├── uploads/              # Uploaded files (created at runtime, mount as volume)
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

---

## Admin features

Admin users can create additional users (admin or non-admin) at `/admin/users`. All authenticated users can create buckets, upload documents, generate quizzes, and take quizzes.

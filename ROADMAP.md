# QuizGenie Roadmap

## What's been built

The initial working application, end-to-end.

### Authentication & User Management
- Login / logout with signed session cookies
- Default `admin/changeme` account bootstrapped on first run
- Admin warning banner until default password is changed
- Admin user management: create admin or non-admin accounts
- Any authenticated user can change their own password

### Buckets & Documents
- Create buckets with name and optional description
- Upload documents (PDF, DOCX, TXT) — text extracted immediately on upload
- Per-document processing status (pending / done / error)
- All buckets visible to all authenticated users (shared workspace)

### Quiz Generation & Taking
- Generate 10-question multiple choice (A/B/C/D) quizzes from bucket content via Claude
- Three difficulty levels — Easy, Medium, Hard — each with distinct prompt instructions
- Difficulty label baked into quiz title for easy identification
- Quizzes persist and can be retaken any number of times
- Loading overlays during upload, generation, and submission
- Deterministic server-side scoring (answer comparison)
- Results page: score, progress bar, per-question correct/incorrect with explanations

### Infrastructure
- SQLite database in `./data/` for easy volume mounting
- Uploaded files stored in `./uploads/`
- Docker + Docker Compose setup with persistent volume mounts
- SVG favicon matching the app logo

---

## Up next

Gaps that affect basic day-to-day usability.

### Content management
- **Delete documents** — remove a document from a bucket; re-extract if needed
- **Delete buckets** — with confirmation; cascades to documents and quizzes
- **Document re-extraction** — retry text extraction for documents that errored

### Quiz improvements
- **Configurable question count** — let users choose 5, 10, 15, or 20 questions at generation time
- **Quiz deletion** — remove a quiz and its attempt history from a bucket
- **Attempt history per quiz** — view all past attempts with scores and timestamps, not just the most recent

### Navigation
- **Global quizzes view** — a "My Quizzes" or "All Quizzes" page, not just per-bucket
- **Recent activity on dashboard** — surface recently taken quizzes and recently uploaded documents

---

## Planned

Features with clear value once the basics are solid.

### User experience
- **Score improvement tracking** — graph or table showing score progression across retakes of the same quiz
- **Bucket search / filter** — as the bucket list grows, a search bar or tag filter on the dashboard
- **Document preview** — show a truncated excerpt of the extracted text so users can confirm extraction worked

### Quiz quality
- **Regenerate individual questions** — flag a question as bad and swap it out without regenerating the whole quiz
- **Question count per difficulty context** — tune how many questions to show based on difficulty (e.g. Hard quizzes default to fewer, more focused questions)

### Admin
- **Admin dashboard** — usage summary: total users, buckets, documents, quizzes, and attempts
- **Disable/enable users** — deactivate a user account without deleting it

---

## Future

Bigger bets that depend on the core being stable.

### Richer content
- **Additional file types** — PowerPoint (`.pptx`), plain Markdown, HTML pages
- **URL ingestion** — paste a URL and extract text from a web page into a bucket
- **Chunking and embeddings** — move from full-text to vector-based retrieval for more precise quiz grounding on large document sets

### Richer assessment
- **Short answer / free response questions** — submitted answers evaluated by Claude against the source material
- **Partial credit** — rubric-based scoring for nuanced answers
- **Study mode** — flashcard-style review of key facts extracted from a bucket before taking a quiz
- **Spaced repetition reminders** — prompt users to retake quizzes at intervals based on past performance

### Collaboration & sharing
- **Per-bucket access control** — make a bucket private, shared with specific users, or public
- **Shareable quiz links** — allow a quiz to be taken without an account (read-only link)
- **Cohort results** — admin view of how a group of users performed on the same quiz

### Platform
- **REST API** — programmatic access to bucket and quiz management for integrations
- **Webhook on quiz completion** — notify an external system when a user submits a quiz
- **SSO / OIDC** — integrate with an external identity provider instead of local accounts

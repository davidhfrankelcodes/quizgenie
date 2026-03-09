# CLAUDE.md

## Project Overview

This application is a document-to-quiz platform.

Users organize related documents into **buckets**. A bucket represents a collection of materials within the same domain, topic, subject area, or body of knowledge. After documents are uploaded into a bucket, the application processes that content and uses it to generate quizzes. The system then evaluates quiz performance based on the source material contained in the bucket.

The overall goal is to help users measure understanding of a defined set of documents rather than quiz against generic knowledge.

Examples of a bucket:
- A biology unit with lecture notes, readings, and study guides
- A compliance training packet
- Internal documentation for a software system
- A collection of historical source documents on the same topic

---

## Core Product Requirements

### 1. Authentication and User Management

The application must support user accounts and permissions.

#### Default admin bootstrap behavior
- On first application launch, if no users exist, create a default admin user:
  - username: `admin`
  - password: `changeme`
- The application should strongly encourage or require changing this password after first login.
- The default admin bootstrap should not create duplicate admin users if users already exist.

#### Admin capabilities
Admin users can:
- log in to the application
- change their own password
- create additional users
- create both:
  - admin users
  - non-admin users
- manage other users as appropriate for the app

#### Non-admin capabilities
Non-admin users can:
- log in
- change their own password
- interact with buckets and quizzes according to authorization rules defined by the app

---

### 2. Buckets and Documents

The core data model includes **buckets** and **documents**.

#### Bucket concept
A bucket is a logical grouping of uploaded documents that belong together in the same domain.

A bucket should:
- have a name
- optionally have a description
- contain one or more uploaded documents
- act as the content boundary for quiz generation and evaluation

#### Why buckets exist
Buckets exist so quiz generation is grounded in a coherent body of source material. The app should treat a bucket as the authoritative knowledge domain for quiz creation. Quiz questions and evaluations should be based on the contents of the selected bucket rather than on general model knowledge alone.

#### Document handling
The application should support uploading documents into buckets.

At a minimum, the system should:
- associate each uploaded document with exactly one bucket
- extract usable text from uploaded documents
- store enough metadata to track the document and its relationship to the bucket
- make the extracted content available for downstream quiz generation and evaluation

Possible future enhancements:
- chunking and embeddings
- duplicate detection
- document reprocessing
- per-document error details

---

### 3. Quiz Generation and Evaluation

The main workflow after bucket creation is quiz generation and performance evaluation.

#### Quiz generation
The application should be able to:
- generate quizzes from the content of a selected bucket
- create questions based on the uploaded source material
- avoid generating questions that are not supported by the bucket content
- support iterative improvement of quiz quality over time

Question format: multiple choice (A/B/C/D), 10 questions per quiz.

#### Evaluation
The application should:
- accept user quiz submissions
- score quiz responses
- evaluate answers against the bucket’s source material
- provide useful feedback where appropriate

The system should aim to distinguish between:
- correct answers supported by the source material
- incorrect answers
- partially correct answers, if the app eventually supports that concept

#### Design principle
The bucket content is the source of truth. Generated quizzes and answer evaluation should remain anchored to the documents in the bucket.

---

## Product Intent

This app is not just a generic quiz generator. It is a **domain-grounded assessment tool**.

The intended user flow is:

1. User creates a bucket
2. User uploads related documents into that bucket
3. The app processes those documents into usable text/content units
4. The app generates quizzes based on that bucket
5. The user takes a quiz
6. The app evaluates the outcome based on the content in the bucket

---

## Suggested MVP Scope

The initial version should prioritize working end-to-end over broad feature depth.

### MVP goals
- login system
- default bootstrap admin user
- ability for admin to create users
- ability for users to change passwords
- ability to create buckets
- ability to upload documents into buckets
- text extraction from uploaded documents
- quiz generation from bucket content
- quiz submission and scoring
- basic results display

### MVP non-goals
Unless explicitly needed, avoid over-engineering the first version with:
- advanced role hierarchies
- collaborative editing
- full audit logging
- elaborate workflow engines
- multi-tenant enterprise features
- overly complex permissions
- premature microservices architecture

---

## Data Model

### User
- id
- username (unique)
- password_hash
- is_admin
- created_at
- updated_at

### Bucket
- id
- name
- description (nullable)
- created_by → User
- created_at
- updated_at

### Document
- id
- bucket_id → Bucket
- filename (sanitized)
- stored_path (on-disk path: `uploads/{bucket_id}/{uuid}_{filename}`)
- content_type (`pdf`, `docx`, or `txt`)
- extracted_text
- processing_status (`pending`, `done`, `error`)
- created_at

### Quiz
- id
- bucket_id → Bucket
- created_by → User
- title (includes difficulty label, e.g. "Quiz: Biology Unit 3 — Hard")
- difficulty (`easy`, `medium`, or `hard`)
- created_at

### QuizQuestion
- id
- quiz_id → Quiz
- question_text
- question_type (`multiple_choice`)
- options_json (JSON string: `{"A": "...", "B": "...", "C": "...", "D": "..."}`)
- answer_key (`"A"`, `"B"`, `"C"`, or `"D"`)
- explanation
- position (ordering index within the quiz)

### QuizAttempt
- id
- quiz_id → Quiz
- user_id → User
- score (float, 0–100)
- total_questions
- submitted_at (null until submitted)
- created_at

### QuizAttemptAnswer
- id
- attempt_id → QuizAttempt
- question_id → QuizQuestion
- user_answer
- is_correct

---

## Security Requirements

- Never store plaintext passwords
- Use secure password hashing
- Require authentication for app access unless explicitly building a public mode
- Restrict user-management functions to admin users
- Restrict privileged operations appropriately
- Validate uploaded files
- Sanitize filenames and user inputs
- Treat generated quiz output as untrusted until validated by application logic
- Avoid exposing sensitive internal prompts or raw implementation details in the UI

---

## UX Expectations

- First-run experience should be simple and obvious
- The existence of the default admin account should be clearly documented
- The app should make it easy to:
  - create a bucket
  - upload documents
  - generate a quiz
  - take a quiz
  - review results
- Admin functionality should be present but not clutter the core flow

---

## AI / LLM Guidance

If this app uses an LLM for quiz generation or answer evaluation:

- The LLM should be grounded in bucket content
- Prompts should emphasize that answers must come from the bucket documents
- The application should prefer reproducible, inspectable workflows over opaque magic
- Where possible, store enough metadata to explain why a question or evaluation was produced
- Avoid relying on model world knowledge when the bucket content is incomplete or silent

---

## Implementation Guidance

When building features for this project:

1. Preserve the core mental model:
   - buckets contain related documents
   - quizzes are generated from buckets
   - evaluations are based on bucket content

2. Favor simple, maintainable architecture for the first version.

3. Build the happy path first:
   - bootstrap admin
   - login
   - create bucket
   - upload document
   - extract text
   - generate quiz
   - submit answers
   - score results

4. Keep code organized around clear responsibilities:
   - auth/user management
   - bucket/document management
   - quiz generation
   - quiz evaluation

5. Avoid speculative complexity unless a real need appears.

---

## Decisions Made

These were open questions that have been resolved in the current implementation:

- **Supported file types:** PDF, DOCX, TXT
- **Non-admin bucket creation:** Yes — all authenticated users can create buckets
- **Bucket visibility:** Shared — all authenticated users see all buckets
- **Quiz persistence:** Quizzes are generated and saved; they persist and can be retaken
- **Question types:** Multiple choice only (A/B/C/D), 10 questions per quiz
- **Quiz difficulty:** Three levels — Easy, Medium, Hard — selectable per quiz generation. Difficulty is baked into the Claude prompt and reflected in the quiz title and UI. Easy = broad recall; Medium = applied understanding and scenario reasoning; Hard = nuanced distinctions, edge cases, synthesis across the material.
- **Answer explanations:** Shown per-question on the results page after submission
- **Document storage:** Full extracted text stored in the database; no chunks or embeddings
- **Document reprocessing:** Not supported in the current version
- **Evaluation method:** Deterministic server-side comparison (user answer vs. `answer_key`)

## Open Questions / Future Decisions

- Should buckets have per-user access controls, or remain globally shared?
- Should the number of quiz questions be configurable per generation?
- Should the app support deleting buckets or documents?
- Should quiz attempts be visible to other users (leaderboard, shared results)?
- Should the app support reprocessing documents when extraction fails?

---

## Summary

This app is a bucket-based, document-grounded quiz platform with admin-managed users.

At startup, it should bootstrap a default `admin/changeme` account if no users exist. Users upload related documents into buckets. Buckets define the knowledge domain. The app generates quizzes from bucket content and evaluates quiz performance based on the same source material.

When making design decisions, optimize for:
- clarity
- groundedness in source material
- secure user management
- simple end-to-end usability
- maintainable implementation
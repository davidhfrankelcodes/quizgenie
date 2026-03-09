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
- document type tracking
- chunking and embeddings
- duplicate detection
- document reprocessing
- per-document status and error reporting

---

### 3. Quiz Generation and Evaluation

The main workflow after bucket creation is quiz generation and performance evaluation.

#### Quiz generation
The application should be able to:
- generate quizzes from the content of a selected bucket
- create questions based on the uploaded source material
- avoid generating questions that are not supported by the bucket content
- support iterative improvement of quiz quality over time

Possible question formats:
- multiple choice
- true/false
- short answer
- explanation-based questions

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

## Recommended Data Model

This is a suggested conceptual model and can be adapted to the framework used.

### User
Fields may include:
- id
- username
- password hash
- is_admin
- created_at
- updated_at

### Bucket
Fields may include:
- id
- name
- description
- created_by
- created_at
- updated_at

### Document
Fields may include:
- id
- bucket_id
- filename
- content_type
- extracted_text
- processing_status
- created_at
- updated_at

### Quiz
Fields may include:
- id
- bucket_id
- created_by
- title
- created_at
- updated_at

### QuizQuestion
Fields may include:
- id
- quiz_id
- question_text
- question_type
- answer_key
- explanation
- source_reference

### QuizAttempt
Fields may include:
- id
- quiz_id
- user_id
- score
- submitted_at

### QuizAttemptAnswer
Fields may include:
- id
- quiz_attempt_id
- quiz_question_id
- user_answer
- is_correct
- evaluation_notes

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

## Open Questions / Future Decisions

These items may need refinement later:

- Which file types are supported for upload?
- Should non-admin users be able to create buckets?
- Are buckets private to a user, shared, or global?
- Should quizzes be regenerated each time or saved persistently?
- What question types should be supported in MVP?
- How should answer explanations be shown?
- Should the app store document chunks or embeddings?
- Should the app support reprocessing documents when prompts change?
- Should evaluation be deterministic, rubric-based, LLM-based, or hybrid?

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
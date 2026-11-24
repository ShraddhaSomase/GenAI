# MudraMitra — Daily Progress

## Day 1 — Project Setup
- [x] Create the MudraMitra project structure.
- [x] Add the project README and introductory Python files.
- [x] Create the initial CLI menu.

## Day 2 — Records Management
- [x] Create sample loan records.
- [x] Implement record viewing, searching, filtering, and summaries.
- [x] Implement the CLI records workflow.

## Day 3 — Data Ingestion
- [x] Create the Record dataclass.
- [x] Download the loan dataset from its source.
- [x] Parse and validate the loan records.
- [x] Support MUDRA and Stand-Up India knowledge documents.

## Day 4 — FastAPI and Search
- [x] Build the FastAPI application.
- [x] Add health and records endpoints.
- [x] Implement search functionality.
- [x] Add API testing.

## Day 5 — LLM Fundamentals
- [x] Add LLM learning notes.
- [x] Prepare evaluation questions.
- [x] Document the LLM workflow.

## Day 6 — LLM Integration and Evaluation
- [x] Integrate the Groq LLM API.
- [x] Compare prompts and evaluate responses.
- [x] Document evaluation results.

## Day 7 — Document Processing and Retrieval
- [x] Process government scheme documents.
- [x] Implement document chunking.
- [x] Generate and store document embeddings.
- [x] Set up ChromaDB vector storage.

## Day 8 — RAG Question Answering
- [x] Implement semantic and keyword hybrid retrieval.
- [x] Build the RAG question-answering pipeline.
- [x] Return source citations with answers.
- [x] Evaluate answerability, citation coverage, and source accuracy.

## Day 9 — Agent and Tools
- [x] Implement the LangGraph agent workflow.
- [x] Add the EMI schedule calculator.
- [x] Integrate tool execution and human approval.

## Day 10 — Streamlit Interface
- [x] Build the Streamlit chat interface.
- [x] Display answers and source citations.
- [x] Add user feedback functionality.

## Day 11 — Checkpoint 2 Features
- [x] Add the loan amount picker.
- [x] Add RAG and Agent modes.
- [x] Display scheme categories and document-conflict information.
- [x] Save user feedback.

## Day 12 — Deployment and CI
- [x] Add Docker configuration for the API and UI.
- [x] Add Docker Compose configuration.
- [x] Configure GitHub Actions for linting, tests, and Docker builds.
- [x] Document local and deployed application access.

## Day 13 — Production Readiness
- [x] Add prompt-injection safeguards.
- [x] Implement response caching.
- [x] Add request latency and token-usage logging.
- [x] Validate question length and API errors.
- [x] Expand automated tests to cover production-readiness features.
- [x] Verify Ruff and Pytest checks.

## Day 14 — Interview Preparation and Final Documentation
- [x] Prepare the 60-second MudraMitra project pitch.
- [x] Document the hardest technical problem using the STAR format.
- [x] Prepare likely technical interview questions and answers.
- [x] Document the project demo run-of-show.
- [x] Add technical concepts to review.
- [x] Create this root-level PROGRESS.md file.

---

## Verification Notes

- The latest recorded test run passed all 50 tests.
- Ruff checks passed after fixing the import order in app/vectorstore.py.
- The final Git tag exists locally.
- The Day 14 interview preparation document is available at docs/interview.md.

## Follow-up Improvements

The following are not claimed as completed features:
- Implement and verify automatic publication-date-aware ranking.
- Implement general automatic conflict detection and dual-source citations.
- Complete two actual end-to-end demo rehearsals.

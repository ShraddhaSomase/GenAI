# MudraMitra — AI-Powered Loan Assistant

## Project Overview

Developed an AI-powered loan assistant that helps users understand
Pradhan Mantri Mudra Yojana (PMMY) and Stand-Up India loan schemes.

The application retrieves relevant information from government
documents and generates answers with source citations using
Retrieval-Augmented Generation (RAG).

## Key Responsibilities and Features

- Developed REST APIs using Python and FastAPI.
- Implemented hybrid search combining semantic and keyword retrieval.
- Integrated a Groq-hosted LLM for document-grounded question answering.
- Implemented RAG-based answers with source and page citations.
- Added citation validation to reduce unsupported responses.
- Added prompt-injection safeguards for user questions and retrieved content.
- Implemented in-memory response caching with a 5-minute TTL.
- Added request latency and LLM token-usage logging.
- Built automated tests using Pytest.
- Worked with ChromaDB, LangGraph, and Streamlit.

## Technology Stack

Python, FastAPI, RAG, LLM, Groq, ChromaDB, LangGraph,
Streamlit, Pytest, Git, Docker.

## Evaluation Results

Existing project evaluation at top_k=5:

- Overall evaluation score: 92.77%.
- Answerability accuracy: 100%.
- Citation coverage: 100%.
- Source accuracy: 100%.
- Automated test suite: 50 passing tests.

## Resume Description

Developed MudraMitra, an AI-powered loan assistant using Python,
FastAPI, RAG, and Groq LLMs to retrieve information from government
documents and generate cited answers. Implemented hybrid search,
citation validation, prompt-injection safeguards, response caching,
and request monitoring. Achieved a 92.77% overall RAG evaluation
score and maintained 50 passing automated tests.

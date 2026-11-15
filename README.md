# MudraMitra

## About

MudraMitra is a Python project I am developing to manage financial records and provide information about MUDRA loans. I started with basic Python features and gradually added more functionality as I learned new technologies.

## Features

- Add, view, search and manage financial records.
- Store financial records using JSON.
- Provide APIs using FastAPI.
- Search records using TF-IDF and cosine similarity.
- Process PDF documents and divide them into smaller chunks.
- Generate embeddings using Sentence Transformers.
- Store document embeddings in ChromaDB.
- Find relevant information using semantic and hybrid search.
- Answer MUDRA-related questions using RAG and Groq LLM.
- Provide citations with document names and page numbers.
- Refuse to answer when information is not available in the documents.

## Technologies Used

- Python
- FastAPI
- Pandas
- Scikit-learn
- ChromaDB
- Sentence Transformers
- Groq LLM
- JSON
- Git and GitHub

## How to Run

1. Open the project folder in PowerShell.

2. Create a virtual environment (first time only):

   python -m venv .venv

3. Activate the virtual environment:

   .venv\Scripts\activate

4. Install dependencies:

   pip install -r requirements.txt

5. Start the API:

   uvicorn app.main:app --reload

6. Open the API documentation:

   http://127.0.0.1:8000/docs

## API Endpoints

- GET /health - Checks whether the API is running.
- GET /records - Displays financial records.
- GET /records/{id} - Displays one financial record.
- GET /search?q=rent - Searches financial records.
- POST /questions - Saves user questions.
- GET /search/semantic?q=loan - Searches documents using semantic search.
- POST /chat - Generates an LLM response.
- POST /ask - Answers questions using RAG and provides citations.

## Other Useful Commands

- python analysis/explore.py - Explores the financial dataset.
- python -m app.smart_search - Runs smart search.
- python -m app.cli - Starts the command-line menu.
- python -m app.chunking - Creates document chunks.
- python -m eval.run_semantic_eval - Runs semantic search evaluation.
- python -m eval.run_eval - Runs RAG evaluation.

## Day 8 - RAG Question Answering

I added a question-answering feature using Retrieval-Augmented Generation (RAG).

When a user asks a question, the system first searches the PDF documents and retrieves the most relevant chunks. The Groq LLM uses the retrieved information to generate an answer.

I used ChromaDB to store document embeddings and hybrid search to combine semantic search with keyword matching.

The response includes citations with the document name, page number and chunk ID. If the required information is not available in the documents, the system returns a message saying that the information was not found instead of making up an answer.

## Evaluation

I tested the RAG system using 15 questions, including answerable and unanswerable questions. I compared two retrieval configurations.

### Top_k = 3

- Answerability accuracy: 93.33%
- Citation coverage: 91.67%
- Source accuracy: 91.67%
- Keyword accuracy: 40.25%
- Overall score: 82.05%

### Top_k = 5

- Answerability accuracy: 100%
- Citation coverage: 100%
- Source accuracy: 100%
- Keyword accuracy: 63.83%
- Overall score: 92.77%

I selected top_k = 5 because it achieved the better overall score in my evaluation.

Detailed evaluation results are available in eval/eval_results.json.

## Project Progress

I am developing MudraMitra step by step. I started with Python basics and financial record management. Later, I added APIs, smart search, document processing, embeddings, vector storage and RAG-based question answering.

I will continue improving the project by testing the answers and making the search results more accurate.

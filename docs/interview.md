# MudraMitra — Interview Preparation

## 1. 60-Second Project Pitch

MudraMitra is an AI loan-information assistant for PMMY and Stand-Up India. I built it with Python, FastAPI, Streamlit, ChromaDB, and a retrieval-augmented generation pipeline. A question is matched against indexed government documents with hybrid semantic and keyword search; the answer includes source citations, and the API checks that cited chunks actually exist. The app also has a loan-amount picker, an agent endpoint, input safeguards, response caching, and request and token-usage logging.

The hardest design challenge is conflicting or outdated policy documents. An older bank PDF says the Stand-Up India margin can be 25%, while a 2022 Ministry FAQ says up to 15%. Separately, Tarun Plus (Rs 10–20 lakh) is newer than the 2021 FAQ. The assistant should use publication date to rank applicable evidence, but still show the conflict and cite both sources instead of silently choosing one. The current search ranks relevance, not document date; I treat date-aware ranking and general conflict presentation as the next improvement, rather than claiming they are already implemented.

## 2. Ten Likely Interview Questions and Answers

### Q1. What is MudraMitra?

MudraMitra is an AI assistant that helps people understand PMMY and Stand-Up India loan information. It retrieves passages from indexed documents and returns a grounded answer with citations. The Streamlit UI includes a loan-amount picker, and a FastAPI service exposes the search, RAG, and agent features.

### Q2. Why did you choose RAG?

The answers need to be grounded in scheme documents, including details that can change. RAG retrieves relevant passages before generation, so the model can answer from that evidence and cite it instead of relying only on its training data.

### Q3. Walk me through a question from request to answer.

The `/ask` endpoint validates the question and checks the response cache. On a cache miss, hybrid search retrieves document chunks. The RAG pipeline sends those chunks to the LLM, parses its JSON response, and validates citation numbers against the retrieved chunks before returning the answer and source metadata.

### Q4. What do you mean by hybrid search?

It combines semantic search, which looks for meaning, with keyword matching, which catches exact terms. MudraMitra combines their rankings so a relevant passage can be found even when the question uses different wording, while exact scheme names and figures still help retrieval.

### Q5. Why did you use ChromaDB?

ChromaDB stores the document embeddings and metadata and supports vector similarity search. It gives the project a local persistent vector store for retrieving passages to use in RAG.

### Q6. How do you reduce unsupported answers?

The prompt restricts answers to the retrieved context. The pipeline parses the model response and accepts only citation numbers that refer to retrieved chunks; if it cannot verify a citation, it returns an unverified response rather than presenting it as supported.

### Q7. How do you handle conflicting or outdated documents?

The example I use is an older bank PDF stating a 25% margin and a 2022 Ministry FAQ stating up to 15%. I would preserve both passages, rank the applicable newer document first using publication date, and show both values with their source dates and citations. Tarun Plus (Rs 10–20 lakh) is another useful test: it is newer than the 2021 FAQ, so the answer should not treat that FAQ as the latest word on the category.

Today, hybrid search ranks relevance and the loan picker displays a static Stand-Up India margin note; document publication dates are not yet indexed for date-aware ranking. I would be clear about that boundary in a demo: date-aware ranking and general conflict detection are the next step, not a feature I claim is already complete.

### Q8. What did you do about prompt injection?

The system prompt treats both the user question and retrieved document text as untrusted evidence. It tells the model not to follow instructions in either that attempt to change its role, override its rules, or reveal secrets. This is a safeguard, not a substitute for validating inputs and outputs in the application.

### Q9. How did you improve performance and observability?

The `/ask` API caches successful responses in memory, with a limit of 128 entries and a five-minute TTL. It also logs request latency and token usage when available, which helps distinguish cache hits from requests that call the model.

### Q10. How did you test the project?

I use Pytest for the API, records, search, agent tools, and production-readiness behavior, including caching and input safeguards. I also use Ruff for linting. Before quoting a test count, I run the current suite so the number reflects the checked-out version.

## 3. Hardest Problem — STAR Answer

### Situation

The document set contains different versions and sources. An older bank PDF says the Stand-Up India margin requirement is 25%, while the 2022 Ministry FAQ says up to 15%. Tarun Plus, covering Rs 10–20 lakh, is newer than the 2021 FAQ.

### Task

The assistant must not turn a retrieval ranking into a false claim that one document settles every case. It needs to favor the latest applicable evidence while making meaningful disagreement visible and traceable.

### Action

My target behavior is to retain publication date and source metadata, rank applicable evidence by date, and return both sides of a conflict with citations and a clear explanation. I also tested the reasoning against Tarun Plus: a 2021 FAQ should not outrank a newer document just because its wording happens to match better.

In the current implementation, hybrid retrieval ranks semantic and keyword relevance, citation numbers are checked against the retrieved chunks, and the loan picker shows a Stand-Up India margin note. It does not yet index publication dates or perform general date-aware conflict ranking, so I describe that as the next improvement rather than an already shipped capability.

### Result

This challenge shaped a transparent answer standard for MudraMitra: use the latest applicable source as the lead, but show and cite conflicting evidence rather than silently dropping it. It also gave me a concrete test case for improving document metadata and retrieval.

## 4. Technical Concepts to Review

- Python, FastAPI, and REST APIs
- Retrieval-Augmented Generation (RAG)
- Embeddings and vector search
- ChromaDB
- Semantic search, keyword search, and hybrid ranking
- Citation validation and source metadata
- Prompt injection and untrusted input
- In-memory caching and TTL
- Pytest and Ruff
- Streamlit and Docker

## 5. Demo Run of Show

1. Introduce MudraMitra and the document-grounded answering goal.
2. Open the Streamlit UI and explain the two available modes.
3. Ask a question about Shishu, Kishor, or Tarun and show the answer and citations.
4. Move the loan picker into the Rs 10–20 lakh range and point out Tarun Plus.
5. Move it into Stand-Up India eligibility and show the margin-disagreement note.
6. Explain the 25% older bank document versus the up-to-15% 2022 Ministry FAQ; be clear that general date-aware ranking is not yet implemented.
7. Open FastAPI Swagger docs and show the `/ask` request and response shape.
8. Close with the safeguards, caching, tests, and the next step: date-aware source ranking with visible conflicts.

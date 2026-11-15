"""RAG pipeline: retrieve documents and generate cited answers."""

import json
import re

from app.llm import client
from app.vectorstore import hybrid_search


MODEL_NAME = "openai/gpt-oss-20b"


def ask_question(question, top_k=4):
    """Answer a question using retrieved document chunks and citations."""

    question = question.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "found": False,
            "citations": [],
            "retrieved_chunks": 0
        }

    # Step 1: Retrieve relevant document chunks
    chunks = hybrid_search(question, n_results=top_k)

    if not chunks:
        return {
            "answer": "Sorry, I could not find relevant information in my documents.",
            "found": False,
            "citations": [],
            "retrieved_chunks": 0
        }

    # Step 2: Prepare context with citation numbers
    context_parts = []

    for index, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"""
[CITATION {index}]
Source: {chunk['source']}
Page: {chunk['page']}
Title: {chunk['title']}
Content: {chunk['text']}
"""
        )

    context = "\n".join(context_parts)

    # Step 3: Ask the LLM to answer only from retrieved context
    system_prompt = """
You are MudraMitra, an accurate assistant for MUDRA loan information.

Rules:
1. Answer only using the supplied document context.
2. Never use outside knowledge or invent information.
3. If the context does not contain enough information to answer,
   set found to false.
4. If found is false, explain that the information is unavailable.
5. When found is true, include the citation numbers that support
   your answer.
6. Use simple and clear language.
7. Return only valid JSON in this format:

{
  "found": true,
  "answer": "Your answer here",
  "citations": [1]
}

If the answer is unavailable, return:

{
  "found": false,
  "answer": "The requested information is not available in my documents.",
  "citations": []
}
"""

    user_prompt = f"""
DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

Answer using only the document context.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=700
    )

    raw_answer = response.choices[0].message.content or ""

    # Step 4: Parse the LLM JSON response
    try:
        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            raw_answer.strip(),
            flags=re.IGNORECASE
        )

        result = json.loads(cleaned)

    except (json.JSONDecodeError, TypeError):
        return {
            "answer": "Sorry, I could not generate a reliable answer.",
            "found": False,
            "citations": [],
            "retrieved_chunks": len(chunks)
        }

    # Step 5: Validate the found field and citation numbers
    found = result.get("found") is True
    citation_numbers = result.get("citations", [])

    if not found or not isinstance(citation_numbers, list):
        return {
            "answer": str(
                result.get(
                    "answer",
                    "The requested information is not available in my documents."
                )
            ),
            "found": False,
            "citations": [],
            "retrieved_chunks": len(chunks)
        }

    valid_numbers = []

    for number in citation_numbers:
        if type(number) is int and 1 <= number <= len(chunks):
            if number not in valid_numbers:
                valid_numbers.append(number)

    # Do not return an answer without supporting citations
    if not valid_numbers:
        return {
            "answer": "Sorry, I could not verify an answer from the retrieved documents.",
            "found": False,
            "citations": [],
            "retrieved_chunks": len(chunks)
        }

    # Step 6: Build citations from actual retrieved metadata
    citations = []

    for number in valid_numbers:
        chunk = chunks[number - 1]

        citations.append({
            "citation": number,
            "source": chunk["source"],
            "page": chunk["page"],
            "title": chunk["title"],
            "chunk_id": chunk["id"]
        })

    return {
        "answer": str(result.get("answer", "")),
        "found": True,
        "citations": citations,
        "retrieved_chunks": len(chunks)
    }


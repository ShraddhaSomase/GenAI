import re
from pathlib import Path

from app.vectorstore import semantic_search

questions_file = Path("eval/questions.md")
output_file = Path("eval/search_results.md")

text = questions_file.read_text(encoding="utf-8")

# Keep only the actual questions, excluding evaluation criteria.
question_section = text.split("## Unanswerable Question")[0]
question_section = question_section.split("## Evaluation Criteria")[0]

questions = re.findall(
    r"^\s*\d+\.\s+(.+)$",
    question_section,
    flags=re.MULTILINE
)

if len(questions) != 10:
    raise ValueError(
        f"Expected 10 questions, but found {len(questions)}"
    )

lines = [
    "# Day 7 - Semantic Search Evaluation",
    "",
    f"Total questions evaluated: {len(questions)}",
    "Embedding model: all-MiniLM-L6-v2",
    "Vector database: ChromaDB",
    "Top results per question: 3",
    ""
]

for number, question in enumerate(questions, start=1):
    print(f"Evaluating {number}/10: {question}")

    results = semantic_search(question, n_results=3)

    lines.extend([
        f"## Question {number}",
        "",
        f"**Query:** {question}",
        "",
        f"**Results found:** {len(results)}",
        ""
    ])

    for rank, result in enumerate(results, start=1):
        lines.extend([
            f"### Result {rank}",
            "",
            f"- ID: `{result['id']}`",
            f"- Source: {result['source']}",
            f"- Page: {result['page']}",
            f"- Title: {result['title']}",
            f"- Distance: {result['distance']:.4f}",
            f"- Text: {result['text']}",
            ""
        ])

output_file.write_text("\n".join(lines), encoding="utf-8")

print("\nEvaluation completed!")
print("Questions evaluated:", len(questions))
print("Report saved:", output_file)

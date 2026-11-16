import json
import re
from pathlib import Path

from app.llm import get_llm_response

QUESTIONS_FILE = Path("eval/questions.md")
RESULTS_FILE = Path("eval/prompt_comparison_results.json")
REPORT_FILE = Path("eval/prompt_compare.md")


def load_questions():
    text = QUESTIONS_FILE.read_text(encoding="utf-8-sig")

    text = text.split("## Unanswerable Question")[0]
    questions = []
    for line in text.splitlines():
        match = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if match:
            questions.append({
                "id": int(match.group(1)),
                "question": match.group(2).strip()
            })

    if len(questions) != 10:
        raise ValueError(
            f"Expected exactly 10 questions, found {len(questions)}"
        )

    return questions


def save_results(results):
    RESULTS_FILE.write_text(
        json.dumps(results, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


def create_report(results):
    lines = [
        "# MudraMitra - Prompt Comparison",
        "",
        "## Objective",
        "",
        "Compare task_prompt_v1 and task_prompt_v2 using the same 10 questions.",
        "Both versions use the same RAG retrieval configuration.",
        "",
        "## Results",
        "",
        "| No. | Question | V1 Answer | V1 Confidence | V1 Correct? | V2 Answer | V2 Confidence | V2 Correct? |",
        "|---|---|---|---|---|---|---|---|"
    ]

    for item in results:
        if "v1" not in item or "v2" not in item:
            continue
        v1 = item["v1"]
        v2 = item["v2"]

        def clean(value):
            return str(value).replace("|", "\\|").replace("\n", " ").strip()

        lines.append(
            f"| {item['id']} "
            f"| {clean(item['question'])} "
            f"| {clean(v1['answer'])} "
            f"| {clean(v1['confidence'])} "
            f"| {v1['correct']} "
            f"| {clean(v2['answer'])} "
            f"| {clean(v2['confidence'])} "
            f"| {v2['correct']} |"
        )

    lines.extend([
        "",
        "## Evaluation Notes",
        "",
        "- Correctness must be checked against the actual MUDRA and Stand-Up India source records.",
        "- Question 6 is intentionally unanswerable. The chatbot must not invent an SBI interest rate.",
        "- Question 10 must not claim who decides repayment terms unless the records support that claim.",
        "- Correctness is marked Review until the answers are manually verified.",
        "",
        "## Final Comparison",
        "",
        "The winning prompt will be selected after reviewing all 10 answers for accuracy, completeness and hallucination control.",
        ""
    ])

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main():
    questions = load_questions()
    results = []

    print("Starting prompt comparison")
    print("Total questions:", len(questions))
    print("Total LLM calls: 20")

    for item in questions:
        print(f"\n========== QUESTION {item['id']} ==========")
        print(item["question"])

        result = {
            "id": item["id"],
            "question": item["question"]
        }

        for version in ("v1", "v2"):
            print(f"\nRunning prompt {version}...")

            response = get_llm_response(
                item["question"],
                task_version=version
            )

            result[version] = {
                "answer": response["answer"],
                "confidence": response["confidence"],
                "follow_up": response["follow_up"],
                "correct": "Review"
            }

            print("Answer:", response["answer"])
            print("Confidence:", response["confidence"])

            results.append(result.copy()) if False else None

            # Save completed responses after each question/version.
            current = next(
                (r for r in results if r["id"] == item["id"]),
                None
            )

            if current is None:
                results.append(result)
            else:
                current[version] = result[version]

            save_results(results)
            create_report(results)

    print("\n========== COMPARISON COMPLETED ==========")
    print("Questions tested:", len(results))
    print("Prompt versions: v1 and v2")
    print("Total responses:", len(results) * 2)
    print("Results saved:", RESULTS_FILE)
    print("Report saved:", REPORT_FILE)


if __name__ == "__main__":
    main()




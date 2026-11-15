import json
from pathlib import Path

from app.rag import ask_question


EVAL_FILE = Path("eval/eval_set.json")
RESULT_FILE = Path("eval/eval_results.json")


def evaluate_configuration(questions, top_k):
    results = []

    for item in questions:
        print(f"Testing Q{item['id']} with top_k={top_k}...")

        response = ask_question(
            item["question"],
            top_k=top_k
        )

        expected_answerable = item["answerable"]
        actual_answerable = response["found"]

        answerability_correct = (
            expected_answerable == actual_answerable
        )

        citations = response.get("citations", [])

        citation_present = (
            len(citations) > 0 if expected_answerable else True
        )

        expected_source = item.get("expected_source")

        source_found = (
            any(
                citation["source"] == expected_source
                for citation in citations
            )
            if expected_source and expected_answerable
            else not expected_answerable
        )

        answer = response.get("answer", "").lower()

        keywords = item.get("expected_keywords", [])

        keyword_matches = sum(
            keyword.lower() in answer
            for keyword in keywords
        )

        keyword_score = (
            keyword_matches / len(keywords)
            if keywords
            else (1.0 if not expected_answerable else 0.0)
        )

        results.append({
            "id": item["id"],
            "question": item["question"],
            "expected_answerable": expected_answerable,
            "actual_answerable": actual_answerable,
            "answerability_correct": answerability_correct,
            "citation_present": citation_present,
            "expected_source_found": source_found,
            "keyword_score": round(keyword_score, 2),
            "answer": response["answer"],
            "citations": citations
        })

    total = len(results)

    answerability_accuracy = sum(
        r["answerability_correct"] for r in results
    ) / total

    answerable_results = [
        r for r in results if r["expected_answerable"]
    ]

    citation_coverage = (
        sum(r["citation_present"] for r in answerable_results)
        / len(answerable_results)
    )

    source_accuracy = (
        sum(r["expected_source_found"] for r in answerable_results)
        / len(answerable_results)
    )

    keyword_accuracy = (
        sum(r["keyword_score"] for r in answerable_results)
        / len(answerable_results)
    )

    overall_score = (
        answerability_accuracy * 0.40
        + citation_coverage * 0.20
        + source_accuracy * 0.20
        + keyword_accuracy * 0.20
    )

    return {
        "top_k": top_k,
        "total_questions": total,
        "answerability_accuracy": round(answerability_accuracy * 100, 2),
        "citation_coverage": round(citation_coverage * 100, 2),
        "source_accuracy": round(source_accuracy * 100, 2),
        "keyword_accuracy": round(keyword_accuracy * 100, 2),
        "overall_score": round(overall_score * 100, 2),
        "details": results
    }


def main():
    with open(EVAL_FILE, "r", encoding="utf-8-sig") as file:
        questions = json.load(file)

    configurations = [3, 5]
    all_results = []

    for top_k in configurations:
        print(f"\nEvaluating top_k={top_k}")
        result = evaluate_configuration(questions, top_k)
        all_results.append(result)

    best_result = max(
        all_results,
        key=lambda result: result["overall_score"]
    )

    output = {
        "configurations": all_results,
        "best_configuration": best_result["top_k"]
    }

    with open(RESULT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    print("\n========== EVALUATION SUMMARY ==========")

    for result in all_results:
        print(f"\ntop_k: {result['top_k']}")
        print(f"Answerability accuracy: {result['answerability_accuracy']}%")
        print(f"Citation coverage: {result['citation_coverage']}%")
        print(f"Source accuracy: {result['source_accuracy']}%")
        print(f"Keyword accuracy: {result['keyword_accuracy']}%")
        print(f"Overall score: {result['overall_score']}%")

    print("\nBest configuration: top_k =", best_result["top_k"])
    print("Detailed results saved to:", RESULT_FILE)


if __name__ == "__main__":
    main()

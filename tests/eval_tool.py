from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(APP_DIR))

import argparse
import json
import statistics
import time
from typing import Any, Dict, List

from app.query_engine import OfflineGitaQA


def load_questions(path: str) -> List[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]


def normalize_answer(text: str) -> str:
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    return text


def get_citations_from_sources(sources: List[Dict[str, Any]], limit: int = 5) -> List[str]:
    citations: List[str] = []
    for src in sources[:limit]:
        verse = src.get("verse")
        page = src.get("page")
        citations.append(verse or f"page {page}")
    return citations


def answer_quality_signals(answer: str) -> Dict[str, Any]:
    answer = normalize_answer(answer)
    lower = answer.lower()

    return {
        "length_chars": len(answer),
        "length_words": len(answer.split()),
        "has_answer_header": "answer:" in lower,
        "has_gita_perspective": "gita perspective:" in lower,
        "has_supporting_verses": "supporting verses:" in lower,
        "has_citations_header": "citations:" in lower,
        "mentions_karma_yoga": "karma yoga" in lower,
        "mentions_paramatma": "paramatma" in lower or "supersoul" in lower,
    }


def run_eval(
    config: str,
    questions_file: str,
    output: str,
    label: str,
    answer_language: str,
    document_language: str,
    query_language: str,
) -> None:
    questions = load_questions(questions_file)
    qa = OfflineGitaQA(config_path=config)

    results: List[Dict[str, Any]] = []
    total_start = time.time()

    for i, question in enumerate(questions, start=1):
        start = time.time()
        result = qa.answer(
            question=question,
            answer_language=answer_language,
            document_language=document_language,
            query_language=query_language,
        )
        elapsed = round(time.time() - start, 3)

        answer = normalize_answer(result.get("answer", ""))
        sources = result.get("sources", [])
        citations = get_citations_from_sources(sources)
        signals = answer_quality_signals(answer)

        row = {
            "index": i,
            "question": question,
            "expanded_query": result.get("expanded_query", ""),
            "answer": answer,
            "citations": citations,
            "num_sources": len(sources),
            "llm_backend": result.get("llm_backend", ""),
            "runtime_device": result.get("runtime_device", ""),
            "embedding_device": result.get("embedding_device", ""),
            "vector_backend": result.get("vector_backend", ""),
            "elapsed_seconds": elapsed,
            "signals": signals,
        }
        results.append(row)

        print("=" * 90)
        print(f"[{i}/{len(questions)}] {question}")
        print(f"Elapsed: {elapsed}s")
        print(f"Citations: {', '.join(citations)}")
        print(answer)
        print()

    total_elapsed = round(time.time() - total_start, 3)

    payload = {
        "label": label,
        "config": config,
        "questions_file": questions_file,
        "answer_language": answer_language,
        "document_language": document_language,
        "query_language": query_language,
        "total_questions": len(questions),
        "total_elapsed_seconds": total_elapsed,
        "results": results,
    }

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 90)
    print(f"Saved run: {out_path}")
    print(f"Label: {label}")
    print(f"Questions: {len(questions)}")
    print(f"Total elapsed: {total_elapsed}s")


def mean_or_zero(values: List[float]) -> float:
    return round(statistics.mean(values), 3) if values else 0.0


def pct(count: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{(100.0 * count / total):.1f}%"


def load_run(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def index_by_question(run: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {row["question"]: row for row in run.get("results", [])}


def compare_rows(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    a_citations = set(a.get("citations", []))
    b_citations = set(b.get("citations", []))

    a_signals = a.get("signals", {})
    b_signals = b.get("signals", {})

    return {
        "question": a["question"],
        "elapsed_a": a.get("elapsed_seconds", 0.0),
        "elapsed_b": b.get("elapsed_seconds", 0.0),
        "elapsed_diff": round(b.get("elapsed_seconds", 0.0) - a.get("elapsed_seconds", 0.0), 3),
        "citations_a": a.get("citations", []),
        "citations_b": b.get("citations", []),
        "citation_overlap": sorted(a_citations.intersection(b_citations)),
        "num_citations_a": len(a_citations),
        "num_citations_b": len(b_citations),
        "answer_len_a": a_signals.get("length_words", 0),
        "answer_len_b": b_signals.get("length_words", 0),
        "has_gita_perspective_a": a_signals.get("has_gita_perspective", False),
        "has_gita_perspective_b": b_signals.get("has_gita_perspective", False),
        "has_supporting_verses_a": a_signals.get("has_supporting_verses", False),
        "has_supporting_verses_b": b_signals.get("has_supporting_verses", False),
        "answer_a": a.get("answer", ""),
        "answer_b": b.get("answer", ""),
    }


def build_markdown_report(run_a: Dict[str, Any], run_b: Dict[str, Any]) -> str:
    label_a = run_a.get("label", "run_a")
    label_b = run_b.get("label", "run_b")

    map_a = index_by_question(run_a)
    map_b = index_by_question(run_b)

    common_questions = [q for q in map_a.keys() if q in map_b]
    comparisons = [compare_rows(map_a[q], map_b[q]) for q in common_questions]

    total = len(common_questions)

    mean_elapsed_a = mean_or_zero([c["elapsed_a"] for c in comparisons])
    mean_elapsed_b = mean_or_zero([c["elapsed_b"] for c in comparisons])

    gita_a = sum(1 for c in comparisons if c["has_gita_perspective_a"])
    gita_b = sum(1 for c in comparisons if c["has_gita_perspective_b"])

    support_a = sum(1 for c in comparisons if c["has_supporting_verses_a"])
    support_b = sum(1 for c in comparisons if c["has_supporting_verses_b"])

    longer_b = sum(1 for c in comparisons if c["answer_len_b"] > c["answer_len_a"])
    changed_citations = sum(1 for c in comparisons if c["citations_a"] != c["citations_b"])

    lines: List[str] = []
    lines.append(f"# Evaluation Comparison: {label_a} vs {label_b}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Questions compared: **{total}**")
    lines.append(f"- Average latency ({label_a}): **{mean_elapsed_a}s**")
    lines.append(f"- Average latency ({label_b}): **{mean_elapsed_b}s**")
    lines.append(f"- `Gita perspective` present in {label_a}: **{gita_a}/{total} ({pct(gita_a, total)})**")
    lines.append(f"- `Gita perspective` present in {label_b}: **{gita_b}/{total} ({pct(gita_b, total)})**")
    lines.append(f"- `Supporting verses` present in {label_a}: **{support_a}/{total} ({pct(support_a, total)})**")
    lines.append(f"- `Supporting verses` present in {label_b}: **{support_b}/{total} ({pct(support_b, total)})**")
    lines.append(f"- Questions where {label_b} answer is longer: **{longer_b}/{total} ({pct(longer_b, total)})**")
    lines.append(f"- Questions where citations changed: **{changed_citations}/{total} ({pct(changed_citations, total)})**")
    lines.append("")
    lines.append("## Per-question comparison")
    lines.append("")

    for c in comparisons:
        lines.append(f"### {c['question']}")
        lines.append("")
        lines.append(f"- Latency: {label_a} = **{c['elapsed_a']}s**, {label_b} = **{c['elapsed_b']}s**, diff = **{c['elapsed_diff']}s**")
        lines.append(f"- Citations {label_a}: `{', '.join(c['citations_a'])}`")
        lines.append(f"- Citations {label_b}: `{', '.join(c['citations_b'])}`")
        lines.append(f"- Citation overlap: `{', '.join(c['citation_overlap']) if c['citation_overlap'] else 'none'}`")
        lines.append(f"- Answer length (words): {label_a} = **{c['answer_len_a']}**, {label_b} = **{c['answer_len_b']}**")
        lines.append(f"- Has `Gita perspective`: {label_a} = **{c['has_gita_perspective_a']}**, {label_b} = **{c['has_gita_perspective_b']}**")
        lines.append(f"- Has `Supporting verses`: {label_a} = **{c['has_supporting_verses_a']}**, {label_b} = **{c['has_supporting_verses_b']}**")
        lines.append("")
        lines.append(f"#### {label_a} answer")
        lines.append("")
        lines.append("```text")
        lines.append(c["answer_a"])
        lines.append("```")
        lines.append("")
        lines.append(f"#### {label_b} answer")
        lines.append("")
        lines.append("```text")
        lines.append(c["answer_b"])
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def compare_runs(path_a: str, path_b: str, output: str) -> None:
    run_a = load_run(path_a)
    run_b = load_run(path_b)

    report = build_markdown_report(run_a, run_b)

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    print(f"Saved comparison report to: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run evaluation and save a JSON result file")
    run_parser.add_argument("--config", default="app/config.yaml")
    run_parser.add_argument("--questions", default="tests/gita_eval_questions.txt")
    run_parser.add_argument("--output", required=True)
    run_parser.add_argument("--label", required=True)
    run_parser.add_argument("--answer-language", default="English", choices=["English", "Sanskrit"])
    run_parser.add_argument("--document-language", default="Auto")
    run_parser.add_argument("--query-language", default="Auto")

    compare_parser = subparsers.add_parser("compare", help="Compare two saved evaluation JSON runs")
    compare_parser.add_argument("--a", required=True, help="First run JSON")
    compare_parser.add_argument("--b", required=True, help="Second run JSON")
    compare_parser.add_argument("--output", required=True, help="Markdown comparison output path")

    args = parser.parse_args()

    if args.command == "run":
        run_eval(
            config=args.config,
            questions_file=args.questions,
            output=args.output,
            label=args.label,
            answer_language=args.answer_language,
            document_language=args.document_language,
            query_language=args.query_language,
        )
    elif args.command == "compare":
        compare_runs(
            path_a=args.a,
            path_b=args.b,
            output=args.output,
        )


if __name__ == "__main__":
    main()
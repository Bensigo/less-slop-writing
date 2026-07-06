#!/usr/bin/env python3
"""Surface-level scanner for common AI-slop writing tells."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Pattern:
    category: str
    regex: str
    reason: str


PATTERNS = [
    Pattern("significance amplifiers", r"\b(pivotal|game-changing|transformative|revolutionary|groundbreaking|cutting-edge|powerful)\b", "Inflates ordinary claims."),
    Pattern("tourism and heritage language", r"\b(nestled|vibrant|rich heritage|hidden gem|bustling|iconic)\b", "Sounds like travel-brochure filler."),
    Pattern("hedge words", r"\b(arguably|fairly|somewhat|notable|worth noting|tends to|in many cases|often)\b", "Weakens or cushions the claim."),
    Pattern("filler qualifiers", r"\b(really|truly|incredibly|very|deeply|highly)\b", "Adds intensity without adding information."),
    Pattern("sycophantic openers", r"\b(great question|excellent question|happy to help|i'?d be happy to|excellent point)\b", "Adds fake praise or service phrasing."),
    Pattern("AI transition words", r"\b(moreover|furthermore|additionally|in addition|nevertheless|therefore)\b", "Uses stiff connectors where direct phrasing may work better."),
    Pattern("verb inflation", r"\b(leverage|utilize|craft|delve|bolster|foster|facilitate|empower|unlock|harness)\b", "Uses inflated verbs instead of plain ones."),
    Pattern("meta-commentary", r"\b(it'?s important to note|it is important to note|key takeaway|this article will|in this post|worth mentioning)\b", "Announces the point instead of making it."),
    Pattern("real-truth constructions", r"\b(at the end of the day|what it really comes down to|the reality is|the truth is|when all is said and done)\b", "Adds fake-wisdom windup."),
    Pattern("manufactured hooks", r"\b(in today'?s rapidly evolving|now more than ever|in an increasingly digital|the way we think about)\b", "Starts with a generic broad hook."),
    Pattern("mid-narrative pivots", r"\b(here'?s where it gets interesting|but that'?s not all|the twist|here'?s the thing)\b", "Manufactures drama."),
    Pattern("negative parallelism", r"\b(it'?s not just about|not only .* but also|not just .* it'?s about)\b", "Often swaps a concrete point for a vaguer one."),
    Pattern("collaborative language", r"\b(let'?s dive (?:in|into)|let'?s explore|let'?s unpack|let'?s break down|join us as)\b", "Creates fake collaboration."),
    Pattern("corporate jargon", r"\b(content ecosystem|move the needle|drives? outcomes|unlocks? scalable growth|align strategy|digital transformation|meaningful engagement|holistic approach)\b", "Gestures at value without naming work."),
    Pattern("rigid outline structure", r"\b(firstly|secondly|thirdly|in conclusion|to conclude)\b", "May indicate school-essay structure."),
    Pattern("default redemption arc", r"\b(silver lining|growth opportunity|valuable lesson|ultimately made us stronger|better position long-term)\b", "Forces a positive lesson onto a negative outcome."),
    Pattern("relentless positivity", r"\b(excited|thrilled|incredible|amazing|can'?t wait|proud to announce)\b", "May overheat the emotional tone."),
    Pattern("excessive formality", r"\b(please do not hesitate|should you require|at your earliest convenience|kindly|regarding the aforementioned)\b", "Sounds stiff or distant."),
    Pattern("manufactured vulnerability", r"\b(i'?ll be honest|truth be told|to be transparent|not going to lie)\b", "Performs authenticity."),
    Pattern("apologetic hedging", r"\b(this might not apply|not necessarily|to some extent|depending on the situation|your mileage may vary)\b", "Over-qualifies the point."),
    Pattern("vague attribution", r"\b(research suggests|studies show|experts say|data shows|industry reports suggest)\b", "Claims authority without naming a source."),
    Pattern("explaining significance", r"\b(this matters because|why this matters|the reason this matters)\b", "Labels importance instead of proving it."),
    Pattern("avoiding specifics", r"\b(significant improvements|more structured|over time|several months|better results|real business outcomes)\b", "Avoids concrete names, numbers, dates, or mechanisms."),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Flag surface-level AI-slop writing tells.")
    parser.add_argument("path", nargs="?", help="Text or Markdown file to scan. Reads stdin when omitted.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    return parser.parse_args()


def read_input(path_value: str | None) -> str:
    if not path_value:
        return sys.stdin.read()

    path = Path(path_value)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def clean_snippet(value: str, limit: int = 140) -> str:
    snippet = re.sub(r"\s+", " ", value).strip()
    if len(snippet) <= limit:
        return snippet
    return snippet[: limit - 1].rstrip() + "..."


def find_pattern_hits(text: str) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for pattern in PATTERNS:
        for match in re.finditer(pattern.regex, text, flags=re.IGNORECASE | re.DOTALL):
            hits.append(
                {
                    "category": pattern.category,
                    "line": line_number(text, match.start()),
                    "match": clean_snippet(match.group(0)),
                    "reason": pattern.reason,
                }
            )
    return hits


def find_format_hits(text: str) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []

    for line_index, line in enumerate(text.splitlines(), start=1):
        em_dash_count = line.count("—")
        if em_dash_count >= 2:
            hits.append(
                {
                    "category": "em dash overuse",
                    "line": line_index,
                    "match": clean_snippet(line),
                    "reason": f"Line contains {em_dash_count} em dashes.",
                }
            )

        bold_matches = re.findall(r"\*\*([^*\n]{3,80})\*\*", line)
        if len(bold_matches) >= 2:
            hits.append(
                {
                    "category": "bold as decoration",
                    "line": line_index,
                    "match": clean_snippet(", ".join(bold_matches)),
                    "reason": "Multiple bold phrases in one line may be decorative emphasis.",
                }
            )

        if re.search(r"[\U0001F300-\U0001FAFF]", line):
            hits.append(
                {
                    "category": "emoji in professional contexts",
                    "line": line_index,
                    "match": clean_snippet(line),
                    "reason": "Emoji may create fake energy in professional prose.",
                }
            )

    return hits


def find_staccato_hits(text: str) -> list[dict[str, object]]:
    sentence_matches = list(re.finditer(r"[^.!?]+[.!?]", text))
    hits: list[dict[str, object]] = []

    for offset in range(max(0, len(sentence_matches) - 2)):
        cluster = sentence_matches[offset : offset + 3]
        words_per_sentence = [len(re.findall(r"\b[\w'-]+\b", match.group(0))) for match in cluster]
        if all(word_count <= 6 for word_count in words_per_sentence):
            combined = " ".join(clean_snippet(match.group(0), 80) for match in cluster)
            hits.append(
                {
                    "category": "staccato clusters",
                    "line": line_number(text, cluster[0].start()),
                    "match": clean_snippet(combined),
                    "reason": "Three short sentences in a row may create synthetic drama.",
                }
            )

    return hits


def scan(text: str) -> dict[str, object]:
    hits = find_pattern_hits(text) + find_format_hits(text) + find_staccato_hits(text)
    hits.sort(key=lambda item: (int(item["line"]), str(item["category"])))

    category_counts: dict[str, int] = {}
    for hit in hits:
        category = str(hit["category"])
        category_counts[category] = category_counts.get(category, 0) + 1

    return {
        "total_hits": len(hits),
        "category_counts": category_counts,
        "hits": hits,
    }


def print_markdown(result: dict[str, object]) -> None:
    print(f"# Slop Scan\n\nTotal surface flags: {result['total_hits']}\n")

    category_counts = result["category_counts"]
    if category_counts:
        print("## Category Counts")
        for category, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0])):
            print(f"- {category}: {count}")
        print()

    print("## Hits")
    hits = result["hits"]
    if not hits:
        print("- No surface flags found. Manual review still required.")
        return

    for hit in hits:
        print(f"- Line {hit['line']}: `{hit['match']}` - {hit['category']}: {hit['reason']}")


def main() -> None:
    args = parse_args()
    text = read_input(args.path)
    result = scan(text)

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_markdown(result)


if __name__ == "__main__":
    main()

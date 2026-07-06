#!/usr/bin/env python3
"""Deterministic evals for the less-slop-writing skill package."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = ROOT / "SKILL.md"
TRIGGER_QUERIES = ROOT / "evals" / "trigger_queries.json"
EVALS = ROOT / "evals" / "evals.json"
SCANNER = ROOT / "scripts" / "slop_scan.py"

TRIGGER_PATTERNS = [
    r"\bai slop\b",
    r"\bless slop\b",
    r"\bgeneric\b",
    r"\bchatgpt\b",
    r"\bai-sounding\b",
    r"\bover-polished\b",
    r"\bvague\b",
    r"\bsharper copy\b",
    r"\bhuman-sounding\b",
    r"\bdirect\b",
    r"\b0-5 slop\b",
    r"\bslop scale\b",
    r"\bunlock scalable growth\b",
]


def load_scanner_module():
    spec = importlib.util.spec_from_file_location("slop_scan", SCANNER)
    if spec is None or spec.loader is None:
        raise AssertionError("Could not load scanner module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_frontmatter() -> dict[str, str]:
    text = SKILL_MD.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError("SKILL.md missing frontmatter")

    frontmatter = text.split("---\n", 2)[1]
    data: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def should_trigger(query: str) -> bool:
    return any(re.search(pattern, query, flags=re.IGNORECASE) for pattern in TRIGGER_PATTERNS)


def assert_metadata() -> None:
    data = load_frontmatter()
    assert data.get("name") == "less-slop-writing", "wrong skill name"
    description = data.get("description", "")
    assert 120 <= len(description) <= 1024, "description should be complete but not bloated"
    for phrase in ["AI slop", "rewriting", "reviewing", "vague", "hype", "missing specifics"]:
        assert phrase.lower() in description.lower(), f"description missing trigger phrase: {phrase}"


def assert_trigger_queries() -> None:
    queries = json.loads(TRIGGER_QUERIES.read_text(encoding="utf-8"))
    assert len(queries) >= 8, "expected multiple trigger eval cases"

    failures = []
    for item in queries:
        actual = should_trigger(item["query"])
        expected = item["should_trigger"]
        if actual != expected:
            failures.append({"query": item["query"], "expected": expected, "actual": actual})

    assert not failures, f"trigger query failures: {failures}"


def assert_eval_fixtures() -> None:
    data = json.loads(EVALS.read_text(encoding="utf-8"))
    assert data["skill_name"] == "less-slop-writing", "eval skill_name mismatch"
    assert len(data["evals"]) >= 3, "expected at least 3 eval cases"
    for item in data["evals"]:
        assert item.get("id"), "eval missing id"
        assert "Use the less-slop-writing skill" in item.get("prompt", ""), f"eval prompt should invoke skill: {item.get('id')}"
        assert len(item.get("assertions", [])) >= 3, f"eval needs assertions: {item.get('id')}"


def assert_scanner_behavior() -> None:
    scanner = load_scanner_module()
    sample = (
        "In today's rapidly evolving digital landscape, brands need a holistic content "
        "ecosystem that unlocks scalable growth and drives meaningful engagement. "
        "Let's dive into why this matters."
    )
    result = scanner.scan(sample)
    categories = set(result["category_counts"])
    expected = {"manufactured hooks", "corporate jargon", "collaborative language", "explaining significance"}
    missing = sorted(expected - categories)
    assert not missing, f"scanner missing expected categories: {missing}"
    assert result["total_hits"] >= 5, "scanner should catch several surface flags in the sample"

    clean_sample = "Dashboard filters shipped today. Account managers save about 20 minutes per weekly report."
    clean_result = scanner.scan(clean_sample)
    assert clean_result["total_hits"] == 0, "clean factual sample should not be flagged"


def main() -> None:
    checks = [
        ("metadata", assert_metadata),
        ("trigger queries", assert_trigger_queries),
        ("eval fixtures", assert_eval_fixtures),
        ("scanner behavior", assert_scanner_behavior),
    ]

    for name, check in checks:
        check()
        print(f"PASS {name}")

    print("PASS all evals")


if __name__ == "__main__":
    main()

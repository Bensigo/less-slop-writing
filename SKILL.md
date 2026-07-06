---
name: less-slop-writing
description: Use this skill when writing, rewriting, editing, reviewing, or scoring prose for AI slop, generic AI voice, vague marketing copy, over-polished business writing, LinkedIn-style filler, AI-sounding articles, proposals, emails, landing-page copy, docs, or social posts. Use it when the user asks for less slop, more direct writing, human-sounding writing, sharper copy, anti-AI-slop review, or a rewrite that removes hedging, hype, jargon, filler, fake enthusiasm, fake collaboration, vague attribution, and missing specifics.
---

# Less Slop Writing

## Core Rule

Make writing specific, direct, and useful. Do not polish vague ideas. Replace vague ideas with concrete facts, or mark the missing facts instead of inventing them.

## Workflow

1. Identify the mode: `write`, `audit`, `rewrite`, or `score`.
2. For detailed audits or rewrites, read `references/slop-taxonomy.md`.
3. If the input is a local text/Markdown file, run `scripts/slop_scan.py <file>` first and use its output as a surface scan, not a final verdict.
4. Check the text manually for substance problems the script cannot prove: missing specifics, unsupported claims, fake insight, generic structure, weak audience fit, and emotional tone mismatch.
5. Preserve the user's actual meaning. Cut filler, but do not remove necessary nuance.
6. When a sentence needs evidence the user has not provided, use `[specific needed: ...]` instead of fabricating names, numbers, dates, or results.

## Audit Output

Use this format unless the user asks for something else:

```markdown
**Verdict**
- Slop level: Low|Medium|High
- Main problem: one direct sentence

**Findings**
- `quoted phrase`: Category - why it weakens the text - concrete fix

**Rewrite**
<clean rewritten version, if requested or clearly useful>

**Missing Specifics**
- List only the facts needed to make the text credible.
```

Keep findings selective. Do not list every tiny issue if three root problems explain the draft.

## Rewrite Standards

- Prefer short sentences with normal verbs: use, make, build, fix, show, send, write.
- Remove throat-clearing: "it is important to note", "the key takeaway", "at the end of the day".
- Replace inflated claims with observable facts.
- Remove fake collaboration: "let's dive in", "let's explore", "we'll unpack".
- Remove fake praise and service language unless the genre requires it.
- Remove corporate filler: "unlock", "leverage", "ecosystem", "move the needle", "drive outcomes".
- Use bullets only when they improve scanning. Do not turn weak prose into weak bullets.
- Match tone to stakes. A dashboard filter update is useful, not thrilling.
- Keep claims sourced. "Research suggests" is not a source.
- If a paragraph says nothing actionable, rewrite it around an action, fact, example, or delete it.

## Scoring

Score on a 0-5 slop scale:

- `0`: Clean, specific, direct.
- `1`: Mostly clean, a few removable tells.
- `2`: Understandable but padded or generic.
- `3`: Noticeably AI-sounding; multiple repeated tells.
- `4`: Heavy slop; vague, over-structured, or over-polished.
- `5`: Mostly empty language; little concrete meaning survives.

Explain the score with evidence, not vibe.

## Script

Run the scanner for file-based inputs:

```bash
python3 scripts/slop_scan.py draft.md
python3 scripts/slop_scan.py draft.md --format json
```

The scanner flags obvious lexical and formatting tells. It cannot judge truth, audience fit, or whether a claim has evidence. Always pair it with manual review.

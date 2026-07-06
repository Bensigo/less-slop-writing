# Less Slop Writing

A Codex skill for writing, rewriting, auditing, and scoring prose for AI slop.

The skill focuses on direct, specific writing. It flags vague marketing copy, over-polished AI voice, hype, hedging, corporate jargon, fake collaboration, vague attribution, and missing specifics.

## Contents

- `SKILL.md`: skill trigger metadata and operating workflow.
- `references/slop-taxonomy.md`: 34 AI-slop patterns grouped by word, phrase, structure, tone, formatting, and content issues.
- `scripts/slop_scan.py`: deterministic surface scanner for common slop tells.
- `evals/`: trigger fixtures and deterministic eval runner.
- `agents/openai.yaml`: Codex UI metadata.

## Usage

Install the folder into Codex global skills:

```bash
cp -R less-slop-writing "${CODEX_HOME:-$HOME/.codex}/skills/less-slop-writing"
```

Run the scanner:

```bash
python3 scripts/slop_scan.py draft.md
python3 scripts/slop_scan.py draft.md --format json
```

Run evals:

```bash
python3 evals/run_evals.py
```

Restart Codex after installing the skill so it is picked up by the app.

# Less Slop Writing

An agent skill for writing, rewriting, auditing, and scoring prose for AI slop.

The skill focuses on direct, specific writing. It flags vague marketing copy, over-polished AI voice, hype, hedging, corporate jargon, fake collaboration, vague attribution, and missing specifics.

This skill is not Codex-specific. Any agent that can read a skill-style instruction folder can use it, including Codex, Claude-style agents, custom agent runners, or internal agent frameworks.

## Contents

- `SKILL.md`: skill trigger metadata and operating workflow.
- `references/slop-taxonomy.md`: 34 AI-slop patterns grouped by word, phrase, structure, tone, formatting, and content issues.
- `scripts/slop_scan.py`: deterministic surface scanner for common slop tells.
- `evals/`: trigger fixtures and deterministic eval runner.
- `agents/openai.yaml`: optional OpenAI/Codex UI metadata. Other agents can ignore it.

## Usage

Point your agent at `SKILL.md` and keep the bundled `references/`, `scripts/`, and `evals/` folders available. The skill is designed so the main instructions stay small, with the detailed slop taxonomy and scanner loaded only when needed.

## Install In Codex

Install the folder into Codex global skills:

```bash
cp -R less-slop-writing "${CODEX_HOME:-$HOME/.codex}/skills/less-slop-writing"
```

Restart Codex after installing the skill so it is picked up by the app.

## Install In Claude Code

Claude Code supports filesystem-based custom skills. Use one of these installs:

Personal install:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)" ~/.claude/skills/less-slop-writing
```

Project install:

```bash
mkdir -p .claude/skills
cp -R /path/to/less-slop-writing .claude/skills/less-slop-writing
```

Use the personal install when you want the skill available across Claude Code projects. Use the project install when you want to commit the skill into a specific repo.

Run the scanner:

```bash
python3 scripts/slop_scan.py draft.md
python3 scripts/slop_scan.py draft.md --format json
```

Run evals:

```bash
python3 evals/run_evals.py
```

For other agents, use that agent's normal mechanism for loading local skills, project instructions, or reusable tool folders.

# card-arena

Unofficial public research scaffold for a Pokemon Trading Card Game AI battle agent.

This repository is designed for competition-style development: clean adapter boundaries, reproducible evaluation, simple baselines, and a staged path toward search/RL/hybrid agents.

## Status

- `TODO(rule-dependent)`: integrate the official competition starter kit or engine API.
- Current code uses a toy local state/action interface for smoke tests and baseline development.
- No official Pokemon assets, card images, proprietary card text database, or private contest data are included.

## Repository structure

```text
src/ptcg_ai_agent/
  actions.py          typed local action model
  state.py            toy/public-safe state model and feature encoder
  agent.py            random and heuristic baseline agents
  match_runner.py     deterministic toy match runner for smoke tests
  adapters/           official starter-kit integration goes here
  training/           self-play/RL placeholders
  evaluation/         baseline league and reports
configs/              experiment configs
docs/                 architecture, strategy, rules integration notes
scripts/              hygiene and utility scripts
tests/                unit and smoke tests
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m ptcg_ai_agent.match_runner --games 10 --seed 7
python scripts/check_public_hygiene.py
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
python -m ptcg_ai_agent.match_runner --games 10 --seed 7
python scripts/check_public_hygiene.py
```

## Development roadmap

1. **valid action loop**: integrate official observation/action API and ensure invalid action rate is zero.
2. **baseline league**: compare random legal vs heuristic vs previous checkpoint.
3. **search agent**: add shallow tactical search with time-budget fallback.
4. **self-play data**: store transitions and evaluate reward shaping.
5. **policy/value model**: train only after simulator throughput and metrics are reliable.
6. **submission hardening**: profile latency, freeze dependencies, document exact reproduction steps.

## Public repo policy

This repo intentionally avoids restricted assets. Add official starter kit files only if the contest license allows redistribution. Otherwise, document installation steps and keep local-only files out of git.

## Disclaimer

This is an unofficial research and competition engineering project. It is not affiliated with, sponsored by, or endorsed by The Pokemon Company, Nintendo, Creatures, Game Freak, or any official Pokemon Trading Card Game entity. Pokemon and related marks are trademarks of their respective owners.

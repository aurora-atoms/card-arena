# Competition Strategy

## Practical main path

1. Make every action legal.
2. Build deterministic evaluation.
3. Beat random legal baseline with transparent heuristics.
4. Add tactical search for knockout/prize-race turns.
5. Add learning only when the simulator is fast and metrics are reliable.

## Initial metrics

- invalid action rate: target 0%.
- timeout/crash rate: target 0%.
- average decision latency: track from first integration.
- p95 decision latency: track before adding search/model inference.
- win rate vs random and heuristic baselines.
- regression delta vs previous best commit.

## Current baseline command

```bash
python -m ptcg_ai_agent.evaluation.league --games 50 --seed 7
```

The current league is a toy smoke test. Replace the runner behind this command after the
official adapter can parse observations, enumerate legal actions, and serialize responses.

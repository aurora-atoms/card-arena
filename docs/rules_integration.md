# Rules Integration Notes

TODO(rule-dependent): fill this after reading the official competition rules and starter kit license.

## Current adapter assumptions

The public smoke path uses a synthetic cabt-shaped fixture, not official starter-kit files.
It assumes observations contain `logs`, `current`, and `select`, with active choices
represented as option-index selections. The adapter preserves raw option indices,
selection context, and min/max selection bounds in `Action.metadata` before returning
a serialized payload such as `[0]`.

Setup and deck-initialization observations remain `TODO(rule-dependent)` until the
official submission package and starter-kit rules are verified.

## Questions to answer

- What observation format is provided?
- Who generates legal actions: official engine, local simulator, or agent?
- What are the decision time limits?
- Are external model calls allowed during matches?
- Are pretrained models allowed?
- Are official starter-kit files redistributable in a public repo?
- What is the submission format?
- `needs-kaggle-recheck`: exact runtime/package constraints.
- `needs-kaggle-recheck`: rating and active-submission mechanics.
- `needs-kaggle-recheck`: data-license and redistribution obligations.
- `needs-kaggle-recheck`: forum-reported simulator or memory issues.

## First integration milestone

1. Implement `OfficialAdapter.parse_observation`.
2. Implement `OfficialAdapter.parse_legal_actions` from the authoritative legal-action source.
3. Implement `OfficialAdapter.serialize_action`.
4. Add a license-safe smoke fixture or local-only fixture instructions.
5. Run `python -m ptcg_ai_agent.evaluation.league --games 50 --seed 7` after swapping in the official adapter path.

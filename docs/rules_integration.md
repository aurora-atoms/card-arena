# Rules Integration Notes

TODO(rule-dependent): fill this after reading the official competition rules and starter kit license.

## Questions to answer

- What observation format is provided?
- Who generates legal actions: official engine, local simulator, or agent?
- What are the decision time limits?
- Are external model calls allowed during matches?
- Are pretrained models allowed?
- Are official starter-kit files redistributable in a public repo?
- What is the submission format?

## First integration milestone

1. Implement `OfficialAdapter.parse_observation`.
2. Implement `OfficialAdapter.parse_legal_actions` from the authoritative legal-action source.
3. Implement `OfficialAdapter.serialize_action`.
4. Add a license-safe smoke fixture or local-only fixture instructions.
5. Run `python -m ptcg_ai_agent.evaluation.league --games 50 --seed 7` after swapping in the official adapter path.

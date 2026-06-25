# Architecture

The project uses a stable local agent interface and isolates official competition dependencies in `adapters/`.

## Design principle

Agent logic should not know whether the observation came from a local simulator, official starter kit, replay log, or future server runtime.

## Target pipeline

```text
official observation -> adapter -> GameState + legal Action list -> agent -> Action -> adapter -> official payload
```

Official or cabt SDK imports belong only in `adapters/`. Core modules such as
state, actions, agents, evaluation, and training consume local `GameState` and
`Action` objects only.

## Expansion plan

- add official adapter tests using sample observations if the license permits committing them.
- add feature extraction and heuristic scoring logs.
- add MCTS/search under a strict time budget.
- add self-play only after deterministic evaluation is stable.

## Adapter acceptance criteria

- core modules do not import official SDK types.
- adapters expose local `GameState` objects and legal `Action` lists.
- cabt-shaped observations preserve `logs`, `current`, `select`, raw option indices, selection context, and min/max selection bounds at the adapter boundary.
- every selected action is checked against the legal action list before serialization.
- smoke tests record invalid-action rate and decision latency.

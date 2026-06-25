from __future__ import annotations

import argparse
import json

from ptcg_ai_agent.match_runner import run_toy_game, summarize_results


def run_baseline_league(games: int, seed: int) -> dict[str, object]:
    """Run the deterministic toy league until the official adapter is available."""

    results = [run_toy_game(seed + i) for i in range(games)]
    summary = summarize_results(results)
    summary["league"] = "toy-baseline"
    summary["seed"] = seed
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=50)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    print(json.dumps(run_baseline_league(args.games, args.seed), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

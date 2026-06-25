from __future__ import annotations

import argparse
import random
from collections import Counter
from dataclasses import dataclass
from time import perf_counter
from typing import Sequence

from ptcg_ai_agent.actions import Action, ActionType, require_legal_action
from ptcg_ai_agent.agent import Agent, HeuristicAgent, RandomLegalAgent
from ptcg_ai_agent.state import GameState, PlayerPublicState


@dataclass(frozen=True, slots=True)
class DecisionRecord:
    agent_name: str
    action_type: str
    action_label: str
    latency_ms: float
    invalid_action: bool = False


@dataclass(frozen=True, slots=True)
class ToyGameResult:
    winner: str
    decisions: tuple[DecisionRecord, ...]

    @property
    def invalid_action_count(self) -> int:
        return sum(decision.invalid_action for decision in self.decisions)

    @property
    def average_latency_ms(self) -> float:
        if not self.decisions:
            return 0.0
        return sum(decision.latency_ms for decision in self.decisions) / len(self.decisions)


def toy_legal_actions() -> list[Action]:
    return [
        Action.pass_turn(),
        Action(ActionType.PLAY_CARD, "play setup card", source_id="toy-setup"),
        Action(ActionType.ATTACH_RESOURCE, "attach energy/resource", source_id="toy-energy"),
        Action(ActionType.ATTACK, "main attack", source_id="toy-attack"),
        Action(ActionType.RETREAT, "retreat damaged active", cost=1.0),
    ]


def initial_state(seed: int) -> GameState:
    rng = random.Random(seed)
    return GameState(
        turn=1,
        current_player=0,
        players=(
            PlayerPublicState(active_hp=rng.choice([80, 100, 120]), hand_count=7),
            PlayerPublicState(active_hp=rng.choice([80, 100, 120]), hand_count=7),
        ),
        remaining_time_ms=25_000,
    )


def select_with_record(
    agent: Agent,
    state: GameState,
    legal_actions: Sequence[Action],
) -> tuple[Action, DecisionRecord]:
    start = perf_counter()
    action = agent.select_action(state, legal_actions)
    latency_ms = (perf_counter() - start) * 1000
    try:
        require_legal_action(action, legal_actions)
        invalid = False
    except ValueError:
        invalid = True
        action = Action.pass_turn()
    return action, DecisionRecord(
        agent_name=agent.name,
        action_type=action.action_type.value,
        action_label=action.label,
        latency_ms=latency_ms,
        invalid_action=invalid,
    )


def run_toy_game(seed: int) -> ToyGameResult:
    random_agent: Agent = RandomLegalAgent(seed=seed)
    heuristic_agent: Agent = HeuristicAgent()
    state = initial_state(seed)
    actions = toy_legal_actions()
    # Smoke-test style: compare first-decision quality, not real PTCG rules.
    a0, d0 = select_with_record(heuristic_agent, state, actions)
    a1, d1 = select_with_record(random_agent, state, actions)
    if a0.action_type == ActionType.ATTACK and a1.action_type != ActionType.ATTACK:
        return ToyGameResult(heuristic_agent.name, (d0, d1))
    if a1.action_type == ActionType.ATTACK and a0.action_type != ActionType.ATTACK:
        return ToyGameResult(random_agent.name, (d0, d1))
    return ToyGameResult("draw", (d0, d1))


def summarize_results(results: Sequence[ToyGameResult]) -> dict[str, object]:
    winners = Counter(result.winner for result in results)
    decisions = [decision for result in results for decision in result.decisions]
    latencies = sorted(decision.latency_ms for decision in decisions)
    p95_index = int((len(latencies) - 1) * 0.95) if latencies else 0
    return {
        "games": len(results),
        "winners": dict(winners),
        "invalid_action_rate": (
            sum(decision.invalid_action for decision in decisions) / len(decisions)
            if decisions
            else 0.0
        ),
        "average_decision_latency_ms": (
            sum(decision.latency_ms for decision in decisions) / len(decisions) if decisions else 0.0
        ),
        "p95_decision_latency_ms": latencies[p95_index] if latencies else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    results = [run_toy_game(args.seed + i) for i in range(args.games)]
    print(summarize_results(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

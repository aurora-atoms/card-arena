from __future__ import annotations

import argparse
import random
from collections import Counter

from ptcg_ai_agent.actions import Action, ActionType
from ptcg_ai_agent.agent import HeuristicAgent, RandomLegalAgent
from ptcg_ai_agent.state import GameState, PlayerPublicState


def toy_legal_actions() -> list[Action]:
    return [
        Action.pass_turn(),
        Action(ActionType.PLAY_CARD, "play setup card"),
        Action(ActionType.ATTACH_RESOURCE, "attach energy/resource"),
        Action(ActionType.ATTACK, "main attack"),
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
    )


def run_toy_game(seed: int) -> str:
    random_agent = RandomLegalAgent(seed=seed)
    heuristic_agent = HeuristicAgent()
    state = initial_state(seed)
    actions = toy_legal_actions()
    # Smoke-test style: compare first-decision quality, not real PTCG rules.
    a0 = heuristic_agent.select_action(state, actions)
    a1 = random_agent.select_action(state, actions)
    if a0.action_type == ActionType.ATTACK and a1.action_type != ActionType.ATTACK:
        return heuristic_agent.name
    if a1.action_type == ActionType.ATTACK and a0.action_type != ActionType.ATTACK:
        return random_agent.name
    return "draw"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    results = Counter(run_toy_game(args.seed + i) for i in range(args.games))
    print(dict(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

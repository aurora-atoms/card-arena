from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Protocol, Sequence

from ptcg_ai_agent.actions import Action, ActionType
from ptcg_ai_agent.state import GameState


class Agent(Protocol):
    name: str

    def select_action(self, state: GameState, legal_actions: Sequence[Action]) -> Action:
        """Return one legal action for the current state."""


@dataclass(slots=True)
class RandomLegalAgent:
    name: str = "random-legal"
    seed: int | None = None
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def select_action(self, state: GameState, legal_actions: Sequence[Action]) -> Action:
        if not legal_actions:
            raise ValueError("legal_actions must not be empty")
        return self._rng.choice(list(legal_actions))


@dataclass(slots=True)
class HeuristicAgent:
    """Transparent baseline.

    This intentionally stays simple. Extend scoring after official observations are integrated.
    """

    name: str = "heuristic-v0"

    def select_action(self, state: GameState, legal_actions: Sequence[Action]) -> Action:
        if not legal_actions:
            raise ValueError("legal_actions must not be empty")
        return max(legal_actions, key=lambda action: self.score_action(state, action))

    def score_action(self, state: GameState, action: Action) -> float:
        cur = state.current()
        opp = state.opponent()
        score = 0.0
        if action.action_type == ActionType.ATTACK:
            score += 10.0
            score += max(0, 120 - opp.active_hp) / 20.0
        if action.action_type == ActionType.PLAY_CARD:
            score += 3.0
        if action.action_type == ActionType.ATTACH_RESOURCE:
            score += 2.0 if cur.energy_attached < 3 else 0.5
        if action.action_type == ActionType.PASS:
            score -= 5.0
        score += (opp.prizes_remaining - cur.prizes_remaining) * 0.2
        return score

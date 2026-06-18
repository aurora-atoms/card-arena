from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True, slots=True)
class PlayerPublicState:
    prizes_remaining: int = 6
    active_hp: int = 100
    bench_count: int = 0
    hand_count: int = 7
    discard_count: int = 0
    energy_attached: int = 0


@dataclass(frozen=True, slots=True)
class GameState:
    """Public-safe toy state.

    Replace or extend through adapters once official competition observations are available.
    """

    turn: int
    current_player: int
    players: tuple[PlayerPublicState, PlayerPublicState]
    tags: dict[str, str] = field(default_factory=dict)

    def current(self) -> PlayerPublicState:
        return self.players[self.current_player]

    def opponent(self) -> PlayerPublicState:
        return self.players[1 - self.current_player]


class StateEncoder:
    """Small numeric encoder for heuristic/search/model prototypes."""

    def encode(self, state: GameState) -> np.ndarray:
        cur = state.current()
        opp = state.opponent()
        return np.array(
            [
                state.turn,
                cur.prizes_remaining,
                opp.prizes_remaining,
                cur.active_hp,
                opp.active_hp,
                cur.bench_count,
                opp.bench_count,
                cur.hand_count,
                opp.hand_count,
                cur.energy_attached,
                opp.energy_attached,
            ],
            dtype=np.float32,
        )

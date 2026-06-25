from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PlayerPublicState:
    prizes_remaining: int = 6
    active_hp: int = 100
    active_max_hp: int = 100
    bench_count: int = 0
    hand_count: int = 7
    discard_count: int = 0
    energy_attached: int = 0
    deck_count: int = 40
    known_cards_in_hand: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GameState:
    """Public-safe toy state.

    Replace or extend through adapters once official competition observations are available.
    """

    turn: int
    current_player: int
    players: tuple[PlayerPublicState, PlayerPublicState]
    phase: str = "main"
    remaining_time_ms: int | None = None
    tags: dict[str, str] = field(default_factory=dict)

    def current(self) -> PlayerPublicState:
        return self.players[self.current_player]

    def opponent(self) -> PlayerPublicState:
        return self.players[1 - self.current_player]


class StateEncoder:
    """Small numeric encoder for heuristic/search/model prototypes."""

    def encode(self, state: GameState) -> tuple[float, ...]:
        cur = state.current()
        opp = state.opponent()
        return (
            float(state.turn),
            float(cur.prizes_remaining),
            float(opp.prizes_remaining),
            float(cur.active_hp),
            float(opp.active_hp),
            float(cur.active_max_hp),
            float(opp.active_max_hp),
            float(cur.bench_count),
            float(opp.bench_count),
            float(cur.hand_count),
            float(opp.hand_count),
            float(cur.energy_attached),
            float(opp.energy_attached),
            float(cur.deck_count),
            float(opp.deck_count),
            float(0 if state.remaining_time_ms is None else state.remaining_time_ms),
        )

from __future__ import annotations

from collections.abc import Sequence as SequenceABC
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Sequence

from ptcg_ai_agent.actions import Action, ActionType, require_legal_action
from ptcg_ai_agent.state import GameState, PlayerPublicState


@dataclass(frozen=True, slots=True)
class AdapterSmokeResult:
    """Result from one fixture-safe adapter smoke path."""

    state: GameState
    action: Action
    payload: list[int]
    metrics: dict[str, object]


class OfficialAdapter:
    """Fixture-safe adapter for cabt-shaped observations.

    Keep this boundary thin. The rest of the agent should not import official SDK objects directly.
    """

    def parse_observation(self, raw_observation: Any) -> GameState:
        raw = _require_mapping(raw_observation, "raw_observation")
        logs = raw.get("logs", ())
        current = raw.get("current")
        if current is None:
            raise NotImplementedError(
                "TODO(rule-dependent): deck initialization observations need official rules"
            )
        current = _require_mapping(current, "current")
        players = current.get("players")
        if not isinstance(players, SequenceABC) or isinstance(players, (str, bytes)) or len(players) != 2:
            raise ValueError("current.players must contain exactly two player states")

        current_player = int(current.get("player", current.get("current_player", 0)))
        if current_player not in (0, 1):
            raise ValueError("current player must be 0 or 1")
        parsed_players: tuple[PlayerPublicState, PlayerPublicState] = (
            self._parse_player(players[0], is_current=current_player == 0),
            self._parse_player(players[1], is_current=current_player == 1),
        )
        return GameState(
            turn=int(current.get("turn", 0)),
            current_player=current_player,
            players=parsed_players,
            phase=str(current.get("phase", "main")),
            remaining_time_ms=_optional_int(
                current.get("remainingTimeMs", current.get("remaining_time_ms"))
            ),
            tags={
                "source": "cabt-shaped",
                "log_count": str(_zone_count(logs)),
                "select_context": _select_context(raw.get("select")),
            },
        )

    def parse_legal_actions(self, raw_observation: Any) -> Sequence[Action]:
        raw = _require_mapping(raw_observation, "raw_observation")
        if raw.get("current") is None:
            raise NotImplementedError(
                "TODO(rule-dependent): deck initialization action payload requires official rules"
            )
        select = raw.get("select")
        if not select:
            raise NotImplementedError(
                "TODO(rule-dependent): observation has no active select options to serialize"
            )
        select = _require_mapping(select, "select")
        options = _option_list(select)
        min_count = int(select.get("minCount", select.get("min_count", 1)))
        max_count = int(select.get("maxCount", select.get("max_count", 1)))

        actions: list[Action] = []
        for fallback_index, option in enumerate(options):
            option_map = _require_mapping(option, "select option")
            option_index = int(option_map.get("index", option_map.get("optionIndex", fallback_index)))
            action_type = _action_type(option_map)
            label = str(option_map.get("label", option_map.get("text", f"option {option_index}")))
            actions.append(
                Action(
                    action_type,
                    label,
                    source_id=f"cabt-option-{option_index}",
                    cost=float(option_map.get("cost", 0.0)),
                    metadata={
                        "option_index": option_index,
                        "select_context": select.get("context", select.get("name", "default")),
                        "min_count": min_count,
                        "max_count": max_count,
                        "option_count": len(options),
                        "raw_option": option_map,
                    },
                )
            )
        return actions

    def serialize_action(self, action: Action) -> list[int]:
        option_index = action.metadata.get("option_index")
        if not isinstance(option_index, int):
            raise ValueError("cannot serialize action without integer metadata['option_index']")

        payload = [option_index]
        min_count = int(action.metadata.get("min_count", 1))
        max_count = int(action.metadata.get("max_count", 1))
        if not min_count <= len(payload) <= max_count:
            raise ValueError(
                f"serialized action length {len(payload)} violates select bounds "
                f"{min_count}..{max_count}"
            )

        option_count = action.metadata.get("option_count")
        if isinstance(option_count, int) and not 0 <= option_index < option_count:
            raise ValueError(f"option index {option_index} outside option count {option_count}")
        return payload

    def smoke_check(self, raw_observation: Any) -> AdapterSmokeResult:
        """Parse one observation, serialize one legal action, and report smoke metrics."""

        crash = False
        timeout = False
        invalid_action_count = 0
        warnings: list[str] = []
        start = perf_counter()
        state = self.parse_observation(raw_observation)
        legal_actions = list(self.parse_legal_actions(raw_observation))
        if not legal_actions:
            raise ValueError("official adapter produced no legal actions")
        action = legal_actions[0]
        try:
            require_legal_action(action, legal_actions)
        except ValueError:
            invalid_action_count = 1
        payload = self.serialize_action(action)
        latency_ms = (perf_counter() - start) * 1000
        metrics: dict[str, object] = {
            "invalid_action_count": invalid_action_count,
            "invalid_action_rate": invalid_action_count / 1,
            "average_decision_latency_ms": latency_ms,
            "p95_decision_latency_ms": latency_ms,
            "crash": crash,
            "timeout": timeout,
            "warnings": warnings,
        }
        return AdapterSmokeResult(state=state, action=action, payload=payload, metrics=metrics)

    def _parse_player(self, raw_player: Any, *, is_current: bool) -> PlayerPublicState:
        player = _require_mapping(raw_player, "player")
        raw_active = player.get("active")
        active: dict[str, Any] = raw_active if isinstance(raw_active, dict) else {}
        hand = player.get("hand", player.get("handCount", player.get("hand_count", 0)))
        prizes = player.get("prizes", player.get("prizeCards", player.get("prizes_remaining", 6)))
        return PlayerPublicState(
            prizes_remaining=_zone_count(prizes),
            active_hp=int(active.get("hp", player.get("active_hp", 0))),
            active_max_hp=int(active.get("maxHp", active.get("max_hp", player.get("active_max_hp", 0)))),
            bench_count=_zone_count(player.get("bench", player.get("benchCount", 0))),
            hand_count=_zone_count(hand),
            discard_count=_zone_count(player.get("discard", player.get("discardCount", 0))),
            energy_attached=int(
                player.get("energyAttached", player.get("energy_attached", active.get("energy", 0)))
            ),
            deck_count=int(player.get("deckCount", player.get("deck_count", 0))),
            known_cards_in_hand=_known_cards(hand) if is_current else (),
        )


def _require_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a mapping")
    return value


def _optional_int(value: Any) -> int | None:
    return None if value is None else int(value)


def _zone_count(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, dict) and "count" in value:
        return int(value["count"])
    if isinstance(value, SequenceABC) and not isinstance(value, (str, bytes)):
        return len(value)
    return int(value)


def _known_cards(value: Any) -> tuple[str, ...]:
    if not isinstance(value, SequenceABC) or isinstance(value, (str, bytes)):
        return ()
    known: list[str] = []
    for card in value:
        if isinstance(card, dict):
            identifier = card.get("id", card.get("name"))
            if identifier is not None:
                known.append(str(identifier))
        elif card is not None:
            known.append(str(card))
    return tuple(known)


def _option_list(select: dict[str, Any]) -> Sequence[Any]:
    options = select.get("options", select.get("option", select.get("option1")))
    if not isinstance(options, SequenceABC) or isinstance(options, (str, bytes)) or not options:
        raise NotImplementedError(
            "TODO(rule-dependent): active select options are required for action serialization"
        )
    return options


def _select_context(select: Any) -> str:
    if not isinstance(select, dict):
        return "none"
    return str(select.get("context", select.get("name", "default")))


def _action_type(option: dict[str, Any]) -> ActionType:
    raw_type = str(option.get("type", option.get("kind", ""))).lower()
    label = str(option.get("label", option.get("text", ""))).lower()
    combined = f"{raw_type} {label}"
    if "attack" in combined:
        return ActionType.ATTACK
    if "retreat" in combined:
        return ActionType.RETREAT
    if "ability" in combined:
        return ActionType.ACTIVATE_ABILITY
    if "attach" in combined or "energy" in combined:
        return ActionType.ATTACH_RESOURCE
    if "order" in combined:
        return ActionType.ORDER_CARDS
    if "target" in combined or "choose" in combined:
        return ActionType.CHOOSE_TARGET
    if "pass" in combined:
        return ActionType.PASS
    return ActionType.PLAY_CARD

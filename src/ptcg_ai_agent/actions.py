from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Sequence


class ActionType(str, Enum):
    PASS = "pass"
    PLAY_CARD = "play_card"
    ATTACK = "attack"
    ATTACH_RESOURCE = "attach_resource"
    ACTIVATE_ABILITY = "activate_ability"
    RETREAT = "retreat"
    CHOOSE_TARGET = "choose_target"
    ORDER_CARDS = "order_cards"


@dataclass(frozen=True, slots=True)
class Action:
    """Local action object.

    Keep official engine payloads in metadata. Agent logic should reason over typed fields.
    """

    action_type: ActionType
    label: str
    source_id: str | None = None
    targets: tuple[str, ...] = ()
    cost: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def pass_turn() -> "Action":
        return Action(ActionType.PASS, "pass")


def require_legal_action(action: Action, legal_actions: Sequence[Action]) -> Action:
    """Return action if legal, otherwise raise with enough context for debugging."""

    if action in legal_actions:
        return action
    labels = ", ".join(candidate.label for candidate in legal_actions) or "<none>"
    raise ValueError(f"agent selected illegal action {action.label!r}; legal actions: {labels}")

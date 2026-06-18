from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ActionType(StrEnum):
    PASS = "pass"
    PLAY_CARD = "play_card"
    ATTACK = "attack"
    ATTACH_RESOURCE = "attach_resource"
    ACTIVATE_ABILITY = "activate_ability"
    RETREAT = "retreat"
    CHOOSE_TARGET = "choose_target"


@dataclass(frozen=True, slots=True)
class Action:
    """Local action object.

    Keep official engine payloads in metadata. Agent logic should reason over typed fields.
    """

    action_type: ActionType
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def pass_turn() -> "Action":
        return Action(ActionType.PASS, "pass")

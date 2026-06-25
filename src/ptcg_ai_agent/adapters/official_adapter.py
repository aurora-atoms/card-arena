from __future__ import annotations

from typing import Any, Sequence

from ptcg_ai_agent.actions import Action
from ptcg_ai_agent.state import GameState


class OfficialAdapter:
    """Placeholder for official competition API integration.

    Keep this boundary thin. The rest of the agent should not import official SDK objects directly.
    """

    def parse_observation(self, raw_observation: Any) -> GameState:
        raise NotImplementedError("TODO(rule-dependent): map official observation to GameState")

    def parse_legal_actions(self, raw_observation: Any) -> Sequence[Action]:
        raise NotImplementedError("TODO(rule-dependent): map official legal actions to Action objects")

    def serialize_action(self, action: Action) -> Any:
        raise NotImplementedError("TODO(rule-dependent): map local Action to official payload")

    def smoke_check(self, raw_observation: Any) -> Action:
        """Parse one observation and return a legal action for integration tests."""

        self.parse_observation(raw_observation)
        legal_actions = list(self.parse_legal_actions(raw_observation))
        if not legal_actions:
            raise ValueError("official adapter produced no legal actions")
        return legal_actions[0]

import pytest

from ptcg_ai_agent.actions import Action, ActionType
from ptcg_ai_agent.adapters.official_adapter import OfficialAdapter


def synthetic_cabt_observation() -> dict[str, object]:
    return {
        "logs": [{"turn": 3, "message": "synthetic public fixture"}],
        "current": {
            "turn": 3,
            "player": 0,
            "phase": "main",
            "remainingTimeMs": 590_000,
            "players": [
                {
                    "active": {"hp": 80, "maxHp": 100, "energy": 2},
                    "bench": [{"slot": 0}, {"slot": 1}],
                    "hand": [{"id": "synthetic-known-a"}, {"id": "synthetic-known-b"}],
                    "discard": [{"id": "synthetic-discard"}],
                    "deckCount": 38,
                    "prizes": [None, None, None, None, None, None],
                },
                {
                    "active": {"hp": 120, "maxHp": 120, "energy": 1},
                    "bench": [{"slot": 0}],
                    "hand": {"count": 5},
                    "discard": [],
                    "deckCount": 41,
                    "prizes": [None, None, None, None],
                },
            ],
        },
        "select": {
            "context": "main-action",
            "minCount": 1,
            "maxCount": 1,
            "options": [
                {"index": 0, "type": "attack", "label": "synthetic attack"},
                {"index": 1, "type": "retreat", "label": "synthetic retreat", "cost": 1.0},
            ],
        },
    }


def test_parse_cabt_observation_to_public_game_state() -> None:
    state = OfficialAdapter().parse_observation(synthetic_cabt_observation())

    assert state.turn == 3
    assert state.current_player == 0
    assert state.phase == "main"
    assert state.remaining_time_ms == 590_000
    assert state.tags["log_count"] == "1"
    assert state.tags["select_context"] == "main-action"
    assert state.current().hand_count == 2
    assert state.current().known_cards_in_hand == ("synthetic-known-a", "synthetic-known-b")
    assert state.opponent().hand_count == 5
    assert state.opponent().known_cards_in_hand == ()
    assert state.opponent().prizes_remaining == 4


def test_parse_legal_actions_preserves_cabt_selection_metadata() -> None:
    actions = list(OfficialAdapter().parse_legal_actions(synthetic_cabt_observation()))

    assert [action.action_type for action in actions] == [ActionType.ATTACK, ActionType.RETREAT]
    assert actions[0].metadata["option_index"] == 0
    assert actions[0].metadata["select_context"] == "main-action"
    assert actions[0].metadata["min_count"] == 1
    assert actions[0].metadata["max_count"] == 1
    assert actions[0].metadata["raw_option"]["label"] == "synthetic attack"


def test_serialize_action_returns_option_index_payload() -> None:
    adapter = OfficialAdapter()
    action = list(adapter.parse_legal_actions(synthetic_cabt_observation()))[1]

    assert adapter.serialize_action(action) == [1]


def test_serialize_action_rejects_missing_option_index() -> None:
    with pytest.raises(ValueError, match="option_index"):
        OfficialAdapter().serialize_action(Action(ActionType.ATTACK, "missing option"))


def test_serialize_action_rejects_selection_bounds_violation() -> None:
    action = Action(
        ActionType.ATTACK,
        "out of bounds",
        metadata={"option_index": 0, "min_count": 2, "max_count": 2, "option_count": 1},
    )

    with pytest.raises(ValueError, match="violates select bounds"):
        OfficialAdapter().serialize_action(action)


def test_setup_observation_stays_rule_dependent() -> None:
    observation = {"current": None, "select": None}

    with pytest.raises(NotImplementedError, match="TODO\\(rule-dependent\\)"):
        OfficialAdapter().parse_observation(observation)


def test_parse_observation_rejects_unknown_current_player() -> None:
    observation = synthetic_cabt_observation()
    current = observation["current"]
    assert isinstance(current, dict)
    current["player"] = 2

    with pytest.raises(ValueError, match="current player"):
        OfficialAdapter().parse_observation(observation)


def test_smoke_check_returns_payload_and_zero_invalid_actions() -> None:
    result = OfficialAdapter().smoke_check(synthetic_cabt_observation())

    assert result.payload == [0]
    assert result.action.action_type == ActionType.ATTACK
    assert result.metrics["invalid_action_count"] == 0
    assert result.metrics["invalid_action_rate"] == 0.0
    assert result.metrics["crash"] is False
    assert result.metrics["timeout"] is False
    assert "average_decision_latency_ms" in result.metrics
    assert "p95_decision_latency_ms" in result.metrics

from ptcg_ai_agent.actions import Action, ActionType
from ptcg_ai_agent.agent import HeuristicAgent, RandomLegalAgent
from ptcg_ai_agent.evaluation.league import run_baseline_league
from ptcg_ai_agent.match_runner import run_toy_game, summarize_results
from ptcg_ai_agent.state import GameState, PlayerPublicState


def test_random_agent_returns_legal_action() -> None:
    agent = RandomLegalAgent(seed=1)
    legal = [Action.pass_turn(), Action(ActionType.ATTACK, "attack")]
    state = GameState(1, 0, (PlayerPublicState(), PlayerPublicState()))
    assert agent.select_action(state, legal) in legal


def test_heuristic_prefers_attack_over_pass() -> None:
    agent = HeuristicAgent()
    legal = [Action.pass_turn(), Action(ActionType.ATTACK, "attack")]
    state = GameState(1, 0, (PlayerPublicState(), PlayerPublicState()))
    assert agent.select_action(state, legal).action_type == ActionType.ATTACK


def test_toy_game_reports_no_invalid_actions() -> None:
    result = run_toy_game(seed=7)
    assert result.invalid_action_count == 0
    assert result.average_latency_ms >= 0


def test_summary_tracks_required_baseline_metrics() -> None:
    results = [run_toy_game(seed=i) for i in range(5)]
    summary = summarize_results(results)
    assert summary["games"] == 5
    assert summary["invalid_action_rate"] == 0
    assert "average_decision_latency_ms" in summary
    assert "p95_decision_latency_ms" in summary


def test_baseline_league_is_deterministic() -> None:
    first = run_baseline_league(games=10, seed=3)
    second = run_baseline_league(games=10, seed=3)
    assert first["winners"] == second["winners"]
    assert first["invalid_action_rate"] == second["invalid_action_rate"]

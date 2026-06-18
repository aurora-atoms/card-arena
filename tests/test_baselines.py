from ptcg_ai_agent.actions import Action, ActionType
from ptcg_ai_agent.agent import HeuristicAgent, RandomLegalAgent
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

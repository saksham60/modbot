from modbot.env.core.environment import ModBotEnv
from modbot.env.models.action import ActionModel
from modbot.env.models.config import ActionType


def test_invalid_action_is_penalized() -> None:
    env = ModBotEnv(task_id="easy", seed=7)
    env.reset()
    _, reward, done, info = env.step(
        ActionModel(action_type=ActionType.FETCH_USER_HISTORY, user_id="user-alpha")
    )

    assert not done
    assert info.valid_action is False
    assert reward < 0
    assert info.reward_breakdown["invalid_action"] < 0


def test_relevant_context_fetch_scores_better_than_irrelevant_fetch() -> None:
    env_relevant = ModBotEnv(task_id="medium", seed=7)
    env_relevant.reset()
    env_relevant.step(ActionModel(action_type=ActionType.REVIEW_REPORT, report_id="medium-001"))
    _, relevant_reward, _, relevant_info = env_relevant.step(
        ActionModel(action_type=ActionType.FETCH_THREAD_CONTEXT, report_id="medium-001")
    )

    env_irrelevant = ModBotEnv(task_id="medium", seed=7)
    env_irrelevant.reset()
    env_irrelevant.step(ActionModel(action_type=ActionType.REVIEW_REPORT, report_id="medium-001"))
    _, irrelevant_reward, _, irrelevant_info = env_irrelevant.step(
        ActionModel(action_type=ActionType.FETCH_USER_HISTORY, user_id="user-echo")
    )

    assert relevant_info.reward_breakdown["relevant_context"] > irrelevant_info.reward_breakdown["relevant_context"]
    assert relevant_reward > irrelevant_reward

from modbot.env.core.environment import ModBotEnv
from modbot.env.models.action import ActionModel
from modbot.env.models.config import ActionType


def test_reset_returns_expected_easy_observation() -> None:
    env = ModBotEnv(task_id="easy", seed=7)
    observation = env.reset()

    assert observation.task_id == "easy"
    assert observation.step == 0
    assert observation.current_report is None
    assert observation.remaining_review_budget == 12
    assert observation.allowed_actions == [ActionType.REVIEW_REPORT]
    assert len(observation.queue_snapshot) == 4


def test_review_remove_complete_transitions_case_state() -> None:
    env = ModBotEnv(task_id="easy", seed=7)
    observation = env.reset()

    target_report_id = observation.queue_snapshot[0].report_id
    observation, _, done, _ = env.step(ActionModel(action_type=ActionType.REVIEW_REPORT, report_id=target_report_id))
    assert not done
    assert observation.current_report is not None
    assert observation.current_report.report_id == target_report_id

    observation, _, _, _ = env.step(ActionModel(action_type=ActionType.REMOVE_CONTENT, report_id=target_report_id))
    assert observation.active_decision == ActionType.REMOVE_CONTENT

    observation, _, done, _ = env.step(ActionModel(action_type=ActionType.COMPLETE_CASE, report_id=target_report_id))
    state = env.state()
    assert not done
    assert state.active_report_id is None
    assert target_report_id not in state.queue
    completed = {report.report_id: report for report in state.reports}
    assert completed[target_report_id].status.value == "completed"

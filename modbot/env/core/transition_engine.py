"""Transition engine for applying actions to hidden state."""

from modbot.env.actions.executor import ActionExecutionResult, execute_action
from modbot.env.actions.validator import validate_action
from modbot.env.models.action import ActionModel
from modbot.env.models.info import StepInfoModel
from modbot.env.models.state import TrajectoryEntryModel
from modbot.env.state.trust_manager import recompute_backlog_pressure
from modbot.env.state.queue_manager import completed_case_count, pending_case_count


class TransitionEngine:
    """Coordinate validation, execution, reward shaping, and grading."""

    def __init__(self, observation_builder, reward_engine, episode_manager, grader_factory) -> None:
        self.observation_builder = observation_builder
        self.reward_engine = reward_engine
        self.episode_manager = episode_manager
        self.grader_factory = grader_factory

    def step(self, state, action: ActionModel):
        """Advance the environment by one agent action."""

        validation = validate_action(state, action)
        if validation.is_valid:
            outcome = execute_action(state, action, validation)
        else:
            if state.active_report_id and state.active_report_id in state.runtime_reports:
                state.runtime_reports[state.active_report_id].invalid_attempts += 1
            elif action.report_id and action.report_id in state.runtime_reports:
                state.runtime_reports[action.report_id].invalid_attempts += 1
            outcome = ActionExecutionResult(message=validation.message)

        state.step_count += 1
        recompute_backlog_pressure(state)
        reward, breakdown = self.reward_engine.compute(state, validation.is_valid, outcome)
        state.total_reward = round(state.total_reward + reward, 4)
        state.reward_history.append(dict(breakdown))
        state.trajectory.append(
            TrajectoryEntryModel(
                step=state.step_count,
                action_type=action.action_type,
                report_id=action.report_id,
                reward=reward,
                message=outcome.message,
            )
        )

        done_reason = self.episode_manager.evaluate_done(state)
        if done_reason is not None:
            state.done = True
            state.done_reason = done_reason
            final_score, grader_components = self.grader_factory.grade(state)
            state.final_score = final_score
            state.grader_components = grader_components

        observation = self.observation_builder.build(state)
        info = StepInfoModel(
            valid_action=validation.is_valid,
            message=outcome.message,
            reward=reward,
            reward_breakdown=breakdown,
            budget_spent=outcome.budget_spent,
            done_reason=state.done_reason,
            final_score=state.final_score,
            grader_components=dict(state.grader_components),
            state_summary={
                "pending_reports": pending_case_count(state),
                "completed_cases": completed_case_count(state),
                "active_report_id": state.active_report_id,
                "community_trust": state.community_trust,
                "appeal_pressure": state.appeal_pressure,
                "backlog_pressure": state.backlog_pressure,
                "remaining_review_budget": state.remaining_review_budget,
            },
        )
        return observation, reward, state.done, info

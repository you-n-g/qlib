from rdagent.scenarios.data_science.proposal.exp_gen.base import DSHypothesis, DSTrace
from rdagent.scenarios.data_science.proposal.exp_gen.proposal import DSProposalV2ExpGen
from rdagent.utils.agent.tpl import T

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Project specific settings."""

    problem_name: str | None = None
    problem_desc: str | None = None
    hypothesis_desc: str

    model_config = SettingsConfigDict(env_prefix="DS_EXP_GEN_",
                                      # extra="allow", # Does it allow extrasettings
                                     )


class CustomExpGen(DSProposalV2ExpGen):
    """
    Customize the experiment design.

    Currently, we customize the hypothesis generation.

    We don't directly run the task due to
    - one hypothesis may involves multiple loops to try;
        - We hope learn from previous failures and design better tasks based on the same hypothesis.
    """

    def gen(self, trace: DSTrace):
        custom_settings = Settings()

        # Retrieve SOTA experiment and feedback
        sota_exp_fb = trace.sota_experiment_fb()
        if sota_exp_fb is None:
            sota_exp, fb_to_sota_exp = None, None
        else:
            sota_exp, fb_to_sota_exp = sota_exp_fb

        # Build scenario description (attach EDA info if available)
        eda_output = None
        if sota_exp is not None:
            eda_output = sota_exp.experiment_workspace.file_dict.get("EDA.md", None)
        scenario_desc = self.scen.get_scenario_all_desc(eda_output=eda_output)

        # Describe the current best solution
        sota_exp_desc = T("scenarios.data_science.share:describe.exp").r(
            exp=sota_exp, heading="Best of previous exploration of the scenario")

        # Component description and failed trace description
        component_desc = T("scenarios.data_science.share:component_description_in_pipeline").r()

        failed_exp_feedback_list_desc = T("scenarios.data_science.share:describe.trace").r(
            exp_and_feedback_list=trace.experiment_and_feedback_list_after_init(return_type="failed"),
            type="failed",
            pipeline=True,
        )

        hypothesis = DSHypothesis(
            component="Pipeline",
            hypothesis=custom_settings.hypothesis_desc,
            problem_name=custom_settings.problem_name,
            problem_desc=custom_settings.problem_desc,
            problem_label="FEEDBACK_PROBLEM",
        )

        return self.task_gen(
            component_desc=component_desc,
            scenario_desc=scenario_desc,
            sota_exp_desc=sota_exp_desc,
            sota_exp=sota_exp,
            hypotheses=[hypothesis],
            pipeline=True,
            failed_exp_feedback_list_desc=failed_exp_feedback_list_desc,
            fb_to_sota_exp=fb_to_sota_exp,
        )

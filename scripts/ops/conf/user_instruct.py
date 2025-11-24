"""

After configuring the the time, we should start the experiment loop with the following command:

    script -c "LOG_TRACE_PATH=$LOG_TRACE_PATH mydotenv.sh python -m ipdb -c c  rdagent/app/data_science/loop.py --competition $m --path $LOG_TRACE_PATH --exp_gen_cls rdagent.scenarios.data_science.proposal.exp_gen.proposal.DSProposalV2ExpGen --interactor_cls rdagent.scenarios.data_science.interactor.FBDSInteractor"

and then start the frontend server with the following command:

    mydotenv.sh streamlit run rdagent/log/ui/ds_user_interact.py
"""
from dotenv import set_key
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'


set_key(str(env_path), 'DS_USER_INTERACTION_WAIT_SECONDS', "60")

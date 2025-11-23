import typer
from dotenv import set_key
from pathlib import Path

app = typer.Typer()

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
print(env_path)

@app.command()
def set_deploy():
    set_key(str(env_path), 'DS_EXP_GEN_HYPOTHESIS_DESC', 'We are putting this solution online, so we aim to remove any unnecessary code without hurting the final results. For example, we will use the best hyperparameters or features already found in the stdout instead of searching for them again, remove code used only for analysis, and delete unused models.')
    set_key(str(env_path), 'APP_TPL', 'app/ts/tpl/')
    set_key(str(env_path), 'DS_ENABLE_MODEL_DUMP', "True")


@app.command()
def set_intention(intention: str):
    """
    After setting intention, you can start the experiment loop with the following command:

    .. code-block:: bash

        m=cube
        LOG_TRACE_PATH=./log/$m
        script -c "LOG_TRACE_PATH=$LOG_TRACE_PATH mydotenv.sh python -m ipdb -c c  rdagent/app/data_science/loop.py --competition $m --path $LOG_TRACE_PATH --exp_gen_cls rdagent.scenarios.data_science.proposal.exp_gen.custom.CustomExpGen"
    """
    set_key(str(env_path), 'DS_EXP_GEN_HYPOTHESIS_DESC', intention)

@app.command()
def unset_deploy():
    from dotenv import unset_key
    unset_key(str(env_path), 'DS_EXP_GEN_HYPOTHESIS_DESC')
    unset_key(str(env_path), 'APP_TPL')
    unset_key(str(env_path), 'DS_ENABLE_MODEL_DUMP')

if __name__ == "__main__":
    app()

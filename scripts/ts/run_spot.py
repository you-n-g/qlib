# def build_dataset
# cd /Data/home/xiaoyang/repos/RD-Agent-QUBE/git_ignore_folder/ds_data/cube
# mkdir -p data
# sudo mount --bind  ~/data/high-freq/bar/klinescoin.parquet data
# cp rdagent/app/ts/description.md  git_ignore_folder/ds_data/cube/description.md

# TODO:  checkout to me/ts_scen and pip install -e .

import typer
import subprocess
from pathlib import Path

from prefect import task
from prefect.cache_policies import INPUTS, TASK_SOURCE
from rdagent.utils.agent.tpl import T

DIRNAME = Path(__file__).absolute().resolve().parent

PROJECT_ROOT = DIRNAME.parent.parent

app = typer.Typer()


@app.command()
def deploy_data():
    data_dir = PROJECT_ROOT / "git_ignore_folder" / "ds_data" / "cube-spot" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    task(cache_policy=TASK_SOURCE + INPUTS)(subprocess.run)(
        f'sudo mount --bind  ~/data/high-freq/bar/klines-1T-symbol.parquet "{data_dir}"', shell=True)

    with data_dir.parent.joinpath("description.md").open("w") as f:
        f.write(
            T("app.ts.description", ftype="md").r(instruments=" ".join([f.stem for f in data_dir.glob("*.parquet")])))


if __name__ == "__main__":
    app()

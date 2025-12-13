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

def ensure_perm(path: Path):
    current_path = path
    while current_path != PROJECT_ROOT:
        subprocess.run(["sudo", "chown", f"{Path.home().owner()}", str(current_path)], check=False)
        current_path = current_path.parent
    subprocess.run(["sudo", "chown", f"{Path.home().owner()}", str(PROJECT_ROOT)], check=False)

def deploy_data(source_path="~/data/high-freq/bar/klines-1T-symbol.parquet", competition="cube-spot"):
    data_dir = PROJECT_ROOT / "git_ignore_folder" / "ds_data" / competition / "data"

    ensure_perm(data_dir.parent)
    data_dir.mkdir(parents=True, exist_ok=True)

    mount_cmd = f'sudo mount --bind {source_path}  "{data_dir}"'
    check_mount_cmd = f'mount | grep "{data_dir}"'
    if subprocess.run(check_mount_cmd, shell=True).returncode != 0:
        task(cache_policy=TASK_SOURCE + INPUTS)(subprocess.run)(mount_cmd, shell=True)
    else:
        print("Data already mounted.")

    with data_dir.parent.joinpath("description.md").open("w") as f:
        f.write(
            T("app.ts.description", ftype="md").r(instruments=" ".join([f.stem for f in data_dir.glob("*.parquet")])))

@app.command()
def deploy_all():
    deploy_data()
    deploy_data("/home/xiaoyang/data/high-freq/bar/klinescoin.parquet/", competition="cube")

if __name__ == "__main__":
    app()

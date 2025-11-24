from pathlib import Path
from collections import defaultdict
import pickle
import typer
import pandas as pd

app = typer.Typer(help="Load a session from a specific path and create a new session as in refine_trace.py.")


def load_session(session_path: Path):
    p_l = sorted((session_path / "__session__/").glob("*/*"), key=lambda p: (int(p.parent.name), p.name))
    for p in p_l[::-1]:
        if p.name.startswith("4_"):
            with open(p, "rb") as f:
                sess = pickle.load(f)
            return sess
    raise FileNotFoundError(f"No session record starting with '4_' found under {session_path / '__session__'}")

def update_session(sess, from_workspace: Path):

    exp = sess.trace.hist[0][0]
    assert exp.sub_workspace_list[0] is exp.experiment_workspace
    ws = exp.experiment_workspace

    exp.result = pd.read_csv(from_workspace / "scores.csv", index_col=0)
    ws.workspace_path = from_workspace
    for file in ["main.py", "EDA.md", "stdout.txt"]:
        with open(from_workspace / file, "r") as f:
            ws.file_dict[file] = f.read()

def create_new_session(from_session: Path, end_idx: None | int = None, from_workspace: Path | None = None,
                       out_path: Path = "log/cube/", force: bool = False):
    """
    from_session is a path with dataset name like "cube"
    """

    # Load session
    sess = load_session(from_session)

    # Select best item (same criteria as refine_trace.py) but respect scenario metric direction
    direction = getattr(getattr(sess, "scen", None), "metric_direction", True)
    best_item = sorted(
        sess.trace.hist[:end_idx],
        key=lambda x: (
            x[1].decision,
            x[1].decision
            and (
                -x[0].result.iloc[:, -1]["ensemble"].item()
                if not direction
                else x[0].result.iloc[:, -1]["ensemble"].item()
            ),
        ),
    )[-1]
    print(f"{sess.trace.hist.index(best_item)=}")

    # Determine LOOP_IDX where experiment object identity matches
    for LOOP_IDX in range(len(sess.trace.hist)):
        if sess.trace.hist[LOOP_IDX][0] is best_item[0]:
            break
    else:
        raise RuntimeError("Failed to locate LOOP_IDX for best_item.")

    # Reset uncommitted record status if scheduler exists
    if hasattr(sess.exp_gen, "trace_scheduler"):
        sess.exp_gen.trace_scheduler.uncommited_rec_status = defaultdict(int)

    # Prepare the new session path (fixed path as in refine_trace.py)
    out_path = Path(out_path)
    sess_path = out_path / "__session__"
    if sess_path.exists():
        if force:
            import shutil
            shutil.rmtree(sess_path)
        else:
            raise RuntimeError(f"Session path {sess_path} already exists.")

    # Rebuild trace focusing on the selected loop
    trace = sess.trace
    for k, v in trace.idx2loop_id.items():
        if v == LOOP_IDX:
            enq_idx = k
            break
    else:
        raise RuntimeError(f"Failed to find enqueue index for LOOP_IDX={LOOP_IDX}.")

    trace.hist = [trace.hist[enq_idx]]
    trace.idx2loop_id = {0: 0}
    trace.dag_parent = [()]

    # Reset loop-related states
    sess.loop_prev_out = defaultdict(dict)
    sess.loop_idx = 1  # type: ignore[attr-defined]
    sess.step_idx = defaultdict(int)  # dict from loop index to next step index
    sess.step_idx[0] = len(sess.steps)
    sess.step_idx[1] = 0
    loop_trace = defaultdict(list)
    loop_trace[0] = sess.loop_trace[enq_idx]
    sess.loop_trace = loop_trace

    # Point session to the new session folder
    sess.session_folder = sess_path

    if from_workspace is not None:
        update_session(sess, from_workspace)

    # Dump the new session record
    sess_loop_path = sess_path / "0"
    sess_loop_path.mkdir(parents=True, exist_ok=True)

    # update_session(sess)
    with open(sess_loop_path / f"{len(sess.steps) - 1}_record", "wb") as f:
        pickle.dump(sess, f)


@app.command("create")
def cli_create(
    session_path: str,
    end_idx: None | int = typer.Option(None, "-e", help="Optional end index to consider in the session trace"),
    from_workspace: Path | None = typer.Option(None, "-w", help="Optional workspace path to update session from"),
    out_path: Path | None = typer.Option("log/cube/", "-o", help="Optional output path"),
    force: bool = typer.Option(False, "-f", help="Force remove existing session path if it exists"),
):
    """
    Load session from a specific path and create a new session (same logic as scripts/refine_trace.py).

    -p, --session-path: Path to the base folder of a session (e.g., log/cube or log/backup/cube-...[/cube])
    -e, --end-idx: Optional end index to consider in the session trace
    -w, --from-workspace: Optional workspace path to update session from

    Example:

        python scripts/create_session.py ./log/cube/ -e  1 -w ./git_ignore_folder/RD-Agent_workspace/badae57f66fe454f90513e0cff1717d2/
    """
    create_new_session(Path(session_path), end_idx=end_idx, from_workspace=from_workspace, out_path=out_path, force=force)


if __name__ == "__main__":
    app()

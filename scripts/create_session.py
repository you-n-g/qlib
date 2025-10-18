from pathlib import Path
from collections import defaultdict
import pickle
import typer

app = typer.Typer(help="Load a session from a specific path and create a new session as in refine_trace.py.")


def load_session(session_path: Path):
    p_l = sorted((session_path / "__session__/").glob("*/*"), key=lambda p: (int(p.parent.name), p.name))
    for p in p_l[::-1]:
        if p.name.startswith("4_"):
            with open(p, "rb") as f:
                sess = pickle.load(f)
            return sess
    raise FileNotFoundError(f"No session record starting with '4_' found under {session_path / '__session__'}")

def update_session(sess):
    from IPython import embed; embed()  # update session before dumping
    sess.exp_gen
    from rdagent.app.data_science.conf import DS_RD_SETTING

    from rdagent.core.utils import import_class

def create_new_session(from_session: Path) -> None:
    """
    from_session is a path including dataset name like "cube"
    """

    # Load session
    sess = load_session(from_session)

    # Select best item (same criteria as refine_trace.py) but respect scenario metric direction
    direction = getattr(getattr(sess, "scen", None), "metric_direction", True)
    best_item = sorted(
        sess.trace.hist,
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
    sess_path = Path("log/cube/__session__")

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

    # Dump the new session record
    sess_loop_path = sess_path / "0"
    sess_loop_path.mkdir(parents=True, exist_ok=True)

    # update_session(sess)
    with open(sess_loop_path / f"{len(sess.steps) - 1}_record", "wb") as f:
        pickle.dump(sess, f)


@app.command("create")
def cli_create(session_path: str):
    """
    Load session from a specific path and create a new session (same logic as scripts/refine_trace.py).

    session_path: Path to the base folder of a session (e.g., log/cube or log/backup/cube-...[/cube])
    """
    create_new_session(Path(session_path))


if __name__ == "__main__":
    app()

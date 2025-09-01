
from pathlib import Path
import pickle

def load_session(session_path: Path):
    p_l = sorted((session_path / "__session__/").glob("*/*"), key=lambda p: (int(p.parent.name), p.name))
    for p in p_l[::-1]:
        if p.name.startswith("4_"):
            with open(p, "rb") as f:
                sess = pickle.load(f)
            return sess

# %%
from pathlib import Path

# from_session = "log/backup/cube-2025-08-31-15h-05m"
from_session = max(Path("log/backup").glob("cube-*"))
if (from_session / "cube").exists():
    from_session = from_session / "cube"
sess = load_session(from_session)

best_item = sorted(sess.trace.hist, key = lambda x: (x[1].decision, x[1].decision and x[0].result.iloc[:, -1]["ensemble"].item()))[-1]

best_item[0].result


for LOOP_IDX in range(len(sess.trace.hist)):
    if sess.trace.hist[LOOP_IDX][0] is best_item[0]:
        break

from_session, LOOP_IDX

# %%

from pathlib import Path
import pickle


def backup_session(session_path: Path, log_path: Path):
    log_path = Path("./log/cube")
    backup_path = log_path / "session_backup"

    # move __session__ and Loop_* into backup_path
    import shutil

    session_path = Path("./log/cube/__session__")
    loop_path = Path("./log/cube/Loop_*")

    # Create backup path if it doesn't exist
    backup_path.mkdir(parents=True, exist_ok=True)

    # Move __session__ directory
    if session_path.exists():
        shutil.move(str(session_path), str(backup_path / "__session__"))

    # Move Loop_* directories
    for loop_dir in Path("./log/cube/").glob("Loop_*"):
        if loop_dir.is_dir():
            shutil.move(str(loop_dir), str(backup_path / loop_dir.name))



# %%

def mock_session():
    trace = sess.trace


    for k, v in trace.idx2loop_id.items():
        if v == LOOP_IDX:
            enq_idx = k

    parents = trace.get_parents(enq_idx)
    enqidx2new = {}
    dag_parent_new = []

    hist_new = []
    for idx in parents:
        node = trace.hist[idx]
        if node[1].decision:
            if len(hist_new) == 0:
                dag_parent_new.append(())
            else:
                dag_parent_new.append((len(hist_new),))
            enqidx2new[idx] = len(hist_new)
            hist_new.append(node)


    for idx, new_idx in enqidx2new.items():
        shutil.copytree(str(backup_path / f"Loop_{idx}"), str(log_path / f"Loop_{new_idx}"))


    sess.trace.dag_parent = dag_parent_new
    sess.trace.hist = hist_new
    sess.trace.idx2loop_id = {idx: idx for idx in range(len(hist_new))}

    sess_loop_path = session_path / f"{len(hist_new) - 1}"
    sess_loop_path.mkdir(parents=True, exist_ok=True)
    with open(sess_loop_path / p_l[-1].name, "wb") as f:
        pickle.dump(sess, f)


# %%

# from_session = Path("log/cube/")
from collections import defaultdict
sess = load_session(from_session)

if hasattr(sess.exp_gen, "trace_scheduler"):
    sess.exp_gen.trace_scheduler.uncommited_rec_status = defaultdict(int)

sess_path = Path("log/cube/__session__")

trace = sess.trace
for k, v in trace.idx2loop_id.items():
    if v == LOOP_IDX:
        enq_idx = k

trace.hist = [trace.hist[enq_idx]]
trace.idx2loop_id = {0: 0}
trace.dag_parent = [()]

sess.loop_prev_out = defaultdict(dict)
sess.loop_idx: int = 1
sess.step_idx = defaultdict(int)  # dict from loop index to next step index
sess.step_idx[0] = len(sess.steps)
sess.step_idx[1] = 0
loop_trace = defaultdict(list)
loop_trace[0] = sess.loop_trace[enq_idx]
sess.loop_trace = loop_trace

sess.session_folder = sess_path

sess_loop_path = sess_path / f"0"
# sess_loop_path = sess_path / f"12"
sess_loop_path.mkdir(parents=True, exist_ok=True)
with open(sess_loop_path / f"{len(sess.steps) - 1}_record", "wb") as f:
    pickle.dump(sess, f)

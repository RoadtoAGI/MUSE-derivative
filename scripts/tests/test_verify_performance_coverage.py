import subprocess, sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "verify_performance_coverage.py"

def run(work_dir, scene=None):
    cmd = [sys.executable, str(SCRIPT), "--work-dir", str(work_dir)]
    if scene: cmd += ["--scene", scene]
    return subprocess.run(cmd, capture_output=True, text=True)

def make_scene(root, sid, slugs, perf_slugs=None, skip_entries=None):
    sd = root / "pipeline" / f"scene_{sid}"; sd.mkdir(parents=True)
    (sd / "role_briefs.md").write_text(
        "\n".join(f"character: {s}" for s in slugs), encoding="utf-8")
    st = root / "pipeline" / "staging" / f"scene_{sid}"; st.mkdir(parents=True)
    for s in (perf_slugs or []):
        (st / f"{s}_performance.md").write_text(
            f"character: {s}\nlines:\n  - text: x\nforbidden:\n  - y\n", encoding="utf-8")
    if skip_entries is not None:
        ad = root / "pipeline" / "audit"; ad.mkdir(parents=True, exist_ok=True)
        (ad / "skip_performance.yaml").write_text(skip_entries, encoding="utf-8")

def test_set_equal_pass(tmp_path):
    make_scene(tmp_path, "S01", ["a", "b"], perf_slugs=["a", "b"])
    assert run(tmp_path, "S01").returncode == 0

def test_count_equal_but_wrong_slug_fails(tmp_path):
    make_scene(tmp_path, "S01", ["a", "b"], perf_slugs=["a", "c"])
    r = run(tmp_path, "S01"); assert r.returncode == 1 and "b" in r.stderr

def test_single_role_needs_skip_entry(tmp_path):
    make_scene(tmp_path, "S02", ["a"])          # 无 performance 无声明
    assert run(tmp_path, "S02").returncode == 1

def test_valid_skip_entry_passes(tmp_path):
    make_scene(tmp_path, "S02", ["a"],
               skip_entries="- scene_id: S02\n  reason: 单角色内心戏\n")
    assert run(tmp_path, "S02").returncode == 0

def test_multi_role_valid_skip_entry_passes(tmp_path):
    make_scene(tmp_path, "S03", ["a", "b"],
               skip_entries="- scene_id: S03\n  reason: scene_card 标记无对白过渡\n")
    assert run(tmp_path, "S03").returncode == 0

def test_batch_skip_rejected(tmp_path):
    make_scene(tmp_path, "S03", ["a", "b"],
               skip_entries="- scene_id: all\n  reason: 本 run 无需\n")
    r = run(tmp_path, "S03"); assert r.returncode == 1 and "all" in r.stderr

def test_missing_min_fields_fails(tmp_path):
    make_scene(tmp_path, "S04", ["a"], perf_slugs=["a"])
    p = tmp_path / "pipeline/staging/scene_S04/a_performance.md"
    p.write_text("character: a\n", encoding="utf-8")   # 缺 lines/forbidden
    r = run(tmp_path, "S04"); assert r.returncode == 1 and "lines" in r.stderr

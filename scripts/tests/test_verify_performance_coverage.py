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

def test_skip_cannot_mask_missing_role_briefs(tmp_path):
    """skip 是'本场不产素材'的豁免,不是'上游 role_brief 缺失'的豁免。"""
    (tmp_path / "pipeline" / "scene_S05").mkdir(parents=True)   # 无 role_briefs.md
    ad = tmp_path / "pipeline" / "audit"; ad.mkdir(parents=True)
    (ad / "skip_performance.yaml").write_text(
        "- scene_id: S05\n  reason: 单角色内心戏\n", encoding="utf-8")
    r = run(tmp_path, "S05")
    assert r.returncode == 1 and "role_briefs" in r.stderr

def test_skip_cannot_mask_empty_role_briefs(tmp_path):
    """role_briefs 存在但无 character: 段,同样是上游漏步,不可被 skip 掩盖。"""
    sd = tmp_path / "pipeline" / "scene_S05"; sd.mkdir(parents=True)
    (sd / "role_briefs.md").write_text("# 空文件\n", encoding="utf-8")
    ad = tmp_path / "pipeline" / "audit"; ad.mkdir(parents=True)
    (ad / "skip_performance.yaml").write_text(
        "- scene_id: S05\n  reason: 单角色内心戏\n", encoding="utf-8")
    r = run(tmp_path, "S05")
    assert r.returncode == 1 and "role_briefs" in r.stderr

def test_zero_scene_full_scan_fails(tmp_path):
    """全扫描发现零场景 = work-dir 传错,静默 exit 0 会放行 writer。"""
    (tmp_path / "pipeline").mkdir(parents=True)
    r = run(tmp_path)
    assert r.returncode == 1 and "scene_" in r.stderr

def test_fenced_yaml_body_passes(tmp_path):
    """actor 把 schema 包在 ```yaml fence 里是合法产物形态,不得误杀。"""
    make_scene(tmp_path, "S06", ["a"], perf_slugs=["a"])
    p = tmp_path / "pipeline/staging/scene_S06/a_performance.md"
    p.write_text(
        '# a — scene S06 performance\n\n```yaml\ncharacter: a\n'
        'lines:\n  - to: b\n    text: "x"\nforbidden:\n  - 谄媚称呼\n```\n',
        encoding="utf-8")
    assert run(tmp_path, "S06").returncode == 0

def test_empty_key_shell_fails(tmp_path):
    """光有 key 没有条目 = 实质缺字段(design §7 '缺 lines 或 forbidden')。"""
    make_scene(tmp_path, "S07", ["a"], perf_slugs=["a"])
    p = tmp_path / "pipeline/staging/scene_S07/a_performance.md"
    p.write_text("character: a\n\n```\nlines:\nforbidden:\n```\n", encoding="utf-8")
    r = run(tmp_path, "S07")
    assert r.returncode == 1 and "lines" in r.stderr

def test_commented_key_does_not_count(tmp_path):
    """HTML 注释里的 key 不算真实字段。"""
    make_scene(tmp_path, "S08", ["a"], perf_slugs=["a"])
    p = tmp_path / "pipeline/staging/scene_S08/a_performance.md"
    p.write_text(
        "character: a\n<!--\nlines:\n  - text: x\nforbidden:\n  - y\n-->\n",
        encoding="utf-8")
    r = run(tmp_path, "S08")
    assert r.returncode == 1 and "lines" in r.stderr

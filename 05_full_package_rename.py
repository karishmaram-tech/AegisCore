#!/usr/bin/env python3
"""
05_full_package_rename.py
=====================
Phase 2, final step: physically renames every "decepticon"-named directory
(via `git mv`, so history is preserved) and rewrites every Python import,
Go module reference, npm workspace package name, and GitHub URL across the
ENTIRE repo to match. This is the highest-risk step in the whole migration —
it's the one where the EXTERNAL-tier dry run (04) revealed that text-only
edits would have pointed pyproject.toml/Dockerfiles at directories that
didn't exist yet. This script does the rename AND the reference-rewrite
together, in the correct order, so nothing is left dangling.

STRONGLY RECOMMENDED before running live: commit your current clean state
first (`git add -A && git commit -m "..."`), so `git reset --hard HEAD` is
an instant full undo if anything looks wrong afterward.

What it does, in order:
  1. Renames these directories/files via `git mv` (preserves history):
       packages/decepticon-core            -> packages/aegiscore-core
       packages/decepticon-core/decepticon_core -> .../aegiscore_core
       packages/decepticon-sdk             -> packages/aegiscore-sdk
       packages/decepticon-sdk/decepticon_sdk   -> .../aegiscore_sdk
       packages/decepticon-sdk/examples/*/src/decepticon_example_*  (x6)
       packages/decepticon                 -> packages/aegiscore
       packages/aegiscore/decepticon       -> packages/aegiscore/aegiscore
       .../skills/standard/decepticon      -> .../skills/standard/aegiscore
       .semgrep/decepticon-rules.yml       -> .semgrep/aegiscore-rules.yml
       .github/actions/decepticon-scan     -> .github/actions/aegiscore-scan
       integrations/agent-skills/decepticon -> integrations/agent-skills/aegiscore

  2. Rewrites, repo-wide (every .py/.go/.toml/.json/.yml/.md/.sh/.ps1/etc,
     excluding node_modules/.venv/__pycache__/dist/build/.git and lockfiles):
       - Compound identifiers: decepticon-core, decepticon_core,
         decepticon-sdk, decepticon_sdk, decepticon_example_*
       - The GitHub org+repo path: PurpleAILAB/Decepticon -> the new one
         you specified (this also fixes the Go module path in
         clients/launcher/go.mod and every internal Go import that uses it)
       - Every remaining standalone "decepticon" / "Decepticon" / "sentinel
         ai" (any spacing/case), case-preserved, same logic as the cosmetic
         script

  NOTE: the GHCR container registry namespace (ghcr.io/purpleailab/...) is
  left as "purpleailab" on purpose — that's a separate decision (your GHCR
  publishing target) from your GitHub source repo, already reviewed and
  approved in step 04's dry run. This script only touches the GitHub
  org/repo path, not the container registry namespace.

  NOT touched (regenerate with their own tools afterward):
       package-lock.json, uv.lock, go.sum

Usage:
    python 05_full_package_rename.py     # dry run: shows the rename plan
                                          # and a match-count summary, writes nothing
    # commit your current state, review the plan, then:
    # edit DRY_RUN = False below
    python 05_full_package_rename.py     # applies for real
"""

import re
import shutil
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(r"C:\Users\Pawan\sentinel-ai")
DRY_RUN = True   # <-- flip to False only after committing + reviewing the plan

NEW_BRAND = "aegiscore"
OLD_GITHUB_PATH = "PurpleAILAB/Decepticon"
NEW_GITHUB_PATH = "karishmaram-tech/AegisCore"

MIGRATION_DIR = PROJECT_DIR / "scripts" / "migration"
MIGRATION_DIR.mkdir(parents=True, exist_ok=True)

BACKUP_ROOT = PROJECT_DIR.parent / "_aegiscore_migration_backups"

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".next",
    "dist", "build", ".mypy_cache", ".pytest_cache", ".idea", ".vscode",
    "volumes", ".turbo", "target", "eggs", ".eggs", "scripts",  # scripts/migration excluded
}
SKIP_FILENAMES = {"package-lock.json", "uv.lock", "go.sum", "yarn.lock"}
MAX_FILE_SIZE_BYTES = 3_000_000

# ---------------------------------------------------------------------------
# Directory renames — ORDER MATTERS. Each path assumes prior renames in
# this list have already been applied.
# ---------------------------------------------------------------------------
DIRECTORY_RENAMES = [
    ("packages/decepticon-core", "packages/aegiscore-core"),
    ("packages/aegiscore-core/decepticon_core", "packages/aegiscore-core/aegiscore_core"),

    ("packages/decepticon-sdk", "packages/aegiscore-sdk"),
    ("packages/aegiscore-sdk/decepticon_sdk", "packages/aegiscore-sdk/aegiscore_sdk"),
    ("packages/aegiscore-sdk/examples/agent/src/decepticon_example_agent",
     "packages/aegiscore-sdk/examples/agent/src/aegiscore_example_agent"),
    ("packages/aegiscore-sdk/examples/callback/src/decepticon_example_callback",
     "packages/aegiscore-sdk/examples/callback/src/aegiscore_example_callback"),
    ("packages/aegiscore-sdk/examples/middleware/src/decepticon_example_middleware",
     "packages/aegiscore-sdk/examples/middleware/src/aegiscore_example_middleware"),
    ("packages/aegiscore-sdk/examples/prompt/src/decepticon_example_prompt",
     "packages/aegiscore-sdk/examples/prompt/src/aegiscore_example_prompt"),
    ("packages/aegiscore-sdk/examples/skill/src/decepticon_example_skill",
     "packages/aegiscore-sdk/examples/skill/src/aegiscore_example_skill"),
    ("packages/aegiscore-sdk/examples/tool/src/decepticon_example_tool",
     "packages/aegiscore-sdk/examples/tool/src/aegiscore_example_tool"),

    ("packages/decepticon", "packages/aegiscore"),
    ("packages/aegiscore/decepticon", "packages/aegiscore/aegiscore"),
    ("packages/aegiscore/aegiscore/skills/standard/decepticon",
     "packages/aegiscore/aegiscore/skills/standard/aegiscore"),

    (".semgrep/decepticon-rules.yml", ".semgrep/aegiscore-rules.yml"),
    (".github/actions/decepticon-scan", ".github/actions/aegiscore-scan"),
    ("integrations/agent-skills/decepticon", "integrations/agent-skills/aegiscore"),
]

# ---------------------------------------------------------------------------
# Text substitution mapping
# ---------------------------------------------------------------------------
LITERAL_MAPPING = OrderedDict([
    (OLD_GITHUB_PATH, NEW_GITHUB_PATH),
    ("decepticon-core", "aegiscore-core"),
    ("decepticon_core", "aegiscore_core"),
    ("decepticon-sdk", "aegiscore-sdk"),
    ("decepticon_sdk", "aegiscore_sdk"),
    ("decepticon_example_", "aegiscore_example_"),
])

TERM_PATTERN = re.compile(r"\b(?:sentinel[\s_-]?ai|decepticon)\b", re.IGNORECASE)


def case_matched_replacement(match: re.Match) -> str:
    s = match.group(0)
    if s.isupper():
        return NEW_BRAND.upper()
    if s[0].isupper():
        return NEW_BRAND[0].upper() + NEW_BRAND[1:]
    return NEW_BRAND


def apply_rebrand(text: str) -> str:
    for old, new in LITERAL_MAPPING.items():
        text = text.replace(old, new)
    return TERM_PATTERN.sub(case_matched_replacement, text)


def run(cmd, cwd=None):
    print(f"[cmd] {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def is_git_repo(root: Path) -> bool:
    r = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=str(root))
    return r.returncode == 0 and r.stdout.strip() == "true"


def is_probably_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(8000)
        return b"\0" in chunk
    except Exception:
        return True


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILENAMES:
            continue
        try:
            if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                continue
        except OSError:
            continue
        yield path


# ---------------------------------------------------------------------------
# Step 1: directory renames
# ---------------------------------------------------------------------------
def plan_directory_renames(root: Path):
    """Simulates the sequence: later entries often live under a path that
    only exists after an earlier entry in this same list has been applied.
    We track which renames are 'virtually done' so far and resolve each
    entry's real on-disk path accordingly, instead of checking every entry
    against the untouched starting filesystem."""
    plan = []
    applied = []  # [(old_rel, new_rel), ...] simulated as done, in order
    for old_rel, new_rel in DIRECTORY_RENAMES:
        real_old_rel = old_rel
        for prev_old, prev_new in applied:
            if real_old_rel == prev_new or real_old_rel.startswith(prev_new + "/"):
                real_old_rel = prev_old + real_old_rel[len(prev_new):]
                break
        old_path = root / real_old_rel
        new_path = root / new_rel
        if old_path.exists():
            plan.append((old_rel, new_rel, real_old_rel, "WILL RENAME"))
            applied.append((old_rel, new_rel))
        elif new_path.exists():
            plan.append((old_rel, new_rel, real_old_rel, "already done - skip"))
            applied.append((old_rel, new_rel))
        else:
            plan.append((old_rel, new_rel, real_old_rel, "MISSING - neither path exists!"))
    return plan


def execute_directory_renames(root: Path, use_git: bool):
    for old_rel, new_rel in DIRECTORY_RENAMES:
        old_path = root / old_rel
        new_path = root / new_rel
        if not old_path.exists():
            if new_path.exists():
                print(f"  [skip] {new_rel} already exists")
                continue
            sys.exit(f"[error] Neither {old_rel} nor {new_rel} exists — aborting mid-sequence. "
                      f"Check the plan output above before re-running.")
        new_path.parent.mkdir(parents=True, exist_ok=True)
        if use_git:
            r = run(["git", "mv", old_rel, new_rel], cwd=str(root))
            if r.returncode != 0:
                sys.exit(f"[error] git mv failed for {old_rel} -> {new_rel}:\n{r.stderr}")
        else:
            shutil.move(str(old_path), str(new_path))
        print(f"  [renamed] {old_rel}  ->  {new_rel}")


# ---------------------------------------------------------------------------
# Step 2: repo-wide text rebrand
# ---------------------------------------------------------------------------
def dry_run_text_scan(root: Path):
    results = []
    for path in iter_text_files(root):
        if is_probably_binary(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        updated = apply_rebrand(text)
        if updated != text:
            count = sum(1 for _ in TERM_PATTERN.finditer(text)) + sum(
                text.count(k) for k in LITERAL_MAPPING
            )
            results.append((str(path.relative_to(root)), count))
    return results


def apply_text_rebrand(root: Path, backup_dir: Path):
    changed = 0
    total_replacements = 0
    log_rows = []
    for path in iter_text_files(root):
        if is_probably_binary(path):
            continue
        rel = path.relative_to(root)
        try:
            original = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  [warn] could not read {rel}: {e}")
            continue
        updated = apply_rebrand(original)
        if updated == original:
            continue
        changed += 1
        backup_path = backup_dir / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        updated_lf = updated.replace("\r\n", "\n")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(updated_lf)
        log_rows.append(str(rel))
        total_replacements += 1
    return changed, log_rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not PROJECT_DIR.exists():
        sys.exit(f"[error] Project directory not found: {PROJECT_DIR}")

    use_git = is_git_repo(PROJECT_DIR)
    mode = "DRY RUN (no files touched)" if DRY_RUN else "LIVE (renaming + rewriting for real)"
    print("=" * 72)
    print(f"Full package rename — {mode}")
    print(f"Using {'git mv (history preserved)' if use_git else 'shutil.move (NOT a git repo!)'}")
    print("=" * 72)

    print("\n--- Directory rename plan ---")
    plan = plan_directory_renames(PROJECT_DIR)
    for old_rel, new_rel, real_old_rel, status in plan:
        resolved_note = f"  (resolves to: {real_old_rel})" if real_old_rel != old_rel else ""
        print(f"  [{status:30}] {old_rel}  ->  {new_rel}{resolved_note}")

    missing = [p for p in plan if "MISSING" in p[3]]
    if missing:
        print(f"\n[error] {len(missing)} planned rename(s) have neither source nor "
              f"destination path — the directory layout may have changed since this "
              f"script was written. Aborting before touching anything.")
        sys.exit(1)

    print("\n--- Text rebrand scan (repo-wide) ---")
    if DRY_RUN:
        results = dry_run_text_scan(PROJECT_DIR)
        results.sort(key=lambda r: -r[1])
        for rel, count in results[:40]:
            print(f"  [{count:>4} matches] {rel}")
        if len(results) > 40:
            print(f"  ... and {len(results) - 40} more files")
        print(f"\nWould modify {len(results)} files.")

        report_path = MIGRATION_DIR / "05_text_rebrand_dry_run.txt"
        report_path.write_text(
            "\n".join(f"[{c:>4} matches] {r}" for r, c in results),
            encoding="utf-8", newline="\n",
        )
        print(f"Full list written to {report_path}")

        print("\n" + "=" * 72)
        print("This was a DRY RUN. Nothing was renamed or rewritten.")
        print("Recommended before going live:")
        print('  git add -A && git commit -m "Phase 2: pre-package-rename checkpoint"')
        print("Then set DRY_RUN = False and run again.")
        return

    # ---- LIVE ----
    print("\n--- Executing directory renames ---")
    execute_directory_renames(PROJECT_DIR, use_git)

    print("\n--- Applying repo-wide text rebrand ---")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = BACKUP_ROOT / f"full_rename_{stamp}"
    changed, log_rows = apply_text_rebrand(PROJECT_DIR, backup_dir)
    print(f"Modified {changed} files.")

    log_path = MIGRATION_DIR / "05_text_rebrand_log.txt"
    log_path.write_text("\n".join(log_rows), encoding="utf-8", newline="\n")
    print(f"Change log written to {log_path}")
    print(f"Backups (outside the repo) written to {backup_dir}")

    print("\n" + "=" * 72)
    print("Done. Required follow-up (not automated on purpose):")
    print("  1. uv sync --extra neo4j          (relink workspace members under new names)")
    print("  2. npm install                     (regenerate package-lock.json)")
    print("  3. docker compose build --no-cache")
    print("  4. docker compose up -d --force-recreate")
    print("  5. Create the empty repo at github.com/%s, then:" % NEW_GITHUB_PATH)
    print("       git remote set-url origin https://github.com/%s.git" % NEW_GITHUB_PATH)
    print("  6. Run your test suite before pushing anywhere.")


if __name__ == "__main__":
    main()

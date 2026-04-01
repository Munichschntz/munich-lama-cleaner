#!/usr/bin/env python3
"""Clean local build artifacts, build a wheel, and install it.

Usage examples:
  python scripts/clean_rebuild.py --venv .venv311 --with-deps
  python scripts/clean_rebuild.py --venv .venv --no-deps
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

CLEAN_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    "build",
    "dist",
}


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> int:
    print(f"\n$ {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=cwd, text=True)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def is_tracked(repo: Path, rel: Path) -> bool:
    proc = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(rel)],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.returncode == 0


def clean_artifacts(repo: Path, include_venv: bool) -> None:
    removed: list[Path] = []
    skipped: list[Path] = []

    for path in sorted(repo.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if not path.is_dir():
            continue

        rel = path.relative_to(repo)
        if ".git" in rel.parts:
            continue
        if not include_venv and ".venv" in rel.parts:
            continue

        if path.name in CLEAN_NAMES or path.name.endswith(".egg-info"):
            if is_tracked(repo, rel):
                skipped.append(rel)
                continue
            shutil.rmtree(path, ignore_errors=True)
            removed.append(rel)

    print(f"Removed {len(removed)} artifact directories")
    for rel in removed:
        print(f" - {rel}")
    if skipped:
        print(f"Skipped {len(skipped)} tracked directories")
        for rel in skipped:
            print(f" - {rel}")


def resolve_python(repo: Path, venv: str | None) -> str:
    if not venv:
        return sys.executable

    venv_path = (repo / venv).resolve()
    if sys.platform.startswith("win"):
        candidate = venv_path / "Scripts" / "python.exe"
    else:
        candidate = venv_path / "bin" / "python"

    if not candidate.exists():
        raise SystemExit(f"Python interpreter not found at: {candidate}")
    return str(candidate)


def main() -> None:
    parser = argparse.ArgumentParser(description="Full clean + wheel rebuild + reinstall")
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument("--venv", default=None, help="Target virtualenv directory (e.g. .venv311)")
    parser.add_argument("--include-venv-clean", action="store_true", help="Also clean artifacts under .venv")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--with-deps", action="store_true", help="Install wheel and resolve dependencies")
    mode.add_argument("--no-deps", action="store_true", help="Install wheel without dependency resolution")

    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not (repo / "setup.py").exists():
        raise SystemExit(f"Not a package repo (setup.py missing): {repo}")

    with_deps = True
    if args.no_deps:
        with_deps = False

    print(f"Repository: {repo}")
    clean_artifacts(repo, include_venv=args.include_venv_clean)

    py = resolve_python(repo, args.venv)
    print(f"Using Python: {py}")

    run([py, "-m", "pip", "install", "-U", "pip", "setuptools", "wheel", "build"], cwd=repo)
    run([py, "-m", "build", "--wheel", str(repo)], cwd=repo)

    wheel_files = sorted((repo / "dist").glob("*.whl"))
    if not wheel_files:
        raise SystemExit("No wheel found in dist/")

    wheel = wheel_files[-1]
    install_cmd = [py, "-m", "pip", "install", "--force-reinstall"]
    if not with_deps:
        install_cmd.append("--no-deps")
    install_cmd.append(str(wheel))

    run([py, "-m", "pip", "uninstall", "-y", "lama-cleaner"], cwd=repo, check=False)
    run(install_cmd, cwd=repo)
    run([py, "-m", "pip", "show", "lama-cleaner"], cwd=repo)

    print("\nClean rebuild finished.")


if __name__ == "__main__":
    main()

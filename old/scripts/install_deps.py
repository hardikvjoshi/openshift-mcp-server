#!/usr/bin/env python3
"""
Install only missing dependencies from requirements.txt.

Usage:
  - Check what would be installed (no changes):
      python3 scripts/install_deps.py --check
  - Install missing only:
      python3 scripts/install_deps.py
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict


def read_requirements(requirements_path: Path) -> List[str]:
    if not requirements_path.exists():
        print(f"requirements.txt not found at: {requirements_path}")
        sys.exit(1)
    lines = []
    for raw in requirements_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def get_installed_packages() -> Dict[str, str]:
    # Use pip list to avoid extra dependencies
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    if result.returncode != 0:
        print("Warning: failed to query installed packages; proceeding to install all requirements.")
        return {}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Warning: could not parse pip list output; proceeding to install all requirements.")
        return {}
    installed = {pkg["name"].lower(): pkg.get("version", "") for pkg in data}
    return installed


_NAME_SPLIT_RE = re.compile(r"[<>=!~]")


def extract_package_name(requirement: str) -> str:
    # Heuristic: take text up to first version/operator char
    m = _NAME_SPLIT_RE.search(requirement)
    return (requirement[: m.start()] if m else requirement).strip().lower()


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    # Ensure we're running inside project-local venv (.venv). If not, create and re-exec.
    venv_dir = project_root / ".venv"
    venv_python = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

    if not venv_dir.exists():
        print(f"Creating virtual environment at {venv_dir} ...")
        proc = subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
        if proc.returncode != 0:
            print("Error: failed to create virtual environment.")
            return proc.returncode

    # If current interpreter is not the venv interpreter, re-exec within venv
    if Path(sys.executable).resolve() != venv_python.resolve():
        script_path = Path(__file__).resolve()
        print(f"Re-executing under virtual environment: {venv_python}")
        os.execv(str(venv_python), [str(venv_python), str(script_path), *sys.argv[1:]])

    req_path = project_root / "requirements.txt"
    requirements = read_requirements(req_path)

    installed = get_installed_packages()
    missing: List[str] = []

    for req in requirements:
        pkg_name = extract_package_name(req)
        if pkg_name and pkg_name in installed:
            continue
        missing.append(req)

    if "--check" in sys.argv:
        if not missing:
            print("All dependencies are already installed.")
        else:
            print("Missing dependencies that would be installed:")
            for item in missing:
                print(f"  - {item}")
        return 0

    if not missing:
        print("All dependencies already satisfied. Nothing to install.")
        return 0

    print("Installing missing dependencies (continuing on errors):")
    overall_rc = 0
    for item in missing:
        print(f"  - {item}")
        cmd = [sys.executable, "-m", "pip", "install", "--no-input", item]
        proc = subprocess.run(cmd)
        if proc.returncode != 0:
            print(f"Warning: failed to install {item}; skipping.")
            overall_rc = proc.returncode
    return overall_rc


if __name__ == "__main__":
    raise SystemExit(main())



"""Sync GitHub Actions Python matrix versions from pyproject classifiers."""

import re
import sys
import tomllib
from collections.abc import Mapping
from pathlib import Path

from ruamel.yaml import YAML


def load_classifiers(pyproject_path: Path) -> list[str]:
    """
    Extract Python version classifiers from pyproject.toml.

    Parameters
    ----------
    pyproject_path : Path
        Path to the pyproject.toml file.

    Returns
    -------
    list[str]
        Sorted unique Python versions like "3.12".

    """
    if not pyproject_path.exists():
        raise FileNotFoundError(f"Missing {pyproject_path}")
    data = pyproject_path.read_text(encoding="utf-8")
    project = tomllib.loads(data).get("project", {})
    classifiers = project.get("classifiers", [])
    versions = []
    for item in classifiers:
        match = re.search(r"Programming Language :: Python :: (\d+\.\d+)", item)
        if match:
            versions.append(match.group(1))
    versions = sorted(set(versions), key=float)
    if not versions:
        raise ValueError("No Python classifiers found in pyproject.toml")
    return versions


def update_workflow(path: Path, versions: list[str]) -> bool:
    """
    Update a workflow matrix to match the provided Python versions.

    Parameters
    ----------
    path : Path
        Workflow YAML/YML file to update.
    versions : list[str]
        Python versions to set in matrix entries.

    Returns
    -------
    bool
        True if the file was modified.

    """
    yaml = YAML()
    yaml.preserve_quotes = True
    data = yaml.load(path.read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        return False
    jobs = data.get("jobs", {})
    if not isinstance(jobs, Mapping):
        return False
    changed = False
    for job in jobs.values():
        strategy = job.get("strategy", {}) if isinstance(job, Mapping) else {}
        matrix = strategy.get("matrix", {}) if isinstance(strategy, Mapping) else {}
        if not isinstance(matrix, dict):
            continue
        for key in list(matrix.keys()):
            if re.search(r"python.*version", key):
                if matrix.get(key) != versions:
                    matrix[key] = versions
                    changed = True
    if changed:
        yaml.dump(data, path)
    return changed


def run() -> int:
    """Run the workflow matrix synchronization."""
    versions = load_classifiers(Path("pyproject.toml"))
    paths = [Path(p) for p in sys.argv[1:] if p.endswith((".yml", ".yaml"))]
    if not paths:
        print("No workflow YAML paths provided.")
        return 0
    for path in paths:
        update_workflow(path, versions)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

#!/usr/bin/env python3
"""Aggregate build manifests into a single file."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def get_git_sha() -> str:
    """Return the current Git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover - fatal path
        raise SystemExit(f"Failed to determine git SHA: {exc}") from exc
    return result.stdout.strip()


def load_build_manifests(dist_dir: Path) -> List[Dict]:
    """Load all manifest.json files under dist/*/manifest.json."""
    builds: List[Dict] = []
    for manifest_path in sorted(dist_dir.glob("*/manifest.json")):
        with manifest_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and "builds" in data:
            items = data.get("builds") or []
            if not isinstance(items, list):  # pragma: no cover - defensive
                raise SystemExit(
                    f"Manifest {manifest_path} has a non-list 'builds' entry"
                )
            builds.extend(items)
        elif isinstance(data, list):
            builds.extend(data)
        elif isinstance(data, dict):
            builds.append(data)
        else:  # pragma: no cover - defensive
            raise SystemExit(f"Unsupported manifest format in {manifest_path}")
    return builds


def ensure_unique_names(builds: List[Dict], sha: str) -> None:
    """Ensure all builds have unique names by appending short SHA on collisions."""
    seen: Dict[str, int] = {}
    short_sha = sha[:7]
    for build in builds:
        name = build.get("name")
        if not name:
            continue
        count = seen.get(name, 0)
        if count == 0:
            seen[name] = 1
            continue
        # Collision detected; append the short SHA and, if necessary, an index.
        new_name = f"{name}-{short_sha}"
        while new_name in seen:
            count += 1
            new_name = f"{name}-{short_sha}-{count}"
        build["name"] = new_name
        seen[new_name] = 1
        seen[name] = count + 1


DEFAULT_DIST_DIR = Path("dist")


def main() -> None:
    dist_dir = DEFAULT_DIST_DIR
    dist_dir.mkdir(parents=True, exist_ok=True)

    builds = load_build_manifests(dist_dir)
    git_sha = get_git_sha()

    ensure_unique_names(builds, git_sha)

    aggregate = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha,
        "builds": builds,
    }

    output_path = dist_dir / "manifest.json"
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(aggregate, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()

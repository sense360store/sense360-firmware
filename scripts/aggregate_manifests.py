#!/usr/bin/env python3
"""Aggregate ESPHome manifest metadata from built firmware outputs.

This script searches the provided distribution directory (``dist`` by default)
for per-device ``manifest.json`` files and produces a single aggregated
manifest at ``<dist>/manifest.json``. The aggregated file contains a timestamp
and ensures each entry also exposes its relative distribution path.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


@dataclass
class ManifestEntry:
    path: Path
    content: dict

    @property
    def distribution(self) -> str:
        """Return the directory name that holds the manifest."""
        return self.path.parent.name


def find_manifests(dist_root: Path) -> Iterable[ManifestEntry]:
    for manifest_path in sorted(dist_root.glob("*/manifest.json")):
        if manifest_path.is_file():
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            yield ManifestEntry(path=manifest_path, content=data)


def aggregate_manifests(entries: List[ManifestEntry]) -> dict:
    if not entries:
        raise SystemExit(
            "No manifest.json files found in the distribution directory; "
            "ensure the build job produced firmware outputs before publishing."
        )

    aggregated = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "builds": [],
    }

    for entry in entries:
        payload = dict(entry.content)
        payload.setdefault("distribution", entry.distribution)
        aggregated["builds"].append(payload)

    return aggregated


def main() -> None:
    dist_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
    if not dist_root.exists():
        raise SystemExit(
            f"Distribution directory '{dist_root}' does not exist; nothing to aggregate."
        )

    manifests = list(find_manifests(dist_root))
    aggregated = aggregate_manifests(manifests)

    output_path = dist_root / "manifest.json"
    output_path.write_text(json.dumps(aggregated, indent=2), encoding="utf-8")
    print(f"Aggregated {len(manifests)} manifest(s) into {output_path}")


if __name__ == "__main__":
    main()

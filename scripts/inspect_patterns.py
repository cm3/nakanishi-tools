#!/usr/bin/env python3
"""Show how the three sample Manifests group Image API services."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "manifests" / "NAKANISHI_0209"


def v2_ranges(manifest: dict) -> list[dict]:
    canvases = {
        canvas["@id"]: canvas
        for canvas in manifest["sequences"][0]["canvases"]
    }
    groups = []
    for side_range in manifest["structures"][1:]:
        groups.append({
            "view": side_range["label"],
            "services": [
                canvases[canvas_id]["images"][0]["resource"]["service"]["@id"]
                for canvas_id in side_range["canvases"]
            ],
        })
    return groups


def v3_ranges(manifest: dict) -> list[dict]:
    canvases = {canvas["id"]: canvas for canvas in manifest["items"]}
    groups = []
    for side_range in manifest["structures"][0]["items"]:
        groups.append({
            "view": side_range["label"]["ja"][0],
            "services": [
                canvases[canvas["id"]]["items"][0]["items"][0]["body"]["service"][0]["id"]
                for canvas in side_range["items"]
            ],
        })
    return groups


def v3_choice(manifest: dict) -> list[dict]:
    groups = []
    for canvas in manifest["items"]:
        choices = canvas["items"][0]["items"][0]["body"]["items"]
        groups.append({
            "view": canvas["label"]["ja"][0],
            "services": [choice["service"][0]["id"] for choice in choices],
        })
    return groups


def main() -> None:
    patterns = [
        ("v2-ranges", "manifest.json", v2_ranges),
        ("v3-ranges", "manifest-v3-ranges.json", v3_ranges),
        ("v3-choice", "manifest-v3-choice.json", v3_choice),
    ]
    for name, filename, extract in patterns:
        manifest = json.loads((ROOT / filename).read_text(encoding="utf-8"))
        groups = extract(manifest)
        print(f"{name}: " + ", ".join(
            f"{group['view']}={len(group['services'])}画像" for group in groups
        ))
        for group in groups:
            for service in group["services"]:
                print(f"  {group['view']}\t{service}")


if __name__ == "__main__":
    main()

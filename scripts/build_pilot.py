#!/usr/bin/env python3
"""Build a Presentation 2 pilot Manifest from one NIHU registration CSV row."""

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import quote, unquote
from urllib.request import urlopen


MODALITIES = ["VL", "IR", "UVF", "PLwDL", "PLwoDL"]
SIDES = {"Front": "表面", "Back": "裏面"}
IMAGE_API = "https://iiif.nihu.jp/iiif/2"


def read_record(path: Path, identifier: str) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["field_identifier"] == identifier]
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one {identifier} row, found {len(rows)}")
    return rows[0]


def image_entry(encoded_path: str, dirname: str) -> dict:
    relative_path = unquote(encoded_path)
    parts = relative_path.split("/")
    if len(parts) != 3 or parts[1] not in SIDES:
        raise ValueError(f"Unexpected image path: {relative_path}")
    filename = parts[2]
    modality = next((code for code in MODALITIES if filename.endswith(f"_{code}.tif")), None)
    if modality is None:
        raise ValueError(f"Unknown imaging modality: {relative_path}")
    service_id = f"{IMAGE_API}/{quote(dirname + '/' + relative_path, safe='')}"
    with urlopen(f"{service_id}/info.json", timeout=20) as response:
        info = json.load(response)
    if info.get("@id") != service_id:
        raise ValueError(f"Unexpected Image API identifier: {info.get('@id')}")
    width, height = int(info["width"]), int(info["height"])
    scale = min(1.0, 3000 / width, 3000 / height)
    return {
        "path": relative_path,
        "side": parts[1],
        "modality": modality,
        "service_id": service_id,
        "image_url": f"{service_id}/full/!3000,3000/0/default.jpg",
        "width": round(width * scale),
        "height": round(height * scale),
        "source_width": width,
        "source_height": height,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--base-url", required=True, help="Published site URL, without trailing slash")
    parser.add_argument("--identifier", default="NAKANISHI_0209")
    parser.add_argument("--output", type=Path, default=Path("manifests/NAKANISHI_0209"))
    args = parser.parse_args()

    record = read_record(args.csv, args.identifier)
    paths = [value.strip() for value in record["field_filepath"].split(",") if value.strip()]
    if not paths:
        raise ValueError("field_filepath is empty")
    dirname = record["field_image_dirname"].strip()
    if not dirname:
        raise ValueError("field_image_dirname is empty")
    images = [image_entry(path, dirname) for path in paths]
    if len({image["service_id"] for image in images}) != len(images):
        raise ValueError("Duplicate image service ID")

    base = f"{args.base_url.rstrip('/')}/manifests/{args.identifier}"
    canvases = []
    image_rows = []
    for side in SIDES:
        side_images = [image for image in images if image["side"] == side]
        side_images.sort(key=lambda image: MODALITIES.index(image["modality"]))
        for image in side_images:
            canvas_id = f"{base}/canvas/{side.lower()}-{image['modality'].lower()}"
            resource = {
                "@id": image["image_url"],
                "@type": "dctypes:Image",
                "format": "image/jpeg",
                "label": image["modality"],
                "width": image["width"],
                "height": image["height"],
                "service": {
                    "@context": "http://iiif.io/api/image/2/context.json",
                    "@id": image["service_id"],
                    "profile": "http://iiif.io/api/image/2/level2.json",
                },
            }
            canvases.append({
                "@id": canvas_id,
                "@type": "sc:Canvas",
                "label": f"{SIDES[side]}・{image['modality']}",
                "width": image["width"],
                "height": image["height"],
                "metadata": [
                    {"label": "撮影対象", "value": SIDES[side]},
                    {"label": "撮影方式", "value": image["modality"]},
                ],
                "images": [{
                    "@id": f"{base}/annotation/{side.lower()}-{image['modality'].lower()}",
                    "@type": "oa:Annotation",
                    "motivation": "sc:painting",
                    "on": canvas_id,
                    "resource": resource,
                }],
            })
            image_rows.append({
                "canvas_id": canvas_id,
                "image_service_id": image["service_id"],
                "path": image["path"],
                "view_id": side.lower(),
                "modality_code": image["modality"],
                "is_default": image["modality"] == "VL",
            })

    manifest = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": f"{base}/manifest.json",
        "@type": "sc:Manifest",
        "label": record["field_title"] or record["title"],
        "metadata": [
            {"label": "資料ID", "value": record["field_identifier"]},
            {"label": "撮影画像", "value": "表裏と撮影方式を各Canvasのラベルに示します"},
        ],
        "seeAlso": {
            "@id": f"{base}/images.json",
            "format": "application/json",
        },
        "sequences": [{
            "@id": f"{base}/sequence/normal",
            "@type": "sc:Sequence",
            "label": "表面・裏面",
            "canvases": canvases,
        }],
        "structures": [
            {
                "@id": f"{base}/range/top",
                "@type": "sc:Range",
                "label": "撮影対象",
                "viewingHint": "top",
                "ranges": [f"{base}/range/{side.lower()}" for side in SIDES],
            },
            *[
                {
                    "@id": f"{base}/range/{side.lower()}",
                    "@type": "sc:Range",
                    "label": SIDES[side],
                    "canvases": [
                        canvas["@id"] for canvas in canvases
                        if canvas["@id"].split("/canvas/")[-1].startswith(side.lower() + "-")
                    ],
                }
                for side in SIDES
            ],
        ],
    }
    mapping = {
        "schema_version": 1,
        "object_id": record["field_identifier"],
        "manifest_id": manifest["@id"],
        "images": image_rows,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in [("manifest.json", manifest), ("images.json", mapping)]:
        (args.output / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"Wrote {len(canvases)} canvases and {len(images)} images to {args.output}")


if __name__ == "__main__":
    main()

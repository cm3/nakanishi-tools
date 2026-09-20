#!/usr/bin/env python3
"""Build Image API 3 / Presentation 3 Choice manifests for the nine NIHU records."""

import argparse
import csv
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote, unquote
from urllib.request import urlopen


IMAGE_API = "https://iiif.nihu.jp/iiif/3"
MANIFEST_NAME = "manifest-v3-choice-image3.json"
MAPPING_NAME = "images-v3-choice-image3.json"
COLLECTION_NAME = "nakanishi-v3-choice-image3.json"
MODALITIES = ["VL", "PLwDL", "PLwoDL", "IR", "UVF"]
MODALITY_LABELS = {
    "VL": "可視光",
    "PLwDL": "正面反射光あり",
    "PLwoDL": "正面反射光除去",
    "IR": "赤外光",
    "UVF": "紫外蛍光",
}
VIEW_LABELS = {"Front": "表面", "Back": "裏面"}

# Source-file exceptions confirmed for the nine-record collection.
MODALITY_OVERRIDES = {
    "164/001/164_001_VLwoDL.tif": ("PLwoDL", "VLwoDL"),
    "213/02/213_02.tif": ("IR", "方式コードなし（撮影標識のIRから判定）"),
}


def language(ja: str, en: str | None = None) -> dict[str, list[str]]:
    value = {"ja": [ja]}
    if en:
        value["en"] = [en]
    return value


def read_records(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []
    if len(rows) != 9:
        raise ValueError(f"Expected nine records, found {len(rows)}")
    return fields, rows


def parse_modality(relative_path: str) -> tuple[str, str | None]:
    if relative_path in MODALITY_OVERRIDES:
        return MODALITY_OVERRIDES[relative_path]
    filename = relative_path.rsplit("/", 1)[-1]
    for code in MODALITIES:
        if filename.endswith(f"_{code}.tif"):
            return code, None
    raise ValueError(f"Unknown imaging modality: {relative_path}")


def read_image(encoded_path: str, dirname: str) -> dict:
    relative_path = unquote(encoded_path)
    parts = relative_path.split("/")
    if len(parts) != 3:
        raise ValueError(f"Unexpected image path: {relative_path}")
    modality, source_note = parse_modality(relative_path)
    service_id = f"{IMAGE_API}/{quote(dirname + '/' + relative_path, safe='')}"
    with urlopen(f"{service_id}/info.json", timeout=30) as response:
        info = json.load(response)
    if info.get("id") != service_id or info.get("type") != "ImageService3":
        raise ValueError(f"Unexpected Image API 3 response: {relative_path}")
    if info.get("profile") != "level2":
        raise ValueError(f"Expected Image API level2: {relative_path}")
    source_width, source_height = int(info["width"]), int(info["height"])
    scale = min(1.0, 3000 / source_width, 3000 / source_height)
    return {
        "path": relative_path,
        "view_id": parts[1],
        "modality": modality,
        "source_note": source_note,
        "service_id": service_id,
        "image_url": f"{service_id}/full/!3000,3000/0/default.jpg",
        "width": round(source_width * scale),
        "height": round(source_height * scale),
        "source_width": source_width,
        "source_height": source_height,
    }


def service(image: dict) -> dict:
    return {"id": image["service_id"], "type": "ImageService3", "profile": "level2"}


def thumbnail(image: dict) -> dict:
    return {
        "id": f"{image['service_id']}/full/200,/0/default.jpg",
        "type": "Image",
        "format": "image/jpeg",
        "width": 200,
        "height": round(image["source_height"] * 200 / image["source_width"]),
        "service": [service(image)],
    }


def choice_image(image: dict) -> dict:
    result = {
        "id": image["image_url"],
        "type": "Image",
        "format": "image/jpeg",
        "label": language(MODALITY_LABELS[image["modality"]], image["modality"]),
        "width": image["width"],
        "height": image["height"],
        "thumbnail": [thumbnail(image)],
        "service": [service(image)],
    }
    if image["source_note"]:
        result["metadata"] = [{
            "label": language("元ファイルの方式表記"),
            "value": language(image["source_note"]),
        }]
    return result


def build_manifest(record: dict[str, str], images: list[dict], site_url: str) -> tuple[dict, dict]:
    identifier = record["field_identifier"]
    root = f"{site_url.rstrip('/')}/manifests/{identifier}"
    resource_base = f"{root}/v3-choice-image3"
    view_ids = list(dict.fromkeys(image["view_id"] for image in images))
    canvases = []
    mapping_rows = []
    for view_id in view_ids:
        choices = sorted(
            (image for image in images if image["view_id"] == view_id),
            key=lambda image: MODALITIES.index(image["modality"]),
        )
        if len({image["modality"] for image in choices}) != len(choices):
            raise ValueError(f"Duplicate modality in {identifier}/{view_id}")
        default = next((image for image in choices if image["modality"] == "VL"), choices[0])
        slug = view_id.lower()
        canvas_id = f"{resource_base}/canvas/{slug}"
        canvases.append({
            "id": canvas_id,
            "type": "Canvas",
            "label": language(VIEW_LABELS.get(view_id, f"撮影面 {view_id}")),
            "width": max(image["width"] for image in choices),
            "height": max(image["height"] for image in choices),
            "thumbnail": [thumbnail(default)],
            "items": [{
                "id": f"{resource_base}/page/{slug}",
                "type": "AnnotationPage",
                "items": [{
                    "id": f"{resource_base}/annotation/{slug}",
                    "type": "Annotation",
                    "motivation": "painting",
                    "body": {"type": "Choice", "items": [choice_image(image) for image in choices]},
                    "target": canvas_id,
                }],
            }],
        })
        mapping_rows.extend({
            "canvas_id": canvas_id,
            "view_id": view_id,
            "modality_code": image["modality"],
            "image_service_id": image["service_id"],
            "source_path": image["path"],
            "source_modality_note": image["source_note"],
            "is_default": image is default,
        } for image in choices)

    manifest = {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": f"{root}/{MANIFEST_NAME}",
        "type": "Manifest",
        "label": language(record["field_title"] or record["title"]),
        "metadata": [{
            "label": language("資料ID"),
            "value": language(identifier),
        }],
        "thumbnail": canvases[0]["thumbnail"],
        "items": canvases,
    }
    mapping = {
        "schema_version": 1,
        "object_id": identifier,
        "manifest_id": manifest["id"],
        "note": "Choice Manifestの検証・一覧処理用索引。Manifestからは参照しない。",
        "images": mapping_rows,
    }
    return manifest, mapping


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--site-url", default="https://cm3.github.io/nakanishi-tools")
    parser.add_argument("--output-root", type=Path, default=Path("manifests"))
    parser.add_argument(
        "--collection-output",
        type=Path,
        default=Path("collections") / COLLECTION_NAME,
    )
    parser.add_argument("--registration-output", type=Path)
    args = parser.parse_args()

    fields, records = read_records(args.csv)
    jobs = []
    for record in records:
        paths = [value.strip() for value in record["field_filepath"].split(",") if value.strip()]
        dirname = record["field_image_dirname"].strip()
        if not paths or not dirname:
            raise ValueError(f"Missing image paths or directory: {record['field_identifier']}")
        jobs.extend((record["field_identifier"], path, dirname) for path in paths)
    with ThreadPoolExecutor(max_workers=8) as executor:
        loaded = list(executor.map(lambda job: (job[0], read_image(job[1], job[2])), jobs))

    by_identifier: dict[str, list[dict]] = {}
    for identifier, image in loaded:
        by_identifier.setdefault(identifier, []).append(image)

    registration_rows = []
    collection_items = []
    total_images = 0
    for record in records:
        identifier = record["field_identifier"]
        images = by_identifier[identifier]
        manifest, mapping = build_manifest(record, images, args.site_url)
        output = args.output_root / identifier
        write_json(output / MANIFEST_NAME, manifest)
        write_json(output / MAPPING_NAME, mapping)
        collection_items.append({
            "id": manifest["id"],
            "type": "Manifest",
            "label": manifest["label"],
            "thumbnail": manifest["thumbnail"],
        })
        total_images += len(images)

        registration = record.copy()
        registration["field_manifest"] = manifest["id"]
        registration["field_source"] = manifest["thumbnail"][0]["id"]
        registration_rows.append(registration)

    collection = {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": f"{args.site_url.rstrip('/')}/collections/{COLLECTION_NAME}",
        "type": "Collection",
        "label": language("中西コレクション IIIF マニフェスト実験"),
        "summary": language(
            "同一資料の別撮影画像をChoiceで表現した、9資料のIIIF Presentation 3 Manifest一覧"
        ),
        "items": collection_items,
    }
    write_json(args.collection_output, collection)

    if args.registration_output:
        args.registration_output.parent.mkdir(parents=True, exist_ok=True)
        with args.registration_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\r\n")
            writer.writeheader()
            writer.writerows(registration_rows)

    print(f"Wrote {len(records)} Choice manifests for {total_images} Image API 3 images")


if __name__ == "__main__":
    main()

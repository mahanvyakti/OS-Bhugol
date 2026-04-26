#!/usr/bin/env python3
"""Build homepage data manifest and municipality map GeoJSON for OS-Bhugol."""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from shapely.geometry import GeometryCollection, MultiPolygon, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

REPO_URL = "https://github.com/mahanvyakti/OS-Bhugol"
RAW_BASE = "https://raw.githubusercontent.com/mahanvyakti/OS-Bhugol/main"
KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}


@dataclass
class MunicipalityInput:
    state: str
    district: str
    slug: str
    root: Path


def slug_to_title(slug: str) -> str:
    return re.sub(r"\s+", " ", slug.replace("-", " ")).strip().title()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def discover_municipalities(repo_root: Path) -> list[MunicipalityInput]:
    data_root = repo_root / "data" / "india"
    discovered: list[MunicipalityInput] = []

    for state_dir in sorted(data_root.iterdir()):
        if not state_dir.is_dir():
            continue
        for district_dir in sorted((state_dir / "districts").glob("*")):
            if not district_dir.is_dir():
                continue
            municipalities_root = district_dir / "municipalities"
            if not municipalities_root.is_dir():
                continue
            for municipality_dir in sorted(municipalities_root.glob("*")):
                if municipality_dir.is_dir():
                    discovered.append(
                        MunicipalityInput(
                            state=state_dir.name,
                            district=district_dir.name,
                            slug=municipality_dir.name,
                            root=municipality_dir,
                        )
                    )

    return discovered


def relative_repo_path(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def repo_blob_url(path: str) -> str:
    return f"{REPO_URL}/blob/main/{path}"


def repo_raw_url(path: str) -> str:
    return f"{RAW_BASE}/{path}"


def extract_geojson_geometry(geojson_path: Path) -> BaseGeometry:
    payload = load_json(geojson_path)
    gtype = payload.get("type")

    if gtype == "FeatureCollection":
        geometries = []
        for feature in payload.get("features", []):
            geometry = feature.get("geometry")
            if geometry:
                geometries.append(shape(geometry))
        if not geometries:
            raise ValueError(f"No geometries found in {geojson_path}")
        return unary_union(geometries)

    if gtype == "Feature":
        return shape(payload["geometry"])

    return shape(payload)


def extract_kml_geometry(kml_path: Path) -> BaseGeometry:
    tree = ET.parse(kml_path)
    root = tree.getroot()
    polygons: list[BaseGeometry] = []

    for polygon_node in root.findall(".//kml:Polygon", KML_NS):
        coord_node = polygon_node.find(".//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", KML_NS)
        if coord_node is None or not coord_node.text:
            continue

        coords: list[tuple[float, float]] = []
        for point in coord_node.text.strip().split():
            values = point.split(",")
            if len(values) < 2:
                continue
            lon = float(values[0])
            lat = float(values[1])
            coords.append((lon, lat))

        if len(coords) >= 4 and coords[0] != coords[-1]:
            coords.append(coords[0])

        if len(coords) >= 4:
            polygons.append(shape({"type": "Polygon", "coordinates": [coords]}))

    if not polygons:
        raise ValueError(f"No polygon geometry found in {kml_path}")

    return unary_union(polygons)


def choose_wards_geojson(root: Path, meta: dict[str, Any] | None) -> Path | None:
    preferred: list[Path] = []

    if meta and isinstance(meta.get("data_files"), dict):
        for entry in meta["data_files"].values():
            if isinstance(entry, dict) and isinstance(entry.get("geojson"), str):
                candidate = root / entry["geojson"]
                if candidate.is_file() and "ward" in candidate.as_posix().lower():
                    preferred.append(candidate)

    for candidate in sorted(root.rglob("wards.geojson")):
        if "sources" not in candidate.parts:
            preferred.append(candidate)

    unique: list[Path] = []
    seen = set()
    for item in preferred:
        resolved = str(item.resolve())
        if resolved not in seen:
            seen.add(resolved)
            unique.append(item)

    if unique:
        unique.sort(key=lambda p: ("/wards/" not in p.as_posix(), len(p.parts)))
        return unique[0]

    return None


def collect_ward_files(root: Path) -> list[str]:
    ward_files: set[Path] = set()
    for path in root.rglob("*.geojson"):
        lower_name = path.name.lower()
        posix = path.as_posix().lower()
        if lower_name == "wards.geojson" and "sources" not in posix:
            ward_files.add(path)
    for path in root.rglob("*.kml"):
        lower_name = path.name.lower()
        posix = path.as_posix().lower()
        if lower_name == "wards.kml" and "sources" not in posix:
            ward_files.add(path)
    return sorted(p.as_posix() for p in ward_files)


def ensure_polygonal(geometry: BaseGeometry) -> BaseGeometry:
    if geometry.is_empty:
        raise ValueError("Geometry is empty")

    if isinstance(geometry, (MultiPolygon,)) or geometry.geom_type == "Polygon":
        return geometry

    if geometry.geom_type == "GeometryCollection":
        polygons = [g for g in geometry.geoms if g.geom_type in {"Polygon", "MultiPolygon"}]
        if not polygons:
            raise ValueError("No polygonal geometry found in collection")
        return unary_union(polygons)

    raise ValueError(f"Unsupported geometry type: {geometry.geom_type}")


def ward_count_from_meta(meta: dict[str, Any] | None) -> int | None:
    if not meta:
        return None
    units = meta.get("units")
    if not isinstance(units, dict):
        return None
    counts = [value for key, value in units.items() if "ward" in key and isinstance(value, int)]
    if not counts:
        return None
    return max(counts)


def municipality_payload(item: MunicipalityInput, repo_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root = item.root
    meta_path = root / "_meta.json"
    meta = load_json(meta_path) if meta_path.is_file() else None

    boundary_geojson = root / "boundary.geojson"
    boundary_kml = root / "boundary.kml"

    geometry_source = ""
    geometry: BaseGeometry
    geometry_path: str
    boundary_path: str | None = None

    if boundary_geojson.is_file():
        geometry_source = "boundary"
        geometry = extract_geojson_geometry(boundary_geojson)
        geometry_path = relative_repo_path(boundary_geojson, repo_root)
        boundary_path = geometry_path
    elif boundary_kml.is_file():
        geometry_source = "boundary"
        geometry = extract_kml_geometry(boundary_kml)
        geometry_path = relative_repo_path(boundary_kml, repo_root)
        boundary_path = geometry_path
    else:
        wards_geojson = choose_wards_geojson(root, meta)
        if not wards_geojson:
            raise ValueError(f"No boundary or wards geometry found for {root}")
        geometry_source = "dissolved_wards"
        geometry = extract_geojson_geometry(wards_geojson)
        geometry_path = relative_repo_path(wards_geojson, repo_root)

    geometry = ensure_polygonal(geometry)
    centroid = geometry.centroid

    source_files = sorted(
        relative_repo_path(path, repo_root)
        for path in (root / "sources").rglob("*")
        if path.is_file()
    )

    ward_paths = sorted(
        relative_repo_path(Path(path), repo_root)
        for path in collect_ward_files(root)
    )

    state_title = slug_to_title(item.state)
    district_title = slug_to_title(item.district)

    municipality_name = (
        (meta or {}).get("name")
        or slug_to_title(item.slug)
    )

    municipality_id = f"{item.state}-{item.district}-{item.slug}"
    root_rel = relative_repo_path(root, repo_root)
    all_files = [path for path in root.rglob("*") if path.is_file()]

    formats = []
    if any(path.suffix.lower() == ".geojson" for path in all_files):
        formats.append("GeoJSON")
    if any(path.suffix.lower() == ".kml" for path in all_files):
        formats.append("KML")

    manifest_entry: dict[str, Any] = {
        "id": municipality_id,
        "slug": item.slug,
        "name": municipality_name,
        "name_local": (meta or {}).get("name_local"),
        "type": (meta or {}).get("type", "municipality"),
        "state": state_title,
        "district": district_title,
        "paths": {
            "root": root_rel,
            "meta": relative_repo_path(meta_path, repo_root) if meta_path.is_file() else None,
            "boundary": boundary_path,
            "wards": ward_paths,
            "sources": source_files,
        },
        "map": {
            "geometry_source": geometry_source,
            "geometry_path": geometry_path,
            "centroid": {
                "lat": round(float(centroid.y), 6),
                "lng": round(float(centroid.x), 6),
            },
        },
        "stats": {
            "ward_count": ward_count_from_meta(meta),
            "file_count": len(all_files),
            "formats_available": formats,
        },
        "last_updated": (meta or {}).get("last_updated"),
        "links": {
            "folder": repo_blob_url(root_rel),
            "meta": repo_blob_url(relative_repo_path(meta_path, repo_root)) if meta_path.is_file() else None,
            "geometry_raw": repo_raw_url(geometry_path),
        },
    }

    map_feature: dict[str, Any] = {
        "type": "Feature",
        "properties": {
            "id": municipality_id,
            "name": municipality_name,
            "state": state_title,
            "district": district_title,
            "geometry_source": geometry_source,
            "last_updated": (meta or {}).get("last_updated"),
        },
        "geometry": geometry.__geo_interface__,
    }

    return manifest_entry, map_feature


def build_payload(repo_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    municipalities = discover_municipalities(repo_root)
    manifest_entries: list[dict[str, Any]] = []
    map_features: list[dict[str, Any]] = []

    for municipality in municipalities:
        try:
            entry, feature = municipality_payload(municipality, repo_root)
            manifest_entries.append(entry)
            map_features.append(feature)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Skipping {municipality.root}: {exc}")

    manifest_entries.sort(key=lambda item: (item["state"], item["district"], item["name"]))

    manifest = {
        "version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "repo_url": REPO_URL,
        "municipalities": manifest_entries,
    }

    map_geojson = {
        "type": "FeatureCollection",
        "features": map_features,
    }

    return manifest, map_geojson


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build homepage index for OS-Bhugol")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--output-manifest", required=True, help="Output path for municipalities-index.json")
    parser.add_argument("--output-geojson", required=True, help="Output path for municipalities-map.geojson")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    manifest, geojson = build_payload(repo_root)

    dump_json(Path(args.output_manifest).resolve(), manifest)
    dump_json(Path(args.output_geojson).resolve(), geojson)

    print(f"Generated manifest entries: {len(manifest['municipalities'])}")
    print(f"Map features: {len(geojson['features'])}")


if __name__ == "__main__":
    main()


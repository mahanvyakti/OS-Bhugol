# Homepage Maintenance Guide

This document explains how to maintain the OS-Bhugol GitHub Pages homepage.

## 1. Architecture Overview

The homepage lives in `site/` as a React + Vite app.

- UI source code: `site/src/`
- Generated homepage data: `site/public/generated/`
- Data build script: `scripts/build_homepage_index.py`
- Deployment workflow: `.github/workflows/deploy-pages.yml`

The site does not hardcode municipality records. It reads generated JSON built from `data/`.

## 2. How New Geodata Is Picked Up

Run the index builder whenever data changes:

```bash
python scripts/build_homepage_index.py \
  --repo-root . \
  --output-manifest site/public/generated/municipalities-index.json \
  --output-geojson site/public/generated/municipalities-map.geojson
```

Discovery rule:

- Scans `data/india/*/districts/*/municipalities/*`

Map geometry rule:

1. Use `boundary.geojson` or `boundary.kml` if available.
2. Else dissolve ward polygons from ward GeoJSON (build-time fallback).
3. The map always renders municipality-level features only.

## 3. Data Conventions Required

Each municipality folder should follow:

- Optional but recommended municipality `_meta.json`
- Optional `boundary.geojson` or `boundary.kml`
- Ward files (`wards/wards.geojson` or similar)
- Optional `sources/` documents for verification

Recommended metadata fields in municipality `_meta.json`:

- `name`, `name_local`, `type`
- `parent` (`district`, `state`, `country`)
- `units` (ward counts)
- `last_updated`

## 4. Local Development

From repository root:

```bash
cd site
npm install
npm run build:data
npm run dev
```

Build production site:

```bash
npm run build
```

## 5. Deployment (GitHub Pages)

`deploy-pages.yml` builds and deploys on pushes to `main` when site/data/script files change.

- Builds generated data first
- Builds Vite app with base path `/OS-Bhugol/`
- Publishes `site/dist` to GitHub Pages

## 6. Troubleshooting Checklist

If map is empty:

- Confirm `site/public/generated/municipalities-map.geojson` exists.
- Ensure each municipality has either boundary geometry or usable ward GeoJSON.
- Check malformed geometry using `python scripts/validate.py data/`.

If directory links are broken:

- Verify manifest paths are relative to repo root.
- Run tests: `python -m unittest scripts/test_build_homepage_index.py`.

If build fails in CI:

- Ensure `scripts/requirements.txt` includes `shapely>=2.0.0`.
- Confirm Python + Node setup steps in workflow are unchanged.

## 7. Update Workflow for New Geodata

1. Add/modify geodata under `data/`.
2. Run validation (`scripts/validate.py`).
3. Rebuild homepage generated data (`build_homepage_index.py`).
4. Review map + directory locally (`npm run dev`).
5. Commit data + generated files together.

# Contributing to OS-Bhugol

Thank you for wanting to contribute! This guide explains how to add new geographic data.

---

## 🎯 What We're Looking For

### High Priority
1. **Municipal ward boundaries** — Any city in India
2. **Tehsil/taluka boundaries** — Sub-district divisions
3. **Electoral constituencies** — Lok Sabha, Vidhan Sabha, Local body

### Medium Priority
4. **District boundaries** (often already available, but we centralize)
5. **Village boundaries**
6. **Special zones** — SEZs, industrial areas, cantonment boards

---

## 📋 Quality Standards

### Accuracy Requirements
- **Source**: Must be traced from official government documents
- **Precision**: Reasonable accuracy — we're not surveying, but should match reality visually
- **Completeness**: All units in a set (e.g., all 16 wards in Parbhani Municipal Corporation, not just 10)
- **Topology**: Boundaries should align — no gaps or overlaps between adjacent units

### Metadata Requirements
Every data folder **must** include:
1. `_meta.json` with source attribution
2. Original source document in `sources/` folder (PDF, image, or link)

---

## 🛠️ How to Trace Boundaries

### Tools
1. **Google My Maps** — Easiest for beginners, exports to KML
2. **QGIS** — Professional GIS software, exports to GeoJSON
3. **geojson.io** — Quick online editor for simple shapes

### Process
1. Find official map (government website, RTI, or gazette)
2. Overlay on Google Maps/satellite imagery
3. Trace polygons carefully, following roads/landmarks as guides
4. Name each polygon consistently (e.g., "Ward 01", "Ward 02")
5. Export to GeoJSON (preferred) or KML

### Tips
- Use high zoom levels for accuracy
- Follow natural boundaries (rivers, roads) where visible
- Cross-reference multiple sources when possible
- Note any uncertainty in metadata

---

## 📁 Directory Structure

Place your data following this pattern:

```
data/india/{state}/districts/{district}/{entity_type}/{entity_name}/
```

Example:
```
data/india/maharashtra/districts/nanded/municipalities/nanded-waghala-city/
├── _meta.json
├── sources/
│   └── ward-delimitation-2019.pdf
├── boundary.geojson
└── wards/
    └── wards.geojson
```

---

## 📝 _meta.json Format

```json
{
  "name": "Parbhani Municipal Corporation",
  "name_local": "परभणी महानगरपालिका",
  "type": "municipal_corporation",
  "parent": {
    "district": "Parbhani",
    "state": "Maharashtra",
    "country": "India"
  },
  "units": {
    "wards": 16
  },
  "sources": [
    {
      "title": "Ward Delimitation Map",
      "type": "pdf",
      "file": "sources/ward-map-2024.pdf",
      "url": "https://parbhani.gov.in/wards",
      "accessed": "2024-01-15",
      "department": "Parbhani Municipal Corporation"
    }
  ],
  "contributors": ["@mahanvyakti"],
  "created": "2026-01-18",
  "last_updated": "2026-01-18",
  "notes": "Hand-traced from official ward delimitation PDF"
}
```

---

## 🔄 Pull Request Process

1. **Fork** the repository
2. **Create branch**: `git checkout -b add/nanded-wards`
3. **Add data** following the structure above
4. **Test**: Open your GeoJSON in geojson.io to verify it renders
5. **Commit**: Include source in commit message
6. **PR**: Reference the source document in your PR description

### PR Checklist
- [ ] Data placed in correct directory path
- [ ] `_meta.json` includes source attribution
- [ ] Original source document included
- [ ] GeoJSON/KML validates (no syntax errors)
- [ ] All units included (no missing wards)

---

## 🤔 Questions?

- Open a [GitHub Issue](https://github.com/mahanvyakti/OS-Bhugol/issues) for questions
- See existing data as examples of the expected format

---

*Thank you for helping make India's geographic data open!*

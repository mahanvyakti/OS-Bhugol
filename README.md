# OS-Bhugol (ओएस-भूगोल)

**Open Source Geographic Boundaries for India** — Starting with Maharashtra

> *Bhugol (भूगोल)* means "Geography" in Hindi/Marathi.

[![License: ODbL](https://img.shields.io/badge/License-ODbL-blue.svg)](https://opendatacommons.org/licenses/odbl/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🎯 Mission

Make **machine-readable geographic boundary data** freely available for Indian administrative divisions — from states down to municipal wards — in formats developers can actually use.

Government data exists, but often only as PDFs, images, or locked portals. **OS-Bhugol bridges this gap** by providing clean, attributed, open-licensed GeoJSON/KML files.

---

## 🚨 The Problem

| What Government Provides | What Developers Need |
|--------------------------|----------------------|
| Ward maps in PDF/JPEG | GeoJSON/KML polygons |
| Data behind login portals | Raw downloadable files |
| Scattered across 50+ portals | Centralized repository |
| No version history | Git-tracked, auditable |
| Unclear licensing | Clear open license |

**This repository solves this.**

---

## 📊 Current Coverage

| State | District | Entity | Status |
|-------|----------|--------|--------|
| Maharashtra | Parbhani | Municipal Corporation Wards (16) | ✅ Complete |

---

## 📁 Repository Structure

```
OS-Bhugol/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
│
└── data/
    └── india/
        └── maharashtra/
            └── districts/
                └── parbhani/
                    ├── _meta.json              # District metadata
                    └── municipalities/
                        └── parbhani-municipal-corporation/
                            ├── _meta.json      # Municipality metadata  
                            ├── sources/        # Original PDFs/images
                            │   └── mahanagar_palika_prabhag_rachna_map.jpg
                            ├── boundary.geojson
                            └── wards/
                                ├── wards.kml   # All wards combined
                                └── wards.geojson
```

---

## 🔧 Data Formats

| Format | Primary Use | Support |
|--------|-------------|---------|
| **GeoJSON** | Web apps (Leaflet, Mapbox, D3.js) | ✅ Primary |
| **KML** | Google Earth, desktop GIS | ✅ Secondary |
| **Shapefile** | Legacy GIS software | 🔜 On request |

Each data file is accompanied by:
- **`_meta.json`** — Source attribution, last updated, contributor info
- **`sources/`** — Original government documents for verification

---

## 💡 Use Cases

### For Developers
- **Election dashboards** — Visualize results by ward/constituency
- **Census analysis** — Overlay demographic data on boundaries
- **Hyperlocal apps** — "Which ward am I in?" functionality
- **Civic tech** — Complaint tracking, service mapping by area

> Sky is the limit for what can be done with this data!

### For Journalists & Researchers
- **Investigation mapping** — Geographic analysis of stories
- **Academic research** — Urban planning, political science, demography
- **Data journalism** — Interactive maps for stories

### For Government & NGOs
- **Quick prototyping** — Build dashboards without recreating boundaries
- **Cross-department data** — Standardized geography for interoperability
- **Field surveys** — Pre-loaded boundaries for data collection apps

### For Education
- **GIS training** — Real Indian data for students
- **Geography education** — Interactive local maps

---

## 🚀 Quick Start

### Use with Leaflet.js
```javascript
fetch('https://raw.githubusercontent.com/mahanvyakti/OS-Bhugol/main/data/india/maharashtra/districts/parbhani/municipalities/parbhani-municipal-corporation/wards/wards.geojson')
  .then(response => response.json())
  .then(data => {
    L.geoJSON(data).addTo(map);
  });
```

### Use with Python
```python
import geopandas as gpd

wards = gpd.read_file('data/india/maharashtra/districts/parbhani/municipalities/parbhani-municipal-corporation/wards/wards.geojson')
wards.plot()
```

### Download and Open in QGIS
1. Clone: `git clone https://github.com/mahanvyakti/OS-Bhugol.git`
2. Open QGIS → Layer → Add Layer → Add Vector Layer
3. Select any `.geojson` or `.kml` file

---

## 🤝 Contributing

We need help expanding coverage! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to trace boundaries from official maps
- Data quality standards
- Metadata requirements

### Priority Areas
- [ ] Other cities in Maharashtra (Nanded, Latur, Chhatrapati Sambhajinagar)
- [ ] Tehsil boundaries
- [ ] Vidhan Sabha constituencies

---

## 📜 Data Sources & Attribution

All data is traced from **official government sources**. Each `_meta.json` file contains:
- Source document URL or description
- Date accessed
- Government department name
- Any known caveats

**We do not claim copyright** over the underlying geographic facts. Our contribution is the digitization effort and organization.

---

## ⚖️ License

This database is made available under the **Open Database License (ODbL)**. See [LICENSE](LICENSE) for details.

- ✅ Free to use, modify, share
- ✅ Commercial use allowed
- ⚠️ Attribution required
- ⚠️ Share-alike for derivative databases

---

## 🌟 Acknowledgments

- **DataMeet** — Inspiration from India's open data community
- **OpenStreetMap India** — Complementary efforts in mapping
- **NIC & Survey of India** — Original source data

---

## 📬 Contact

- **Maintainer**: [Rajan Gaul](https://github.com/mahanvyakti)
- **Issues**: [GitHub Issues](https://github.com/mahanvyakti/OS-Bhugol/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mahanvyakti/OS-Bhugol/discussions)

---

<p align="center">
  <i>Making India's geography truly open, one boundary at a time.</i>
</p>

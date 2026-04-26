import { useEffect, useMemo, useRef } from "react";
import L from "leaflet";

const LIGHT_TILE = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";
const DARK_TILE = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
const TILE_ATTRIBUTION = '&copy; OpenStreetMap contributors &copy; CARTO';

export default function MapPanel({ mapData, municipalities, selectedId, onSelect, selectedMunicipality, theme }) {
  const mapHostRef = useRef(null);
  const mapRef = useRef(null);
  const tileRef = useRef(null);
  const geoLayerRef = useRef(null);
  const layerByIdRef = useRef(new Map());
  const allBoundsRef = useRef(null);

  useEffect(() => {
    if (!mapHostRef.current || mapRef.current) return;

    const map = L.map(mapHostRef.current, {
      zoomControl: true,
      minZoom: 5,
      maxZoom: 16
    }).setView([20.5937, 78.9629], 5);

    tileRef.current = L.tileLayer(theme === "dark" ? DARK_TILE : LIGHT_TILE, {
      attribution: TILE_ATTRIBUTION
    }).addTo(map);

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current || !tileRef.current) return;
    tileRef.current.setUrl(theme === "dark" ? DARK_TILE : LIGHT_TILE);
  }, [theme]);

  const styleFn = useMemo(() => {
    return (feature) => {
      const isSelected = feature.properties?.id === selectedId;
      return {
        color: isSelected ? "#ff7a00" : "#2f84ff",
        weight: isSelected ? 3 : 2,
        fillColor: isSelected ? "#ffb066" : "#4fa0ff",
        fillOpacity: isSelected ? 0.45 : 0.2
      };
    };
  }, [selectedId]);

  useEffect(() => {
    if (!mapRef.current || !mapData) return;

    if (geoLayerRef.current) {
      geoLayerRef.current.remove();
      layerByIdRef.current.clear();
      allBoundsRef.current = null;
    }

    const layer = L.geoJSON(mapData, {
      style: styleFn,
      onEachFeature: (feature, featureLayer) => {
        const id = feature.properties?.id;
        if (id) layerByIdRef.current.set(id, featureLayer);

        featureLayer.bindTooltip(feature.properties?.name || "Municipality");
        featureLayer.on("click", () => {
          if (id) onSelect(id);
        });
        featureLayer.on("mouseover", () => {
          featureLayer.setStyle({ weight: 4, fillOpacity: 0.4 });
        });
        featureLayer.on("mouseout", () => {
          layer.resetStyle(featureLayer);
        });
      }
    }).addTo(mapRef.current);

    geoLayerRef.current = layer;
    allBoundsRef.current = layer.getBounds();
    if (allBoundsRef.current?.isValid() && !selectedId) {
      mapRef.current.fitBounds(allBoundsRef.current, { padding: [20, 20] });
    }
  }, [mapData, onSelect, styleFn]);

  useEffect(() => {
    if (!geoLayerRef.current || !mapRef.current) return;

    geoLayerRef.current.setStyle(styleFn);
    
    if (selectedId) {
      const selectedLayer = layerByIdRef.current.get(selectedId);
      if (selectedLayer) {
        selectedLayer.bringToFront();
        mapRef.current.fitBounds(selectedLayer.getBounds(), { padding: [28, 28], maxZoom: 12 });
      }
    } else if (allBoundsRef.current?.isValid()) {
      mapRef.current.fitBounds(allBoundsRef.current, { padding: [20, 20] });
    }
  }, [selectedId, styleFn]);

  const resetView = () => {
    onSelect(null);
  };

  return (
    <section id="map" className="section-card" aria-labelledby="map-title">
      <div className="section-head map-head">
        <h2 id="map-title">Municipality Boundary Map</h2>
        <button type="button" className="btn btn-small" onClick={resetView}>Reset view</button>
      </div>
      <p className="muted">Only municipality-level outlines are shown on the map. Individual wards are intentionally excluded.</p>

      <div className="map-wrap">
        <div className="map-canvas" ref={mapHostRef} role="region" aria-label="Municipality boundary map" />
        <aside className="map-sidebar" aria-live="polite">
          <div className="sidebar-list-container">
            <h3>Municipalities</h3>
            <ul className="sidebar-list">
              {municipalities.map((m) => (
                <li key={m.id}>
                  <button
                    type="button"
                    className={`sidebar-item ${selectedId === m.id ? "selected" : ""}`}
                    onClick={() => onSelect(m.id)}
                  >
                    {m.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {selectedMunicipality && (
            <div className="sidebar-details section-card">
              <h4>{selectedMunicipality.name}</h4>
              <p className="small">{selectedMunicipality.district}, {selectedMunicipality.state}</p>
              <hr />
              <p className="muted small">Geometry: <code>{selectedMunicipality.map.geometry_source}</code></p>
              <p className="muted small">Updated: {selectedMunicipality.last_updated || "N/A"}</p>
              <p className="muted small">Files: {selectedMunicipality.stats.file_count}</p>
              <a className="btn btn-ghost btn-small" href={`https://github.com/mahanvyakti/OS-Bhugol/tree/main/${selectedMunicipality.paths.root}`} target="_blank" rel="noreferrer">GitHub Folder</a>
            </div>
          )}
        </aside>
      </div>
    </section>
  );
}


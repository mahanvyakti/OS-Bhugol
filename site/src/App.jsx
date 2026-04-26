import { useEffect, useMemo, useState } from "react";
import HeroSection from "./components/HeroSection";
import MapPanel from "./components/MapPanel";

const BASE = import.meta.env.BASE_URL;

function detectInitialTheme() {
  const stored = window.localStorage.getItem("os-bhugol-theme");
  if (stored === "light" || stored === "dark") return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function App() {
  const [theme, setTheme] = useState(detectInitialTheme);
  const [manifest, setManifest] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("os-bhugol-theme", theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === "dark" ? "light" : "dark");

  useEffect(() => {
    const run = async () => {
      try {
        const [manifestRes, mapRes] = await Promise.all([
          fetch(`${BASE}generated/municipalities-index.json`),
          fetch(`${BASE}generated/municipalities-map.geojson`)
        ]);

        if (!manifestRes.ok || !mapRes.ok) {
          throw new Error("Failed to load generated site data.");
        }

        const loadedManifest = await manifestRes.json();
        const loadedMap = await mapRes.json();
        setManifest(loadedManifest);
        setMapData(loadedMap);
      } catch (err) {
        setError(err.message);
      }
    };
    run();
  }, []);

  const [selectedDistrict, setSelectedDistrict] = useState(null);

  const municipalities = manifest?.municipalities || [];
  
  const groupedByState = useMemo(() => {
    const q = query.toLowerCase();
    const filtered = municipalities.filter((m) =>
      [m.name, m.district, m.state].some((val) => val?.toLowerCase().includes(q))
    );
    
    return filtered.reduce((acc, m) => {
      if (!acc[m.state]) acc[m.state] = {};
      if (!acc[m.state][m.district]) acc[m.state][m.district] = [];
      acc[m.state][m.district].push(m);
      return acc;
    }, {});
  }, [municipalities, query]);

  const toggleSelect = (id) => {
    setSelectedDistrict(null);
    setSelectedId((prev) => (prev === id ? null : id));
  };

  const selectDistrict = (stateName, distName) => {
    setSelectedId(null);
    setSelectedDistrict({ state: stateName, district: distName });
  };

  const selectedMunicipality = municipalities.find((item) => item.id === selectedId) || null;
  
  const districtMunis = selectedDistrict 
    ? municipalities.filter(m => m.state === selectedDistrict.state && m.district === selectedDistrict.district)
    : [];

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="logo">OS-Bhugol</div>
        <nav>
          <a href="#map">Map</a>
          <a href="#directory">Directory</a>
          <a href="https://github.com/mahanvyakti/OS-Bhugol" target="_blank" rel="noreferrer">GitHub</a>
          <button className="btn btn-small" onClick={toggleTheme} style={{ padding: '0.4rem 0.6rem' }}>
            {theme === "dark" ? "Light" : "Dark"}
          </button>
        </nav>
      </header>

      <main className="main-content">
        <HeroSection />

        <section className="bento-box bento-stats">
          <div className="bento-header">Quick Stats</div>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-val">{municipalities.length}</span>
              <span className="stat-label">Municipalities</span>
            </div>
            <div className="stat-card">
              <span className="stat-val">
                {municipalities.reduce((sum, m) => sum + (m.stats?.ward_count || 0), 0)}
              </span>
              <span className="stat-label">Total Wards</span>
            </div>
          </div>
        </section>

        <section id="map" className="bento-box bento-map">
          <div className="bento-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Geospatial Explorer</span>
            <button 
              type="button" 
              className="btn btn-small" 
              onClick={() => setSelectedId(null)}
              style={{ padding: '0.2rem 0.5rem', fontSize: '0.65rem' }}
            >
              Reset Map
            </button>
          </div>
          <MapPanel
            mapData={mapData}
            municipalities={municipalities}
            selectedId={selectedId}
            onSelect={toggleSelect}
            selectedMunicipality={selectedMunicipality}
            theme={theme}
          />
        </section>

        <section id="directory" className="bento-box bento-directory">
          <div className="bento-header">Database Directory</div>
          <div className="directory-split" style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '2rem', height: '600px' }}>
            <div className="directory-list-side" style={{ overflowY: 'auto', paddingRight: '1rem' }}>
              <input
                type="search"
                placeholder="Search database..."
                className="btn"
                style={{ width: '100%', textAlign: 'left', textTransform: 'none', marginBottom: '1.5rem', background: 'var(--surface-muted)' }}
                onChange={(e) => setQuery(e.target.value)}
              />
              <div className="directory-tree">
                {Object.entries(groupedByState).map(([state, districts]) => (
                  <div key={state} className="state-group" style={{ marginBottom: '1rem' }}>
                    <div className="state-header">{state}</div>
                    <div className="district-list" style={{ padding: '1rem' }}>
                      {Object.entries(districts).map(([district, munis]) => (
                        <div key={district} style={{ marginBottom: '1rem' }}>
                          <button 
                            className="stat-label" 
                            onClick={() => selectDistrict(state, district)}
                            style={{ 
                              marginBottom: '0.5rem', 
                              fontSize: '0.6rem', 
                              background: 'none', 
                              border: 'none', 
                              padding: 0, 
                              cursor: 'pointer',
                              color: selectedDistrict?.district === district ? 'var(--accent)' : 'var(--text-muted)',
                              textDecoration: selectedDistrict?.district === district ? 'underline' : 'none'
                            }}
                          >
                            {district} (DISTRICT)
                          </button>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                            {munis.map((m) => (
                              <div 
                                key={m.id} 
                                className={`municipality-chip ${selectedId === m.id ? 'selected' : ''}`}
                                onClick={() => toggleSelect(m.id)}
                                style={{ padding: '0.5rem 0.75rem', fontSize: '0.85rem' }}
                              >
                                {m.name}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="directory-detail-side" style={{ borderLeft: '1px solid var(--bento-border)', paddingLeft: '2rem', overflowY: 'auto' }}>
              {selectedMunicipality ? (
                <div className="detail-content">
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '1rem' }}>
                    <h2 style={{ fontSize: '2rem', margin: '0.5rem 0' }}>{selectedMunicipality.name}</h2>
                    {selectedMunicipality.name_local && (
                      <span className="muted" style={{ fontSize: '1.2rem', fontFamily: 'var(--font-body)' }}>
                        {selectedMunicipality.name_local}
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '2rem', margin: '1.5rem 0' }}>
                    <div>
                      <div className="stat-label">District</div>
                      <div style={{ fontWeight: 600 }}>{selectedMunicipality.district}</div>
                    </div>
                    <div>
                      <div className="stat-label">State</div>
                      <div style={{ fontWeight: 600 }}>{selectedMunicipality.state}</div>
                    </div>
                    <div>
                      <div className="stat-label">Wards</div>
                      <div style={{ fontWeight: 600 }}>{selectedMunicipality.stats?.ward_count || 'N/A'}</div>
                    </div>
                  </div>

                  <div className="bento-box" style={{ background: 'var(--surface-muted)', padding: '1.25rem', marginBottom: '1.5rem', boxShadow: 'none' }}>
                    <div className="stat-label" style={{ marginBottom: '0.75rem' }}>Technical Metadata</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', fontSize: '0.8rem' }}>
                      <div>
                        <span className="muted">Geometry Source:</span><br />
                        <code style={{ fontSize: '0.7rem', color: 'var(--accent)' }}>{selectedMunicipality.map?.geometry_source || 'Unknown'}</code>
                      </div>
                      <div>
                        <span className="muted">Coordinate System:</span><br />
                        <span>WGS84 (EPSG:4326)</span>
                      </div>
                      <div>
                        <span className="muted">Centroid:</span><br />
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem' }}>
                          {selectedMunicipality.map?.centroid?.lat}, {selectedMunicipality.map?.centroid?.lng}
                        </span>
                      </div>
                      <div>
                        <span className="muted">Formats:</span><br />
                        <span>{selectedMunicipality.stats?.formats_available?.join(', ') || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="muted">Last Updated:</span><br />
                        <span>{selectedMunicipality.last_updated || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="muted">Repository Path:</span><br />
                        <code style={{ fontSize: '0.65rem' }}>{selectedMunicipality.paths?.root}</code>
                      </div>
                    </div>
                  </div>

                  <div className="stat-label" style={{ marginBottom: '1rem' }}>Available Files</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
                    <a href={selectedMunicipality.links?.folder} target="_blank" rel="noreferrer" className="btn btn-primary">
                      <span>Browse Repository</span>
                    </a>
                    <a href={selectedMunicipality.links?.geometry_raw} download className="btn">
                      <span>Download GeoJSON</span>
                    </a>
                  </div>
                </div>
              ) : selectedDistrict ? (
                <div className="detail-content">
                  <div className="stat-label">District Summary</div>
                  <h2 style={{ fontSize: '2rem', margin: '0.5rem 0' }}>{selectedDistrict.district}</h2>
                  <p className="muted">{selectedDistrict.state}, India</p>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', margin: '2rem 0' }}>
                    <div className="bento-box" style={{ padding: '1rem', background: 'var(--surface-muted)', boxShadow: 'none' }}>
                      <span className="stat-val" style={{ fontSize: '1.5rem' }}>{districtMunis.length}</span>
                      <span className="stat-label">Municipalities Indexed</span>
                    </div>
                    <div className="bento-box" style={{ padding: '1rem', background: 'var(--surface-muted)', boxShadow: 'none' }}>
                      <span className="stat-val" style={{ fontSize: '1.5rem' }}>
                        {districtMunis.reduce((sum, m) => sum + (m.stats?.ward_count || 0), 0)}
                      </span>
                      <span className="stat-label">Total Wards Found</span>
                    </div>
                  </div>

                  <div className="stat-label" style={{ marginBottom: '1rem' }}>Municipalities in {selectedDistrict.district}</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {districtMunis.map(m => (
                      <div key={m.id} className="btn" style={{ justifyContent: 'space-between', textTransform: 'none', cursor: 'default' }}>
                        <span>{m.name}</span>
                        <span className="muted" style={{ fontSize: '0.7rem' }}>{m.stats?.ward_count || 'N/A'} Wards</span>
                      </div>
                    ))}
                  </div>

                  <div style={{ marginTop: '2.5rem' }}>
                    <a 
                      href={`https://github.com/mahanvyakti/OS-Bhugol/tree/main/data/india/${selectedDistrict.state.toLowerCase()}/districts/${selectedDistrict.district.toLowerCase()}`} 
                      target="_blank" 
                      rel="noreferrer" 
                      className="btn btn-primary"
                    >
                      Browse District Folder
                    </a>
                  </div>
                </div>
              ) : (
                <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <span style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</span>
                  <h3>Select an entity</h3>
                  <p style={{ maxWidth: '30ch' }}>Click on a district or municipality from the list to view data summaries.</p>
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="bento-box bento-use-cases">
          <div className="bento-header">Applications</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
            <div>
              <h4 style={{ marginBottom: '0.5rem' }}>Civic Tech</h4>
              <p className="muted" style={{ fontSize: '0.9rem' }}>Build dashboards, election maps, and service delivery trackers using precise ward outlines.</p>
            </div>
            <div>
              <h4 style={{ marginBottom: '0.5rem' }}>Urban Planning</h4>
              <p className="muted" style={{ fontSize: '0.9rem' }}>Analyze infrastructure distribution and population density across administrative zones.</p>
            </div>
            <div>
              <h4 style={{ marginBottom: '0.5rem' }}>Data Journalism</h4>
              <p className="muted" style={{ fontSize: '0.9rem' }}>Create interactive stories that help citizens understand their local government boundaries.</p>
            </div>
          </div>
        </section>

        <footer className="bento-box bento-footer">
          <div className="bento-header">Credits & Info</div>
          <div className="credits-grid">
            <div className="credit-item">
              <h4>Project Author</h4>
              <p>OS-Bhugol is maintained by <strong>Rajan Gaul</strong>. A project dedicated to open-access geographic data for India.</p>
              <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
                <a href="https://x.com/RajanGaul" target="_blank" rel="noreferrer" className="btn btn-small">X / Twitter</a>
                <a href="https://rajangaul.com/" target="_blank" rel="noreferrer" className="btn btn-small">Portfolio</a>
              </div>
            </div>
            <div className="credit-item">
              <h4>Data Sources</h4>
              <p>Special thanks to the <i><a href="https://opencity.in/" target="_blank" rel="noreferrer">OpenCity</a></i> community and various municipal portals for facilitating public data access.</p>
              <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
                <a href="https://github.com/mahanvyakti/OS-Bhugol/blob/main/CONTRIBUTING.md" target="_blank" rel="noreferrer" className="btn btn-small">Contribute Data</a>
                <a href="https://github.com/mahanvyakti/OS-Bhugol/issues" target="_blank" rel="noreferrer" className="btn btn-small">Report Issues</a>
              </div>
            </div>
          </div>
          <div style={{ marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid var(--bento-border)', fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
            <span>© {new Date().getFullYear()} OS-Bhugol Open Source Project</span>
            <span>Built with React + Leaflet</span>
          </div>
        </footer>
      </main>
    </div>
  );
}

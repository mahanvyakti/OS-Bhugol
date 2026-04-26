import { useEffect, useMemo, useState } from "react";
import DirectoryTree from "./components/DirectoryTree";
import Footer from "./components/Footer";
import HeroSection from "./components/HeroSection";
import MapPanel from "./components/MapPanel";
import ThemeToggle from "./components/ThemeToggle";
import UseCasesSection from "./components/UseCasesSection";

const BASE = import.meta.env.BASE_URL;

function detectInitialTheme() {
  const stored = window.localStorage.getItem("os-bhugol-theme");
  if (stored === "light" || stored === "dark") return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function filterMunicipalities(municipalities, query) {
  const q = query.trim().toLowerCase();
  if (!q) return municipalities;
  return municipalities.filter((item) =>
    [item.name, item.district, item.state, item.slug].filter(Boolean).join(" ").toLowerCase().includes(q)
  );
}

export default function App() {
  const [theme, setTheme] = useState("light");
  const [manifest, setManifest] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const initial = detectInitialTheme();
    setTheme(initial);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("os-bhugol-theme", theme);
  }, [theme]);

  useEffect(() => {
    const run = async () => {
      try {
        const [manifestRes, mapRes] = await Promise.all([
          fetch(`${BASE}generated/municipalities-index.json`),
          fetch(`${BASE}generated/municipalities-map.geojson`)
        ]);

        if (!manifestRes.ok || !mapRes.ok) {
          throw new Error("Failed to load generated site data. Run the homepage data build script.");
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

  const municipalities = manifest?.municipalities || [];
  const filteredMunicipalities = useMemo(
    () => filterMunicipalities(municipalities, query),
    [municipalities, query]
  );

  const toggleSelect = (id) => {
    setSelectedId((prev) => (prev === id ? null : id));
  };

  const selectedMunicipality = municipalities.find((item) => item.id === selectedId) || null;

  return (
    <div className="app-shell">
      <header className="site-header">
        <a href="#" className="logo">OS-Bhugol</a>
        <nav aria-label="Primary">
          <a href="#map">Map</a>
          <a href="#directory">Directory</a>
          <a href="https://github.com/mahanvyakti/OS-Bhugol" target="_blank" rel="noreferrer">Repo</a>
        </nav>
        <ThemeToggle
          theme={theme}
          onToggle={() => setTheme((prev) => (prev === "dark" ? "light" : "dark"))}
        />
      </header>

      <main className="main-content">
        <HeroSection municipalityCount={municipalities.length} />
        <UseCasesSection />

        {error ? (
          <section className="section-card">
            <h2>Data load error</h2>
            <p>{error}</p>
          </section>
        ) : (
          <>
            <MapPanel
              mapData={mapData}
              municipalities={municipalities}
              selectedId={selectedId}
              onSelect={toggleSelect}
              selectedMunicipality={selectedMunicipality}
              theme={theme}
            />
            <DirectoryTree
              municipalities={filteredMunicipalities}
              selectedId={selectedId}
              onSelect={toggleSelect}
              query={query}
              onQuery={setQuery}
            />
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}

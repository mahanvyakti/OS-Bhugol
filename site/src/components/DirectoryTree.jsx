function groupMunicipalities(municipalities) {
  const grouped = {};
  for (const municipality of municipalities) {
    const state = municipality.state || "Unknown state";
    const district = municipality.district || "Unknown district";
    if (!grouped[state]) grouped[state] = {};
    if (!grouped[state][district]) grouped[state][district] = [];
    grouped[state][district].push(municipality);
  }
  return grouped;
}

function FileLinks({ municipality }) {
  const files = [];
  if (municipality.paths?.meta) files.push({ label: "_meta.json", path: municipality.paths.meta });
  if (municipality.paths?.boundary) files.push({ label: "boundary", path: municipality.paths.boundary });
  if (Array.isArray(municipality.paths?.wards)) {
    for (const wardPath of municipality.paths.wards.slice(0, 3)) {
      files.push({ label: "wards", path: wardPath });
    }
  }

  return (
    <ul className="file-links">
      {files.map((file) => (
        <li key={`${municipality.id}-${file.path}`}>
          <a href={`https://github.com/mahanvyakti/OS-Bhugol/blob/main/${file.path}`} target="_blank" rel="noreferrer">
            {file.label}: {file.path}
          </a>
        </li>
      ))}
    </ul>
  );
}

export default function DirectoryTree({ municipalities, selectedId, onSelect, query, onQuery }) {
  const grouped = groupMunicipalities(municipalities);

  return (
    <section id="directory" className="section-card" aria-labelledby="directory-title">
      <div className="section-head">
        <h2 id="directory-title">Data Directory</h2>
        <input
          value={query}
          onChange={(event) => onQuery(event.target.value)}
          type="search"
          placeholder="Search municipality or district"
          aria-label="Search municipalities"
        />
      </div>

      <div className="directory-tree" role="tree">
        {Object.entries(grouped).map(([state, districts]) => (
          <details key={state} open>
            <summary>{state}</summary>
            <div className="tree-level">
              {Object.entries(districts).map(([district, districtMunicipalities]) => (
                <details key={`${state}-${district}`}>
                  <summary>{district} ({districtMunicipalities.length})</summary>
                  <div className="municipality-list">
                    {districtMunicipalities.map((municipality) => (
                      <article
                        key={municipality.id}
                        className={`municipality-card ${selectedId === municipality.id ? "selected" : ""}`}
                      >
                        <div className="municipality-head">
                          <h3>{municipality.name}</h3>
                          <button type="button" className="btn btn-small" onClick={() => onSelect(municipality.id)}>
                            View on map
                          </button>
                        </div>
                        <p className="muted">
                          Geometry source: <code>{municipality.map.geometry_source}</code>
                        </p>
                        <p className="muted">
                          Formats: {municipality.stats.formats_available.join(", ") || "N/A"}
                        </p>
                        <FileLinks municipality={municipality} />
                      </article>
                    ))}
                  </div>
                </details>
              ))}
            </div>
          </details>
        ))}
      </div>
    </section>
  );
}

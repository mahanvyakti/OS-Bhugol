const USE_CASES = [
  "Election and public dashboard visualizations",
  "Civic-tech routing and service area mapping",
  "Data journalism and local investigations",
  "Urban planning and infrastructure overlays",
  "Public health and emergency response analysis",
  "GIS learning using real Indian administrative data"
];

export default function UseCasesSection() {
  return (
    <section className="section-card" aria-labelledby="use-cases-title">
      <h2 id="use-cases-title">What You Can Build</h2>
      <ul className="use-case-grid">
        {USE_CASES.map((item) => (
          <li key={item} className="chip">{item}</li>
        ))}
      </ul>
    </section>
  );
}

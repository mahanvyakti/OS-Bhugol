export default function HeroSection({ municipalityCount }) {
  return (
    <section className="hero section-card" aria-labelledby="hero-title">
      <p className="eyebrow">Open geospatial boundaries for India</p>
      <h1 id="hero-title">OS-Bhugol makes civic boundaries usable for builders.</h1>
      <p className="hero-copy">
        A clean, versioned collection of machine-readable municipal boundaries and related layers.
        Start with municipality-level map views here, then dive deeper into the repository for richer data.
      </p>
      <div className="hero-stats" role="status" aria-live="polite">
        <span>{municipalityCount} municipalities indexed</span>
      </div>
      <div className="hero-actions">
        <a className="btn btn-primary" href="#map">View data map</a>
        <a className="btn btn-ghost" href="https://github.com/mahanvyakti/OS-Bhugol" target="_blank" rel="noreferrer">Open GitHub repo</a>
        <a className="btn btn-ghost" href="https://github.com/mahanvyakti/OS-Bhugol/blob/main/CONTRIBUTING.md" target="_blank" rel="noreferrer">How to contribute</a>
      </div>
    </section>
  );
}

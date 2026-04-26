export default function HeroSection() {
  return (
    <section className="bento-box bento-hero" aria-labelledby="hero-title">
      <div className="bento-header">Context</div>
      <h1 id="hero-title">Open civic boundaries for builders.</h1>
      <p>
        Machine-readable municipal and ward-level geographic data, 
        versioned and ready for your next civic-tech project.
      </p>
      <div className="hero-actions" style={{ justifyContent: 'flex-start', marginTop: '1.5rem' }}>
        <a className="btn btn-primary" href="#map">Explore Map</a>
        <a className="btn" href="https://github.com/mahanvyakti/OS-Bhugol" target="_blank" rel="noreferrer">GitHub Repo</a>
      </div>
    </section>
  );
}

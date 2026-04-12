import React, { useState } from 'react';
import './App.css';

const App = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [step, setStep] = useState(0);

  const steps = [
    "Scraping article content...",
    "Parsing metadata & structure...",
    "Extracting factual claims...",
    "Cross-referencing fact-check databases...",
    "Generating analysis report..."
  ];

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setResult(null);
    setError(null);
    setStep(0);

    // Simulate progress for better UX
    const timer = setInterval(() => {
      setStep(prev => (prev < 4 ? prev + 1 : prev));
    }, 2000);

    try {
      const response = await fetch('http://localhost:8001/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to verify article');
      }

      const data = await response.json();
      clearInterval(timer);
      setStep(4);
      setTimeout(() => {
        setResult(data);
        setLoading(false);
      }, 500);
    } catch (err) {
      clearInterval(timer);
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="app-wrapper">
      <nav className="sticky-nav">
        <div className="nav-content">
          <div className="nav-logo">
            <div className="logo-box">
              <svg className="shield-icon-small" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                <polyline points="9 12 11 14 15 10"></polyline>
              </svg>
            </div>
            <span>Verity</span>
          </div>
          <div className="nav-links">
            <a href="#how-it-works">How it works</a>
            <a href="#methodology">Methodology</a>
            <a href="#api">API</a>
          </div>
        </div>
      </nav>
      <div className="container">
      <header>
        <div className="header-meta">
          <span>Daily Edition</span>
          <span>{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
          <span>Price: Factual Integrity</span>
        </div>
        <div className="logo">VERITY</div>
        <div className="header-meta" style={{ borderBottom: 'none', borderTop: '1px solid var(--border-color)', marginTop: '0.5rem', paddingTop: '0.5rem' }}>
          <span>Truth in the Digital Age</span>
          {result && (
            <button className="new-analysis-btn" onClick={() => { setResult(null); setUrl(''); }}>
              New Analysis
            </button>
          )}
          <span>Verified Reports</span>
        </div>
      </header>

      {!loading && !result && (
        <>
          <div className="hero">
            <h1>Deciphering Global News</h1>
            <p>A rigorous automated verification system for extracting and cross-referencing factual claims from any digital source.</p>
          </div>

          <form className="verify-form" onSubmit={handleVerify}>
            <div className="input-wrapper">
              <input
                type="url"
                className="verify-input"
                placeholder="Enter Article URL for Verification..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
              <button type="submit" className="verify-button">Analyze</button>
            </div>
            {error && <p style={{ color: 'var(--error-color)', marginTop: '2rem', textAlign: 'center', fontStyle: 'italic', fontWeight: 'bold' }}>{error}</p>}
          </form>
        </>
      )}

      {loading && (
        <div className="loading-wrapper">
          <div className="spinner"></div>
          <div className="status-list">
            {steps.map((s, i) => (
              <div key={i} className={`status-item ${i === step ? 'active' : ''} ${i < step ? 'completed' : ''}`}>
                <span className="dot">{i < step ? '●' : i === step ? '○' : '·'}</span>
                {s}
              </div>
            ))}
          </div>
        </div>
      )}

      {result && (
        <div className="results-view">
          <div className="score-card">
            <span className="score-title">Integrity Assessment</span>
            <div className="score-value">
              <span className="score-number" style={{ 
                color: result.factual_integrity_score >= 80 ? 'var(--success-color)' : 
                       result.factual_integrity_score >= 60 ? 'var(--warning-color)' : 
                       'var(--error-color)' 
              }}>
                {result.factual_integrity_score}
              </span>
              <span className="score-total">pts</span>
            </div>
            <span className="reliability-tag" style={{ 
                color: result.factual_integrity_score >= 80 ? 'var(--success-color)' : 
                       result.factual_integrity_score >= 60 ? 'var(--warning-color)' : 
                       'var(--error-color)' 
              }}>
              {result.reliability_label}
            </span>
          </div>

          <article className="article-info">
            <h2>{result.metadata.title}</h2>
            <div className="article-meta">
              <span>Source: {new URL(url).hostname}</span>
              <span>Date: {result.metadata.publish_date || 'N/A'}</span>
              <span>Claims: {result.claims.length}</span>
            </div>
            <p className="article-summary">{result.metadata.summary}</p>
          </article>

          <section className="claims-section">
            <h3>Factual Evidence Analysis</h3>
            {result.claims.map((claim, idx) => (
              <div key={idx} className="claim-card">
                <div className="claim-header">
                  <div className="verdict-tag" style={{ 
                    color: claim.verdict === 'True' ? 'var(--success-color)' : 
                           claim.verdict === 'False' ? 'var(--error-color)' : 
                           'var(--warning-color)'
                  }}>
                    {claim.verdict}
                  </div>
                  <div className="claim-text">"{claim.claim}"</div>
                </div>
                <p className="claim-explanation">{claim.explanation}</p>
              </div>
            ))}
          </section>
        </div>
      )}
      </div>

      <footer className="dark-footer">
        <div className="footer-content">
          <div className="footer-brand-section">
            <div className="footer-logo">
              <svg className="shield-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                <polyline points="9 12 11 14 15 10"></polyline>
              </svg>
              <span>Verity</span>
            </div>
            <p className="footer-desc">
              Empowering global citizens with AI-driven news verification tools to combat misinformation and promote media literacy.
            </p>
          </div>
          
          <div className="footer-links-section">
            <div className="footer-nav-column">
              <h4>RESOURCES</h4>
              <ul>
                <li><a href="#" className="animated-link">Documentation</a></li>
                <li><a href="#" className="animated-link">Fact-check DB</a></li>
                <li><a href="#" className="animated-link">Browser Extension</a></li>
              </ul>
            </div>
            
            <div className="footer-nav-column">
              <h4>CONNECT</h4>
              <ul>
                <li><a href="#" className="animated-link">Twitter</a></li>
                <li><a href="#" className="animated-link">GitHub</a></li>
                <li><a href="#" className="animated-link">Contact</a></li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;

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
      const response = await fetch('http://localhost:8000/api/verify', {
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
  );
};

export default App;

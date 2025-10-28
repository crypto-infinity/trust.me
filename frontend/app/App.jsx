import React, { useState } from "react";
import "../styles.css";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || window.BACKEND_URL || `https://trustme-backend.azurewebsites.net`;
import { __VERSION__ } from "./config";

export default function App() {
  const [subject, setSubject] = useState("");
  const [type, setType] = useState("person"); // non più usato nell'API, ma lasciato per compatibilità UI
  const [context, setContext] = useState("");
  const [language, setLanguage] = useState("en-US");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [showResult, setShowResult] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setShowResult(false);
    let apiResult = null;
    let apiError = null;
    try {
      const response = await fetch(`${BACKEND_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, context, language })
      });
      if (!response.ok) throw new Error("Errore API: " + response.status);
      apiResult = await response.json();
    } catch (err) {
      apiError = err.message;
    }
    // Timeout di 15 secondi dopo la chiamata API
    setTimeout(() => {
      setLoading(false);
      if (apiError) {
        setError(apiError);
      } else {
        setResult(apiResult);
        setShowResult(true);
      }
    }, 15000);
  };

  return (
    <div className={`container${loading ? " loading" : ""}`}> 
      <h1>Trust.me Analyzer</h1>
      <hr></hr>
      <h4>TrustMe: automatic agentic trust validation for online identities - {__VERSION__}</h4>
      <form id="analyze-form" onSubmit={handleSubmit} className={loading ? "form-loading" : ""}>
        <label htmlFor="subject">Subject:</label>
        <input type="text" id="subject" value={subject} onChange={e => setSubject(e.target.value)} required />

        <label htmlFor="context">Context [optional]:</label>
        <textarea id="context" value={context} onChange={e => setContext(e.target.value)}/>

        <label htmlFor="language">Response language:</label>
        <select id="language" value={language} onChange={e => setLanguage(e.target.value)}>
          <option value="it-IT">Italiano</option>
          <option value="en-US">English</option>
          <option value="fr-FR">Français</option>
          <option value="de-DE">Deutsch</option>
          <option value="es-ES">Español</option>
        </select>

        <button type="submit" disabled={loading} className={`animated-btn${loading ? " btn-loading" : ""}`}>{loading ? (
          <span style={{display: 'inline-flex', alignItems: 'center'}}>
            Analisys in progress...
            <svg style={{marginLeft: 8}} width="18" height="18" viewBox="0 0 50 50" className="spinner" xmlns="http://www.w3.org/2000/svg">
              <circle cx="25" cy="25" r="20" fill="none" stroke="#888" strokeWidth="5" strokeDasharray="31.4 31.4" strokeLinecap="round">
                <animateTransform attributeName="transform" type="rotate" from="0 25 25" to="360 25 25" dur="0.8s" repeatCount="indefinite" />
              </circle>
            </svg>
          </span>
        ) : "Analyze"}</button>
      </form>
      <div id="result">
        {error && <span style={{ color: "red" }}>Errore: {error}</span>}
        {result && (
          <div className={`result-animated${showResult ? " show" : ""}`}>
            {(() => {
              const score = typeof result.score === "number" ? result.score : (typeof result.trust_score === "number" ? result.trust_score : null);
              const comment = result.comment || (result.details && result.details.comment);
              const text = result.text || result.report;
              return <>
                {typeof score === "number" && (
                  <>
                    <div className="score-bar-container">
                      <div className="score-label">Score: <b>{score}</b>/100</div>
                      <input type="range" min="0" max="100" value={score} disabled className="score-slider" readOnly />
                      <div className="score-bar-bg">
                        <div className="score-bar-fill" style={{ width: `${score}%` }}></div>
                      </div>
                    </div>
                    {result.details && typeof result.details === 'string' && (
                      <div style={{fontFamily: 'inherit', fontSize: '1em', marginTop: 12, color: '#222', whiteSpace: 'pre-line'}}>{result.details}</div>
                    )}
                  </>
                )}
                {!score && (
                  <div className="comment-box">{comment || 'Nessun commento disponibile.'}</div>
                )}
              </>;
            })()}
          </div>
        )}
      </div>
    </div>
  );
}

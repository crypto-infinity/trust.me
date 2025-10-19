import React, { useState } from "react";
import "../styles.css";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || window.BACKEND_URL || `https://trustme-backend.azurewebsites.net`;
import { __VERSION__ } from "./config";

export default function App({ user }) {
  const [subject, setSubject] = useState("");
  const [type, setType] = useState("person"); // non più usato nell'API, ma lasciato per compatibilità UI
  const [context, setContext] = useState("");
  const [language, setLanguage] = useState("it-IT");
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
    try {
      const response = await fetch(`${BACKEND_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, context, language })
      });
      if (!response.ok) throw new Error("Errore API: " + response.status);
      const res = await response.json();
      setResult(res);
      setTimeout(() => setShowResult(true), 100);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`container${loading ? " loading" : ""}`}> 
      <h1>Trust.me Analyzer v.{__VERSION__}</h1>
      <h2>AI-powered trust score calculator</h2>
      <div style={{marginBottom: 16, fontSize: 15, color: '#555', textAlign: 'center'}}>
        Benvenuto, <b>{user && user.name ? user.name : ""}</b>
      </div>
      <hr></hr>
      <h4>Inserisci i dati della persona o dell'azienda da valutare:</h4>
      <form id="analyze-form" onSubmit={handleSubmit} className={loading ? "form-loading" : ""}>
        <label htmlFor="subject">Soggetto:</label>
        <input type="text" id="subject" value={subject} onChange={e => setSubject(e.target.value)} required />

        <label htmlFor="context">Affina la ricerca [facoltativo]:</label>
        <textarea id="context" value={context} onChange={e => setContext(e.target.value)} required />

        <label htmlFor="language">Lingua:</label>
        <select id="language" value={language} onChange={e => setLanguage(e.target.value)}>
          <option value="it-IT">Italiano</option>
          <option value="en-US">English</option>
          <option value="fr-FR">Français</option>
          <option value="de-DE">Deutsch</option>
          <option value="es-ES">Español</option>
        </select>

        <button type="submit" disabled={loading} className={`animated-btn${loading ? " btn-loading" : ""}`}>{loading ? "Analisi in corso..." : "Analizza"}</button>
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

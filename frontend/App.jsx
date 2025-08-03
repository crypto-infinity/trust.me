import React, { useState } from "react";
import "./styles.css";

const BACKEND_PORT = window.BACKEND_PORT || 8000;
const BACKEND_URL = window.BACKEND_URL || `http://localhost:${BACKEND_PORT}`;

export default function App() {
  const [subject, setSubject] = useState("");
  const [type, setType] = useState("person");
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleLogin = (provider) => {
    alert(`Login con ${provider} (mock): implementa OAuth2 lato backend per produzione.`);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await fetch(`${BACKEND_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, type, context })
      });
      if (!response.ok) throw new Error("Errore API: " + response.status);
      const res = await response.json();
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Trust.me Analyzer</h1>
      <div id="auth-section">
        <button onClick={() => handleLogin("Google")}>Login con Google</button>
        <button onClick={() => handleLogin("Microsoft")}>Login con Microsoft</button>
      </div>
      <form id="analyze-form" onSubmit={handleSubmit}>
        <label htmlFor="subject">Soggetto:</label>
        <input type="text" id="subject" value={subject} onChange={e => setSubject(e.target.value)} required />

        <label htmlFor="type">Tipo:</label>
        <select id="type" value={type} onChange={e => setType(e.target.value)} required>
          <option value="person">Persona</option>
          <option value="company">Azienda</option>
        </select>

        <label htmlFor="context">Contesto:</label>
        <textarea id="context" value={context} onChange={e => setContext(e.target.value)} required />

        <button type="submit" disabled={loading}>{loading ? "Analisi in corso..." : "Analizza"}</button>
      </form>
      <div id="result">
        {error && <span style={{ color: "red" }}>Errore: {error}</span>}
        {result && (
          <>
            {typeof result.score === "number" && (
              <div className="score-bar-container">
                <div className="score-label">Score: <b>{result.score}</b>/100</div>
                <input type="range" min="0" max="100" value={result.score} disabled className="score-slider" readOnly />
                <div className="score-bar-bg">
                  <div className="score-bar-fill" style={{ width: `${result.score}%` }}></div>
                </div>
              </div>
            )}
            {result.comment && <div className="comment-box">{result.comment}</div>}
            {result.text && <div className="output-text">{result.text}</div>}
            {!(result.score || result.comment || result.text) && (
              <div className="output-text">{JSON.stringify(result, null, 2)}</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

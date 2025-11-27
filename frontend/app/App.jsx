import React, { useState } from "react";
import { PublicClientApplication } from "@azure/msal-browser";
// Configurazione MSAL
const msalConfig = {
  auth: {
    clientId: import.meta.env.VITE_APP_CLIENT_ID || "", // Sostituisci con il tuo clientId
    authority: "https://login.microsoftonline.com/" + import.meta.env.VITE_TENANT_ID, // Modifica se usi tenant specifico
    redirectUri: window.location.origin,
  },
};

const msalInstance = new PublicClientApplication(msalConfig);
import "../styles.css";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || window.BACKEND_URL || `https://trustme-backend-dev.azurewebsites.net`;
import { __VERSION__ } from "./config";

export default function App() {
  const [subject, setSubject] = useState("");
  const [type, setType] = useState("person");
  const [context, setContext] = useState("");
  const [language, setLanguage] = useState("en-US");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [showResult, setShowResult] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userName, setUserName] = useState("");

  const handleLogin = async () => {
    try {
      await msalInstance.initialize();
      const loginResponse = await msalInstance.loginPopup({ scopes: ["openid", "profile", "email"] });
      const account = loginResponse.account;
      setIsAuthenticated(true);
      setUserName(account.name || account.username);
      // Recupera il token
      const tokenResponse = await msalInstance.acquireTokenSilent({
        scopes: [
          "api://" + import.meta.env.VITE_API_CLIENT_ID + "/user_impersonation"
        ],
        account,
      });
      const token = tokenResponse.accessToken;
      localStorage.setItem("auth_token", token);
    } catch (error) {
      // Fallback: loginPopup se acquireTokenSilent fallisce
      try {
        const tokenResponse = await msalInstance.acquireTokenPopup(
          { scopes: [
            "api://" + import.meta.env.VITE_API_CLIENT_ID + "/user_impersonation"
          ] }
        );
        const token = tokenResponse.accessToken;
        localStorage.setItem("auth_token", token);
        setIsAuthenticated(true);
        setUserName(tokenResponse.account.name || tokenResponse.account.username);
      } catch (err) {
        alert("Login fallito: " + err.message);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setShowResult(false);
    let apiResult = null;
    let apiError = null;
    try {
      // Recupera il token da localStorage
      const token = localStorage.getItem("auth_token");
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;
      const response = await fetch(`${BACKEND_URL}/analyze`, {
        method: "POST",
        headers,
        body: JSON.stringify({ subject, context, language })
      });
      if (!response.ok) throw new Error("Errore API: " + response.status);
      apiResult = await response.json();
    } catch (err) {
      apiError = err.message;
    }
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

  if (!isAuthenticated) {
    return (
      <div className="container">
        <h1>Trust.me Analyzer</h1>
        <hr></hr>
        <div style={{ marginBottom: "1rem" }}>
          <button onClick={handleLogin}>Login con Microsoft</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`container${loading ? " loading" : ""}`}> 
      <h1>Trust.me Analyzer</h1>
      <hr></hr>
      <h4>TrustMe: automatic agentic trust validation for online identities - {__VERSION__}</h4>
      <div style={{ marginBottom: "1rem" }}>
        <span>Benvenuto, {userName}!</span>
      </div>
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
            Analysis in progress...
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

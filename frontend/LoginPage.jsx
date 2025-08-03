import React, { useState } from "react";
import App from "./app/App";
import "./styles.css";

export default function LoginPage() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = (provider) => {
    setLoading(true);
    setTimeout(() => {
      setUser({ name: provider === "guest" ? "Guest" : provider });
      setLoading(false);
    }, 600); // Simula login
  };

  if (user) return <App user={user} />;

  return (
    <div className={`container${loading ? " loading" : ""}`}> 
      <h1>Trust.me Analyzer</h1>
      <div id="auth-section" style={{marginTop: 40, display: 'flex', flexDirection: 'column', gap: 16}}>
        <button className="animated-btn" onClick={() => handleLogin("Google")} disabled={loading}>Login con Google</button>
        <button className="animated-btn" onClick={() => handleLogin("Microsoft")} disabled={loading}>Login con Microsoft</button>
        <button className="animated-btn" onClick={() => handleLogin("guest")} disabled={loading}>Login come ospite</button>
      </div>
    </div>
  );
}

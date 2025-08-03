// Login con Google (mock)
document.getElementById('google-login').onclick = function() {
    alert('Login con Google (mock): implementa OAuth2 lato backend per produzione.');
    // Qui dovresti reindirizzare verso il backend per l'autenticazione Google
};

// Login con Microsoft (mock)
document.getElementById('microsoft-login').onclick = function() {
    alert('Login con Microsoft (mock): implementa OAuth2 lato backend per produzione.');
    // Qui dovresti reindirizzare verso il backend per l'autenticazione Microsoft
};

// Parametrizzazione URL backend
const BACKEND_PORT = window.BACKEND_PORT || (typeof process !== 'undefined' && process.env && process.env.PORT) || 8000;
const BACKEND_URL = window.BACKEND_URL || `http://localhost:${BACKEND_PORT}`;

// Gestione submit form
const form = document.getElementById('analyze-form');
const resultDiv = document.getElementById('result');

form.onsubmit = async function(e) {
    e.preventDefault();
    resultDiv.innerHTML = '<span>Analisi in corso...</span>';
    let typeValue = form.type.value;
    // Mappatura esplicita se serve (già person/company)
    if (typeValue === 'person' || typeValue === 'company') {
        typeValue = typeValue;
    }
    const data = {
        subject: form.subject.value,
        type: typeValue,
        context: form.context.value
    };
    try {
        const response = await fetch(`${BACKEND_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Errore API: ' + response.status);
        const res = await response.json();

        // Atteso: res.score (0-100), res.comment (string), altri campi opzionali
        let html = '';
        if (typeof res.score === 'number') {
            html += `<div class="score-bar-container">
                <div class="score-label">Score: <b>${res.score}</b>/100</div>
                <input type="range" min="0" max="100" value="${res.score}" disabled class="score-slider" />
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="width:${res.score}%;"></div>
                </div>
            </div>`;
        }
        if (res.comment) {
            html += `<div class="comment-box">${res.comment}</div>`;
        }
        if (res.text) {
            html += `<div class="output-text">${res.text}</div>`;
        }
        resultDiv.innerHTML = html;
    } catch (err) {
        resultDiv.innerHTML = '<span style="color:red">Errore: ' + err.message + '</span>';
    }
};

// Espandi la pagina a piena altezza
window.onload = function() {
    document.body.style.minHeight = '100vh';
    document.documentElement.style.height = '100%';
    document.body.style.height = '100vh';
    document.querySelector('.container').style.minHeight = '100vh';
};

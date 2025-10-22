# Trust.me

Trust.me è una piattaforma progettata per valutare, verificare e presentare informazioni affidabili tramite un sistema di scoring automatizzato e agenti intelligenti. Il progetto è composto da un backend Python (FastAPI), un frontend React e infrastruttura come codice (IaC) con Terraform.

## Architettura

- **Backend**: Python, FastAPI, LangChain, agenti modulari per scraping, verifica, scoring e ricerca.
- **Frontend**: React, Vite, interfaccia moderna per la presentazione dei risultati e autenticazione.
- **IaC**: Terraform per provisioning cloud e gestione delle risorse.

## Funzionalità principali

- **Scraping e raccolta dati**: Estrazione automatica di informazioni da fonti web.
- **Verifica e scoring**: Valutazione dell'affidabilità tramite agenti e algoritmi personalizzati.
- **Interfaccia utente**: Visualizzazione dei risultati, login e gestione utenti.
- **Integrazione cloud**: Deployment automatizzato e scalabile.

## Avvio rapido

### Backend

1. Posizionarsi nella cartella `backend`:
	```powershell
	cd backend
	```
2. Installare le dipendenze:
	```powershell
	pip install -r requirements.txt
	```
3. Avviare il server:
	```powershell
	uvicorn main:app --reload
	```

### Frontend

1. Posizionarsi nella cartella `frontend`:
	```powershell
	cd frontend
	```
2. Installare le dipendenze:
	```powershell
	npm install
	```
3. Avviare l'applicazione:
	```powershell
	npm run dev
	```

## Struttura del progetto

- `backend/` — API, logica di business, agenti
- `frontend/` — Interfaccia utente React
- `iac/` — File Terraform per il deployment
- `service/` — Dockerfile e servizi ausiliari
- `tests/` — Test automatici (unit, integration, e2e)
- `docs/` — Documentazione e materiali di progetto

## Contribuire

1. Fork del repository
2. Creare un branch feature (`git checkout -b feature/NomeFeature`)
3. Effettuare commit e push
4. Aprire una Pull Request

## Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file LICENSE per dettagli.

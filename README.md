# Trust.me

Le persone e le organizzazioni spendono una significativa quantità di tempo ed energie per determinare l'affidabilità delle proprie relazioni (personali e professionali), a volte senza la visione o la comprensione completa delle dinamiche in gioco per gestire correttamente questo  processo: questo porta a decisioni subottimali, partnership fallimentari e costi emotivi ed economici importanti, che producono risultati negativi quantificabili (ad esempio, un’azienda che gode di bassa fiducia può sottoperformare le altre).

Per ulteriori informazioni, vedi https://github.com/crypto-infinity/trust.me/tree/main/docs.

Trust.me è una piattaforma progettata proprio per valutare, verificare e presentare informazioni affidabili tramite un sistema di scoring automatizzato e agenti intelligenti, supportando l'essere umano nel processo di validazione, lasciando lui completa governance. Il progetto è composto da un backend Python (FastAPI) e un frontend React.

## Architettura

- **Backend**: Python, FastAPI, LangChain, agenti modulari per scraping, verifica, scoring e ricerca.
- **Frontend**: React, Vite, interfaccia moderna per la presentazione dei risultati e autenticazione - *attualmente in sviluppo*.

## Funzionalità principali

- **Scraping e raccolta dati**: Estrazione automatica di informazioni da fonti web.
- **Verifica e scoring**: Valutazione dell'affidabilità tramite agenti e algoritmi personalizzati.
- **Interfaccia utente**: Visualizzazione dei risultati, login e gestione utenti.

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
- `service/` — Dockerfile e servizi ausiliari
- `tests/` — Test automatici (unit, integration, e2e)
- `docs/` — Documentazione, studi e materiali di progetto

## Contribuire - se desiderate!

1. Fork del repository
2. Creare un branch feature (`git checkout -b feature/NomeFeature`)
3. Effettuare commit e push
4. Aprire una Pull Request

## Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file LICENSE per dettagli.

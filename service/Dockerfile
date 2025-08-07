# Dockerfile per FastAPI backend
FROM python:3.12-slim

# Imposta la working directory
WORKDIR /app

# Copia requirements e installa dipendenze
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il backend (inclusi agent e main.py)
COPY backend/ .

# Espone la porta 8000
EXPOSE 8000

# Comando di avvio FastAPI (uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

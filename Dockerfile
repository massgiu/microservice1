# Specifica l'immagine base da cui partire.
# Usiamo un'immagine Python 3.9 basata su Debian "buster" (una versione di Linux),
# nella sua versione "slim" per essere più leggera.
FROM python:3.9-slim-buster

# Imposta la directory di lavoro all'interno del container.
# Tutti i comandi successivi (COPY, RUN, ecc.) saranno eseguiti in questa directory.
WORKDIR /app

# Copia il file requirements.txt dalla tua macchina locale alla directory /app nel container.
# Facciamo questo prima di copiare tutto il resto del codice per sfruttare il caching di Docker.
COPY requirements.txt .

# Installa tutte le dipendenze Python elencate in requirements.txt.
# --no-cache-dir serve a ridurre la dimensione finale dell'immagine eliminando i file di cache di pip.
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del codice del tuo progetto (app.py, ecc.)
# dalla directory corrente della tua macchina locale alla directory /app nel container.
COPY . .

# Espone la porta 5000.
# Questo dice a Docker che l'applicazione all'interno del container ascolterà sulla porta 5000.
# Non pubblica automaticamente la porta sul tuo host, serve solo come documentazione o per strumenti di orchestrazione.
EXPOSE 5000

# Definisce il comando che verrà eseguito quando il container viene avviato.
# Qui, avviamo il nostro microservizio Flask.
# Usiamo la forma exec (list of strings) che è preferibile per i comandi principali.
# Ora Flask cercherà il package 'app'
ENV FLASK_APP=app 
ENV FLASK_RUN_HOST=0.0.0.0

# Usa 'flask run' per semplicità in sviluppo
# Per produzione, si userebbe un server WSGI come Gunicorn o uWSGI
CMD ["flask", "run"]
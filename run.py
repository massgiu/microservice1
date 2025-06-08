# my-microservice1/run.py

# Importa la funzione create_app dal tuo pacchetto 'app'
from app import create_app

# Chiama la factory per creare l'istanza dell'applicazione
app = create_app()

if __name__ == '__main__':
    # Avvia l'applicazione in modalità debug per lo sviluppo
    # Per la produzione, useresti un server WSGI come Gunicorn
    app.run(debug=True, host='0.0.0.0', port=5000)
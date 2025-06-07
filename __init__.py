# microservice1/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 1. Inizializza db (senza collegarlo ancora all'app Flask)
# Questo rende 'db' un oggetto disponibile a livello di package.
db = SQLAlchemy()

# 2. Definisci una funzione per creare e configurare la tua applicazione
def create_app():
    app = Flask(__name__)

    # Configurazione dell'applicazione
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3. Collega db all'app Flask QUI, all'interno della funzione create_app
    db.init_app(app)

    # 4. Importa i modelli e crea le tabelle all'interno del contesto dell'applicazione
    with app.app_context():
        # Questo importa semplicemente il modulo 'models' per assicurarsi che
        # le classi dei modelli siano registrate con SQLAlchemy.
        from . import models
        db.create_all() # Crea tutte le tabelle definite nei modelli

    # 5. Importa le tue route e registrale (questo esempio presuppone app.py contiene le route)

    from . import routes  #Questo fa registrare tutte le @app.route

    return app

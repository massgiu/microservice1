# microservice1/app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# 1. Inizializza db (senza collegarlo ancora all'app Flask)
# Questo rende 'db' un oggetto disponibile a livello di package.
db = SQLAlchemy()

# 2. Definisci una funzione per creare e configurare la tua applicazione
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config) # <-- Carica la configurazione da Config
    

    # 3. Collega db all'app Flask, all'interno della funzione create_app
    db.init_app(app)

    # 4. Importa i modelli e crea le tabelle all'interno del contesto dell'applicazione
    with app.app_context():
        # Questo importa semplicemente il modulo 'models' per assicurarsi che
        # le classi dei modelli siano registrate con SQLAlchemy.
        from . import models
        db.create_all() # Crea tutte le tabelle definite nei modelli
        
    # Importa e registra la Blueprint ***
    from .main_routes import main # Importa l'istanza 'main' della Blueprint
    app.register_blueprint(main) # Registra la Blueprint con l'applicazione

    return app

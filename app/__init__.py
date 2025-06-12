# microservice1/app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# 1. Inizializza db (senza collegarlo ancora all'app Flask)
# Questo rende 'db' un oggetto disponibile a livello di package.
db = SQLAlchemy()

# 2. Definisci una funzione per creare e configurare la tua applicazione
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '54kjtb5k6n54kn654lknfsòfxsa' 
    #basedir punta alla cartella 'app'
    basedir = os.path.abspath(os.path.dirname(__file__))
    # instance_path punta a 'my-microservice1/instance'
    # Si deve salire di un livello dalla cartella 'app'
    instance_folder_path = os.path.join(basedir, '..', 'instance') # Saliamo di una cartella e crea il percorso

    if not os.path.exists(instance_folder_path):
        os.makedirs(instance_folder_path)

    # Configurazione dell'applicazione
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_folder_path, 'site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

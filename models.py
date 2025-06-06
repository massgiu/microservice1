from datetime import datetime
from . import db # Assicurati che l'import di db sia corretto (da __init__.py se usi package)

# Modello per i messaggi (già esistente)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.id}: {self.name}>"

# NUOVO Modello per i video
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # La URL del video TikTok (potrebbe essere la URL diretta o la URL embed)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True) # Descrizione opzionale
    # I tags possono essere una stringa separata da virgole per semplicità
    tags = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Video {self.id}: {self.title}>"
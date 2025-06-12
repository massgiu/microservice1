from app import db # import del db da __init__.py
from datetime import datetime

# Modello per i messaggi (già esistente)
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.id}: {self.name}>"

# Modello per i video (es di TikTok)
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # La URL del video (potrebbe essere la URL diretta o la URL embed)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True) # Descrizione opzionale
    # I tags possono essere una stringa separata da virgole per semplicità
    tags = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Video {self.id}: {self.title}>"

# Questa tabella serve a salvare solo i video di YouTube a cui associamo categorie personalizzate.
# Non salverà tutti i dettagli del video, ma solo l'ID necessario per la relazione.
class YouTubeVideo(db.Model):
    __tablename__ = 'youtube_video'  # Specifica esplicita
    id = db.Column(db.String(255), primary_key=True)

    custom_categories = db.relationship(
        'CustomCategory',
        secondary='video_custom_category_association',
        back_populates='videos',
        lazy='dynamic'  # opzionale, per coerenza con l'altro lato
    )

    def __repr__(self):
        return f'<YouTubeVideo {self.id}>'

# Define the association table (can be defined before or after the models)
video_custom_category_association = db.Table(
    'video_custom_category_association',
    db.Column('youtube_video_id', db.String(255), db.ForeignKey('youtube_video.id'), primary_key=True),
    db.Column('custom_category_id', db.Integer, db.ForeignKey('custom_category.id'), primary_key=True)
)

class CustomCategory(db.Model):
    __tablename__ = 'custom_category'  # Anche qui
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))  # puoi anche mettere nullable=False se serve

    videos = db.relationship(
        'YouTubeVideo',
        secondary='video_custom_category_association',
        back_populates='custom_categories',
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<CustomCategory {self.name}>'
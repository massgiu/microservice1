# microservice1/add_videos.py

# Importa la funzione create_app() e l'istanza globale di db da __init__.py
from . import create_app, db
from .models import Video # Importa il tuo modello Video
from datetime import datetime # Assicurati di importare datetime se lo usi

# Crea l'istanza dell'applicazione chiamando la factory
app = create_app()

# Entra nel contesto dell'applicazione 'app' per poter interagire con db
with app.app_context():
    # Esempio di URL embed di TikTok (dovrai trovarne uno vero per testare)
    # Questi URL possono essere diversi a seconda della versione dell'API di TikTok
    sample_video_url_1 = "https://www.tiktok.com/embed/v2/7374768374938363649" # Questo è un esempio, non reale
    sample_video_url_2 = "https://www.tiktok.com/embed/v2/7374768374938363650" # Questo è un esempio, non reale

    video1 = Video(
        url=sample_video_url_1,
        title="Il mio primo TikTok",
        description="Un video divertente!",
        tags="funny, cat"
    )
    video2 = Video(
        url=sample_video_url_2,
        title="Ricetta Veloce",
        description="Come fare la pizza in 5 minuti",
        tags="cooking, food"
    )

    db.session.add(video1)
    db.session.add(video2)
    db.session.commit()
    print("Video di esempio aggiunti al database!")
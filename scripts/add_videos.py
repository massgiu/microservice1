# microservice1/scripts/add_videos.py

import sys
import os

# Ottieni il percorso della directory di questo script ('scripts/')
script_dir = os.path.dirname(__file__)
# Risali di un livello per ottenere il percorso della radice del progetto ('my-microservice1/')
project_root = os.path.abspath(os.path.join(script_dir, '..'))

# Aggiungi la radice del progetto al percorso di ricerca di Python
# sys.path.insert(0, ...) lo aggiunge all'inizio per dargli priorità
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# Importa la funzione create_app() e l'istanza globale di db da __init__.py
from app import create_app, db
from app.models import Video # Importa il tuo modello Video
from datetime import datetime # Assicurati di importare datetime se lo usi

# Crea l'istanza dell'applicazione chiamando la factory
app = create_app()

# Entra nel contesto dell'applicazione 'app' per poter interagire con db
with app.app_context():
    # Esempio di URL embed di TikTok (dovrai trovarne uno vero per testare)
    # Questi URL possono essere diversi a seconda della versione dell'API di TikTok
    # Esempio di come dovrebbero essere i video_to_add:
    videos_to_add = [
        {"url": "https://www.tiktok.com/embed/7361664188730877216", "title": "Gatto Pazzo", "description": "Un gatto che fa acrobazie assurde.", "tags": "gatto, divertente, animali"},
        {"url": "https://www.tiktok.com/embed/7376045542861217056", "title": "Ricetta Veloce", "description": "Torta al cioccolato in 5 minuti.", "tags": "cucina, dolce, ricetta, veloce"},
        {"url": "https://www.tiktok.com/embed/7370395780517565729", "title": "Cane che Balla", "description": "Un simpatico cane che balla la salsa.", "tags": "cane, divertente, animali, ballo"},
        {"url": "https://www.tiktok.com/embed/7376483562370778401", "title": "Consigli di Studio", "description": "Tecniche efficaci per memorizzare velocemente.", "tags": "studio, apprendimento, consigli"},
        {"url": "https://www.tiktok.com/embed/736181966453966570", "title": "Drone Fantastico", "description": "Volo mozzafiato con il drone al tramonto.", "tags": "drone, natura, paesaggio, volo"}
    ]
    for elem in videos_to_add:
        video = Video(
            url=elem["url"],
            title=elem["title"],
            description=elem["description"],
            tags=elem["tags"]
        )
        db.session.add(video)
    db.session.commit()

    
    print("Video di esempio aggiunti al database!")
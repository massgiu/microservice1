# my-microservice1/app/youtube_service.py

from googleapiclient.discovery import build
import os
import datetime
import sys

# Importa le configurazioni dal file config.py
# Cerchiamo prima in config.py, poi nelle variabili d'ambiente
try:
    from config import YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID
except ImportError:
    # Fallback per variabili d'ambiente se config.py non è presente o non contiene le variabili
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
    YOUTUBE_CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID")
    if not YOUTUBE_API_KEY or not YOUTUBE_CHANNEL_ID:
        print("ERRORE: Chiave API o ID Canale YouTube non configurati.")
        print("Assicurati di avere un file 'config.py' nella root del progetto con YOUTUBE_API_KEY e YOUTUBE_CHANNEL_ID,")
        print("oppure di averle impostate come variabili d'ambiente.")
        sys.exit("Configurazione API mancante. Impossibile procedere.")


YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_youtube_service():
    """Restituisce un'istanza del servizio YouTube Data API v3."""
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

def get_latest_video(channel_id=YOUTUBE_CHANNEL_ID):
    """
    Recupera i dettagli dell'ultimo video pubblicato su un canale YouTube.
    Restituisce un dizionario con titolo, descrizione, URL dell'embed e URL della thumbnail,
    o None se non trova video o ci sono errori.
    """
    if not YOUTUBE_API_KEY or not YOUTUBE_CHANNEL_ID: # Controllo per chiavi non impostate o vuote
        print("ERRORE: API Key o Channel ID non configurati per il recupero video.")
        return None

    try:
        youtube = get_youtube_service()
        
        search_response = youtube.search().list(
            channelId=channel_id,
            type="video",
            order="date", # Ordina per data per ottenere il più recente
            part="id,snippet",
            maxResults=1, # Vogliamo solo l'ultimo
            q="" # Query vuota richiesta per la ricerca per canale
        ).execute()

        videos = search_response.get("items", [])
        
        if videos:
            latest_video_data = videos[0]
            video_id = latest_video_data["id"]["videoId"]
            title = latest_video_data["snippet"]["title"]
            description = latest_video_data["snippet"]["description"]
            thumbnail_url = latest_video_data["snippet"]["thumbnails"]["high"]["url"]
            
            # URL standard per l'embed di YouTube
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            
            return {
                "id": video_id,
                "title": title,
                "description": description,
                "embed_url": embed_url,
                "thumbnail_url": thumbnail_url
            }
        else:
            return None # Nessun video trovato

    except Exception as e:
        print(f"Errore durante il recupero dell'ultimo video di YouTube: {e}")
        # Messaggi di errore generici, la diagnosi è stata fatta dal debug_api_build.py
        return None

def get_all_videos_from_channel(channel_id=YOUTUBE_CHANNEL_ID, max_results=25, category_id=None):
    """
    Recupera una lista di video da un canale YouTube, con opzione di filtro per categoria.
    Restituisce una lista di dizionari con dettagli del video.
    """
    if not YOUTUBE_API_KEY or not YOUTUBE_CHANNEL_ID: 
        print("ERRORE: API Key o Channel ID non configurati per il recupero video.")
        return []

    youtube = get_youtube_service()
    all_videos = []
    next_page_token = None
    current_results_count = 0

    while current_results_count < max_results:
        try:
            results_to_fetch = min(max_results - current_results_count, 50)
            
            # Aggiunto 'videoCategoryId' se specificato
            search_params = {
                "channelId": channel_id,
                "type": "video",
                "order": "date",
                "part": "id,snippet",
                "maxResults": results_to_fetch,
                "pageToken": next_page_token,
                "q": ""
            }
            if category_id:
                search_params["videoCategoryId"] = category_id

            search_response = youtube.search().list(
                **search_params
            ).execute()

            for search_result in search_response.get("items", []):
                if search_result["id"]["kind"] == "youtube#video":
                    video_id = search_result["id"]["videoId"]
                    title = search_result["snippet"]["title"]
                    description = search_result["snippet"]["description"]
                    thumbnail_url = search_result["snippet"]["thumbnails"]["high"]["url"]
                    published_at_str = search_result["snippet"]["publishedAt"]
                    
                    published_at = datetime.datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))

                    all_videos.append({
                        "id": video_id,
                        "title": title,
                        "description": description,
                        "embed_url": f"http://www.youtube.com/embed/{video_id}", # Correzione URL
                        "thumbnail_url": thumbnail_url,
                        "published_at": published_at
                    })
                    current_results_count += 1
            
            next_page_token = search_response.get("nextPageToken")
            if not next_page_token or current_results_count >= max_results:
                break

        except Exception as e:
            print(f"Errore durante il recupero dei video di YouTube: {e}")
            break
    
    all_videos.sort(key=lambda x: x['published_at'], reverse=True)
    return all_videos

def get_video_categories(region_code="IT"):
    """
    Recupera un elenco delle categorie video di YouTube per una data regione.
    Restituisce una lista di dizionari { 'id': 'category_id', 'title': 'Category Name' }
    """
    try:
        youtube = get_youtube_service()
        response = youtube.videoCategories().list(
            part="snippet",
            regionCode=region_code
        ).execute()

        categories = []
        for item in response.get('items', []):
            categories.append({
                'id': item['id'],
                'title': item['snippet']['title']
            })
        return categories
    except Exception as e:
        print(f"Errore durante il recupero delle categorie video di YouTube: {e}")
        return []

# Rimosso il blocco if __name__ == "__main__": per test diretti.
# Queste funzioni verranno chiamate dall'applicazione Flask.
if __name__ == "__main__":
    print("--- Test dell'ultimo video ---")
    latest = get_latest_video()
    if latest:
        print(f"ID Video: {latest.get('id')}")
        print(f"Titolo: {latest.get('title')}")
        print(f"Descrizione: {latest.get('description')}")
        print(f"URL Embed: {latest.get('embed_url')}")
        print(f"URL Thumbnail: {latest.get('thumbnail_url')}")
    else:
        print("Nessun ultimo video trovato o errore di configurazione/rete.")

    print("\n--- Test di tutti i video (primi 3) ---")
    all_vids = get_all_videos_from_channel(max_results=3)
    if all_vids:
        for i, v in enumerate(all_vids):
            print(f"\nVideo {i+1}:")
            print(f"  Titolo: {v.get('title')}")
            print(f"  Pubblicato il: {v.get('published_at').strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  URL Embed: {v.get('embed_url')}")
    else:
        print("Nessun video trovato o errore di configurazione/rete.")

    print("Tentativo di recupero categorie YouTube...")
    categories = get_video_categories()
    if categories:
        print(f"Recuperate {len(categories)} categorie:")
        for cat in categories:
            print(f"  - ID: {cat['id']}, Titolo: {cat['title']}")
    else:
        print("Nessuna categoria recuperata o errore. Controlla il messaggio sopra.")

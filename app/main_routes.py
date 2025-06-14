# my-microservice1/app/main_routes.py

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from datetime import datetime
import re # Importa re per espressioni regolari per pulire i tag

# Importa l'istanza di db dal modulo principale (__init__.py)
# Questo è il modo standard per accedere all'oggetto db da una Blueprint
from . import db
from .models import Message, Video, CustomCategory, YouTubeVideo 

# Importa le funzioni per interagire con l'API di YouTube
from .youtube_service import get_latest_video, get_all_videos_from_channel, get_video_categories 

# Inizializza la Blueprint
# 'main' è il nome della tua Blueprint. Sarà usato nei nomi degli endpoint (es. 'main.index')
main = Blueprint('main', __name__) #Questa instanza sarà usata in __init__

# Route per la pagina principale con il form e la lista dei messaggi
@main.route('/', methods=['GET','POST'], endpoint='index_page')
def home():
    error = None
    success = None
    #called by index.html after submit pressed
    if request.method == 'POST':
        # Recupera i dati dal form
        name = request.form['name']
        message_content = request.form['message_content']

        # Validazione base dei dati
        if not name or not message_content:
            error = "Nome e messaggio non possono essere vuoti!"
        else:
            try:
                # Crea una nuova istanza del modello Message
                new_message = Message(name=name, message_content=message_content)

                # Aggiungi il nuovo messaggio alla sessione del database
                db.session.add(new_message)
                # Esegui il commit per salvare i dati nel database
                db.session.commit()
                success = "Messaggio inviato con successo!"
            except Exception as e:
                db.session.rollback() # Annulla l'operazione in caso di errore
                error = f"Errore durante il salvataggio del messaggio: {e}"

    # Quando carichiamo la pagina per la prima volta (metodo GET o POST),
    # recuperiamo tutti i messaggi dal database e li memorizzamo nella lista all_messages
    all_messages = db.session.execute(db.select(Message).order_by(Message.created_at.desc())).scalars().all()
    # Passiamo i messaggi al template
    return render_template('index.html', messages=all_messages, error=error, success=success)

    """ @app_instance.route('/video', methods=['GET'], endpoint='video_page')
    def video_page():
        all_videos = db.session.execute(db.select(Video).order_by(Video.created_at.desc())).scalars().all()
        return render_template('video.html',videos=all_videos) """
    
# Questa route ora accetta un parametro opzionale 'tag_filter' nell'URL
@main.route('/video', methods=['GET'], endpoint='video_page')
@main.route('/video/custom_category/<int:custom_category_id>', methods=['GET'], endpoint='video_page')
def video_page(custom_category_id=None): # custom_category sarà None se non presente nell'URL

    custom_categories = db.session.execute(db.select(CustomCategory).order_by(CustomCategory.name)).scalars().all()
    print(f"DEBUG: Categorie recuperate dal DB per il menu: {[c.name for c in custom_categories]}") # DEBUG

    # 2. Determina quali video_id di YouTube dobbiamo mostrare in base alla categoria selezionata
    youtube_video_ids_to_display = []
    if custom_category_id:
        selected_category = db.session.get(CustomCategory, custom_category_id)
        if selected_category:
            # Questa è la riga critica che recupera gli ID dei video dal tuo DB locale
            youtube_video_ids_to_display = [video.id for video in selected_category.videos.all()]
            print(f"DEBUG: Categoria selezionata ID={custom_category_id}, Nome='{selected_category.name}'") # DEBUG
            print(f"DEBUG: ID Video associati nel tuo DB: {youtube_video_ids_to_display}") # DEBUG
        else:
            print(f"DEBUG: Categoria con ID {custom_category_id} non trovata nel tuo DB.") # DEBUG
            youtube_video_ids_to_display = []
    else:
        print("DEBUG: Nessuna categoria personalizzata selezionata (Mostra tutti i video del canale).") # DEBUG
    
    # 3. Recupera i video dal canale YouTube tramite API
    # Assicurati che max_results sia sufficientemente alto per recuperare i video che ti aspetti
    all_video_from_youtube = get_all_videos_from_channel(max_results=50) # Puoi aumentare questo numero (es. 100)
    print(f"DEBUG: Video recuperati dall'API di YouTube (totale {len(all_video_from_youtube)}): {[v['id'] for v in all_video_from_youtube[:5]]}...") # Mostra i primi 5 ID

    # 4. Filtra i video ottenuti dall'API in base alla categoria selezionata
    filtered_videos_by_category = []
    if youtube_video_ids_to_display: # Se abbiamo una lista di ID da filtrare (categoria selezionata)
        for video_data in all_video_from_youtube:
            if video_data['id'] in youtube_video_ids_to_display:
                filtered_videos_by_category.append(video_data)
        print(f"DEBUG: Dopo filtro categoria, video rimasti: {len(filtered_videos_by_category)}") # DEBUG
    else:
        # Se non c'è una categoria selezionata, o la categoria selezionata non ha video associati nel DB
        filtered_videos_by_category = all_video_from_youtube
        print(f"DEBUG: Nessun filtro categoria applicato, mostrando tutti i video del canale (totale: {len(filtered_videos_by_category)})") # DEBUG

    # 5. Applica il filtro di ricerca testuale (se presente)
    search_query = request.args.get('q', '').strip()
    final_filtered_videos = []
    if search_query:
        for video in filtered_videos_by_category:
            if search_query.lower() in video['title'].lower() or \
               search_query.lower() in video['description'].lower():
                final_filtered_videos.append(video)
        print(f"DEBUG: Dopo filtro ricerca, video rimasti: {len(final_filtered_videos)}") # DEBUG
    else:
        final_filtered_videos = filtered_videos_by_category
        print(f"DEBUG: Nessun filtro ricerca applicato. Video finali: {len(final_filtered_videos)}") # DEBUG


    return render_template('video2.html', 
                           videos=final_filtered_videos, 
                           custom_categories=custom_categories, 
                           current_filter_category_id=custom_category_id, 
                           current_search_query=search_query)

# GESTIONE DELLE CATEGORIE
# Pagina principale di gestione delle categorie
@main.route('/categories', methods=['GET'], endpoint='manage_categories')
def manage_categories():
    """Mostra l'elenco di tutte le categorie personalizzate."""
    categories = db.session.execute(db.select(CustomCategory).order_by(CustomCategory.name)).scalars().all()
    return render_template('manage_categories.html', categories=categories)

#Aggiunta di una nuova categoria: controlla che il nome non sia vuoto e che non ci siano duplicat
@main.route('/categories/add', methods=['GET', 'POST'], endpoint='add_category')
def add_category():
    """Permette di aggiungere una nuova categoria personalizzata."""
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Il nome della categoria non può essere vuoto.', 'error')
            return redirect(url_for('main.add_category'))

        # Controlla se una categoria con lo stesso nome esiste già
        existing_category = db.session.execute(db.select(CustomCategory).filter_by(name=name)).scalar_one_or_none()
        if existing_category:
            flash(f"Esiste già una categoria con il nome '{name}'. Scegli un nome diverso.", 'error')
            return redirect(url_for('main.add_category'))
        
        try:
            new_category = CustomCategory(name=name, description=description)
            db.session.add(new_category)
            db.session.commit()
            flash(f"Categoria '{name}' aggiunta con successo!", 'success')
            return redirect(url_for('main.manage_categories'))
        except Exception as e:
            db.session.rollback()
            flash(f"Errore durante l'aggiunta della categoria: {e}", 'error')
            return redirect(url_for('main.add_category'))

    return render_template('add_edit_category.html', title='Aggiungi Categoria', category=None)

#form di modifica di una categoria esistente
@main.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'], endpoint='edit_category')
def edit_category(category_id):
    """Permette di modificare una categoria esistente."""
    category = db.session.get(CustomCategory, category_id)
    if not category:
        flash('Categoria non trovata.', 'error')
        return redirect(url_for('main.manage_categories'))

    if request.method == 'POST':
        new_name = request.form['name'].strip()
        new_description = request.form.get('description', '').strip()

        if not new_name:
            flash('Il nome della categoria non può essere vuoto.', 'error')
            return redirect(url_for('main.edit_category', category_id=category.id))
        
        # Controlla se il nuovo nome è già usato da un'altra categoria
        existing_category = db.session.execute(db.select(CustomCategory).filter_by(name=new_name)).scalar_one_or_none()
        if existing_category and existing_category.id != category.id:
            flash(f"Esiste già un'altra categoria con il nome '{new_name}'. Scegli un nome diverso.", 'error')
            return redirect(url_for('main.edit_category', category_id=category.id))

        try:
            category.name = new_name
            category.description = new_description
            db.session.commit()
            flash(f"Categoria '{category.name}' aggiornata con successo!", 'success')
            return redirect(url_for('main.manage_categories'))
        except Exception as e:
            db.session.rollback()
            flash(f"Errore durante l'aggiornamento della categoria: {e}", 'error')
            return redirect(url_for('main.edit_category', category_id=category.id))

    return render_template('add_edit_category.html', title='Modifica Categoria', category=category)

#Route per l'eliminazione di una categoria: è un metodo POST per maggiore sicurezza
@main.route('/categories/delete/<int:category_id>', methods=['POST'], endpoint='delete_category')
def delete_category(category_id):
    """Permette di eliminare una categoria."""
    category = db.session.get(CustomCategory, category_id)
    if not category:
        flash('Categoria non trovata.', 'error')
        return redirect(url_for('main.manage_categories'))
    
    try:
        # Nota: La relazione molti-a-molti non impone la cancellazione a cascata automatica
        # Questo elimina solo la categoria. Le associazioni nella tabella intermedia
        # verranno gestite automaticamente da SQLAlchemy quando elimini un CustomCategory
        # se db.Table è configurata correttamente.
        db.session.delete(category)
        db.session.commit()
        flash(f"Categoria '{category.name}' eliminata con successo!", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Errore durante l'eliminazione della categoria: {e}", 'error')

    return redirect(url_for('main.manage_categories'))

@main.route('/manage_video_categories', methods=['GET', 'POST'], endpoint='manage_video_categories')
def manage_video_categories():
    # 1. Recupera tutti i video dal canale YouTube (per visualizzazione)
    # Limita i risultati per non sovraccaricare la pagina se hai molti video.
    # Potresti voler implementare la paginazione qui in futuro.
    all_youtube_videos_data = get_all_videos_from_channel(max_results=50) # Recupera i dettagli dall'API

    # 2. Recupera tutte le categorie personalizzate dal DB
    custom_categories = db.session.execute(db.select(CustomCategory).order_by(CustomCategory.name)).scalars().all()

    if request.method == 'POST':
        try:
            # Per ogni video che è stato visualizzato nella form:
            for video_data in all_youtube_videos_data:
                video_id = video_data['id']
                
                # Cerca il video nel tuo database locale (YouTubeVideo model)
                # Se non esiste, crealo. È importante che esista per poter associare le categorie.
                video_in_db = db.session.execute(db.select(YouTubeVideo).filter_by(id=video_id)).scalar_one_or_none()
                if not video_in_db:
                    video_in_db = YouTubeVideo(id=video_id)
                    db.session.add(video_in_db)
                    # Non fare commit qui, lo faremo alla fine del ciclo
                
                # Rimuovi tutte le associazioni esistenti per questo video prima di ri-aggiungerle
                # Questo assicura che le checkbox deselezionate vengano gestite correttamente.
                video_in_db.custom_categories.clear()

                # Recupera le categorie selezionate per questo video_id dalla form (dopo le modifiche)
                # Le checkbox inviano i loro valori come 'video_ID-category_ID'
                selected_category_ids_for_video = request.form.getlist(f'categories_for_{video_id}')
                # per ogni categoria flaggata
                for cat_id_str in selected_category_ids_for_video:
                    cat_id = int(cat_id_str)
                    category = db.session.get(CustomCategory, cat_id)
                    if category and category not in video_in_db.custom_categories:
                        video_in_db.custom_categories.append(category)
            
            db.session.commit()
            flash('Associazioni video-categorie aggiornate con successo!', 'success')
            return redirect(url_for('main.manage_video_categories'))

        except Exception as e:
            db.session.rollback()
            flash(f"Errore durante l'aggiornamento delle associazioni: {e}", 'error')
            # Rimane sulla stessa pagina per mostrare l'errore

    # Quando la pagina viene caricata (GET) o dopo un POST fallito, prepariamo i dati:
    
    # Crea un dizionario per tenere traccia delle categorie associate a ogni video.
    # Questo è necessario per pre-selezionare le checkbox nel template.
    video_associations = {}
    for video_data in all_youtube_videos_data:
        video_id = video_data['id']
        video_in_db = db.session.execute(db.select(YouTubeVideo).filter_by(id=video_id)).scalar_one_or_none()
        if video_in_db:
            # Crea un set degli ID delle categorie associate per un accesso rapido
            video_associations[video_id] = {cat.id for cat in video_in_db.custom_categories}
        else:
            video_associations[video_id] = set() # Nessuna associazione se il video non è nel DB locale

    return render_template('manage_video_categories.html', 
                           youtube_videos=all_youtube_videos_data,
                           custom_categories=custom_categories,
                           video_associations=video_associations)


# Ottieni tutti i messaggi
@main.route('/api/messages', methods=['GET'])
def get_all_messages():
    
    # Recupera tutti i messaggi dal database, ordinati per data di creazione decrescente
    messages = db.session.execute(db.select(Message).order_by(Message.created_at.desc())).scalars().all()

    # Converte la lista di oggetti Message in una lista di dizionari Python
    # Questo è necessario perché jsonify lavora con tipi Python nativi (dizionari, liste, stringhe, numeri)
    messages_list = []
    # Ogni msg è un dizionario con 4 key
    for msg in messages:
        messages_list.append({
            'id': msg.id,
            'name': msg.name,
            'message_content': msg.message_content,
            'created_at': msg.created_at.isoformat() # Converte la data in formato stringa ISO 8601
        })

    # Restituisce la lista di dizionari come risposta JSON
    return jsonify(messages_list)

# Ottieni un singolo messaggio dal suo ID
@main.route('/api/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    # Cerca il messaggio per ID nel database
    # .first_or_404() è un metodo conveniente di Flask-SQLAlchemy
    # che restituisce l'oggetto trovato o un errore 404 se non esiste
    message = db.session.execute(db.select(Message).filter_by(id=message_id)).scalar_one_or_none()

    if message is None:
        # Se il messaggio non è stato trovato, restituisce una risposta 404 Not Found
        return jsonify({'error': 'Message not found'}), 404

    # Converte l'oggetto Message in un dizionario Python
    message_data = {
        'id': message.id,
        'name': message.name,
        'message_content': message.message_content,
        'created_at': message.created_at.isoformat()
    }

    # Restituisce il dizionario come risposta JSON
    return jsonify(message_data)

# Aggiorna un messaggio attraverso ID
@main.route('/api/messages/<int:message_id>', methods=['PUT'])
def update_message(message_id):
    # Cerca il messaggio per ID
    message = db.session.execute(db.select(Message).filter_by(id=message_id)).scalar_one_or_none()

    if message is None:
        # Se il messaggio non è stato trovato, restituisce una risposta 404 Not Found
        return jsonify({'error': 'Message not found'}), 404

    # Ottiene i dati dal corpo della richiesta (JSON)
    # request.get_json() analizza il corpo JSON della richiesta HTTP
    data = request.get_json()

    # Estrae i campi da aggiornare, fornendo un valore predefinito (quello esistente)
    # se il campo non è presente nel JSON della richiesta
    name = data.get('name', message.name)
    message_content = data.get('message_content', message.message_content)

    # Validazione base dei dati ricevuti
    if not name or not message_content:
        return jsonify({'error': 'Nome e messaggio non possono essere vuoti!'}), 400 # 400 Bad Request

    try:
        # Aggiorna i campi del messaggio con i nuovi dati
        message.name = name
        message.message_content = message_content

        # Esegue il commit per salvare le modifiche nel database
        db.session.commit()

        # Restituisce il messaggio aggiornato come JSON
        updated_message_data = {
            'id': message.id,
            'name': message.name,
            'message_content': message.message_content,
            'created_at': message.created_at.isoformat()
        }
        return jsonify(updated_message_data), 200

    except Exception as e:
        db.session.rollback() # Annulla l'operazione in caso di errore
        return jsonify({'error': f'Error updating message: {e}'}), 500
        
# Cancella un messaggio per ID - DELETE convenzione standard per la rimozione di risorse in un'API RESTful
@main.route('/api/messages/<int:message_id>', methods=['DELETE']) 
def delete_message(message_id):
    message = db.session.execute(db.select(Message).filter_by(id=message_id)).scalar_one_or_none()

    if message is None:
        # Se il messaggio non è stato trovato, restituisce una risposta 404 Not Found
        return jsonify({'error': 'Message not found'}), 404

    try:
        # Se il messaggio esiste, lo elimina dalla sessione del database
        db.session.delete(message)
        # Esegue il commit per salvare le modifiche nel database
        db.session.commit()
        # Restituisce una risposta di successo (status 204 No Content è comune per DELETE)
        return jsonify({'message': 'Message deleted successfully'}), 200
        # Oppure puoi usare return '', 204 se non vuoi un corpo nella risposta di successo
    except Exception as e:
        db.session.rollback() # Annulla l'operazione in caso di errore
        return jsonify({'error': f'Error deleting message: {e}'}), 500

# Endpoint di "health check"
# Un endpoint di health check serve per verificare che il servizio sia attivo e funzionante.
@main.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Microservizio attivo!"}), 200

# Endpoint API semplice: /greet
# Questo endpoint risponde a una richiesta GET e può opzionalmente prendere un nome.
@main.route('/greet', methods=['GET'])
def greet_user():
    # Recuperiamo il parametro 'name' dalla query string (es. /greet?name=Alice)
    name = request.args.get('name', 'Ospite') # 'Ospite' è il valore di default se 'name' non è fornito

    # Restituiamo una risposta JSON
    return jsonify({"message": f"Ciao, {name}!"}), 200



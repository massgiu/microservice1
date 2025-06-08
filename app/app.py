from flask import Flask, jsonify, request, render_template # Aggiungi render_template per le pagine HTML

from .models import Message, Video # quel punto indica dove c'è __init__
from datetime import datetime # Assicurati che sia presente se lo usi in Message/Video models


# Crea l'istanza dell'applicazione chiamando la factory function
#app = create_app()
def register_routes(app_instance, db_instance): # Riceve l'istanza di app e db

    # Route per la pagina principale con il form e la lista dei messaggi
    @app_instance.route('/', methods=['GET','POST'], endpoint='index_page')
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
                    db_instance.session.add(new_message)
                    # Esegui il commit per salvare i dati nel database
                    db_instance.session.commit()
                    success = "Messaggio inviato con successo!"
                except Exception as e:
                    db_instance.session.rollback() # Annulla l'operazione in caso di errore
                    error = f"Errore durante il salvataggio del messaggio: {e}"

        # Quando carichiamo la pagina per la prima volta (metodo GET o POST),
        # recuperiamo tutti i messaggi dal database e li memorizzamo nella lista all_messages
        all_messages = db_instance.session.execute(db_instance.select(Message).order_by(Message.created_at.desc())).scalars().all()
        # Passiamo i messaggi al template
        return render_template('index.html', messages=all_messages, error=error, success=success)

    @app_instance.route('/video', endpoint='video_page')
    def video_page():
        all_videos = db_instance.session.execute(db_instance.select(Video).order_by(Video.created_at.desc())).scalars().all()
        return render_template('video.html',videos=all_videos)

    # Ottieni tutti i messaggi
    @app_instance.route('/api/messages', methods=['GET'])
    def get_all_messages():
        
        # Recupera tutti i messaggi dal database, ordinati per data di creazione decrescente
        messages = db_instance.session.execute(db_instance.select(Message).order_by(Message.created_at.desc())).scalars().all()

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
    @app_instance.route('/api/messages/<int:message_id>', methods=['GET'])
    def get_message(message_id):
        # Cerca il messaggio per ID nel database
        # .first_or_404() è un metodo conveniente di Flask-SQLAlchemy
        # che restituisce l'oggetto trovato o un errore 404 se non esiste
        message = db_instance.session.execute(db_instance.select(Message).filter_by(id=message_id)).scalar_one_or_none()

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
    @app_instance.route('/api/messages/<int:message_id>', methods=['PUT'])
    def update_message(message_id):
        # Cerca il messaggio per ID
        message = db_instance.session.execute(db_instance.select(Message).filter_by(id=message_id)).scalar_one_or_none()

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
            db_instance.session.commit()

            # Restituisce il messaggio aggiornato come JSON
            updated_message_data = {
                'id': message.id,
                'name': message.name,
                'message_content': message.message_content,
                'created_at': message.created_at.isoformat()
            }
            return jsonify(updated_message_data), 200

        except Exception as e:
            db_instance.session.rollback() # Annulla l'operazione in caso di errore
            return jsonify({'error': f'Error updating message: {e}'}), 500
        
    # Cancella un messaggio per ID - DELETE convenzione standard per la rimozione di risorse in un'API RESTful
    @app_instance.route('/api/messages/<int:message_id>', methods=['DELETE']) 
    def delete_message(message_id):
        message = db_instance.session.execute(db_instance.select(Message).filter_by(id=message_id)).scalar_one_or_none()

        if message is None:
            # Se il messaggio non è stato trovato, restituisce una risposta 404 Not Found
            return jsonify({'error': 'Message not found'}), 404

        try:
            # Se il messaggio esiste, lo elimina dalla sessione del database
            db_instance.session.delete(message)
            # Esegue il commit per salvare le modifiche nel database
            db_instance.session.commit()
            # Restituisce una risposta di successo (status 204 No Content è comune per DELETE)
            return jsonify({'message': 'Message deleted successfully'}), 200
            # Oppure puoi usare return '', 204 se non vuoi un corpo nella risposta di successo
        except Exception as e:
            db_instance.session.rollback() # Annulla l'operazione in caso di errore
            return jsonify({'error': f'Error deleting message: {e}'}), 500

    # Endpoint di "health check"
    # Un endpoint di health check serve per verificare che il servizio sia attivo e funzionante.
    @app_instance.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "Microservizio attivo!"}), 200

    # Endpoint API semplice: /greet
    # Questo endpoint risponde a una richiesta GET e può opzionalmente prendere un nome.
    @app_instance.route('/greet', methods=['GET'])
    def greet_user():
        # Recuperiamo il parametro 'name' dalla query string (es. /greet?name=Alice)
        name = request.args.get('name', 'Ospite') # 'Ospite' è il valore di default se 'name' non è fornito

        # Restituiamo una risposta JSON
        return jsonify({"message": f"Ciao, {name}!"}), 200

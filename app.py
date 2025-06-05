from flask import Flask, jsonify, request, render_template # Aggiungi render_template per le pagine HTML
from flask_sqlalchemy import SQLAlchemy # Importa SQLAlchemy

# Inizializziamo l'applicazione Flask
app = Flask(__name__)

# --- Configurazione del Database ---
# Specifica l'URI del database. Per SQLite, è 'sqlite:///nome_file.db'.
# Il database verrà creato nella stessa cartella di app.py.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# Disabilita il tracciamento delle modifiche, che consuma memoria extra e non è strettamente necessario per piccoli progetti.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inizializza l'istanza di SQLAlchemy con l'app Flask
db = SQLAlchemy(app)

# --- Definizione del Modello del Database ---
# Creiamo un modello per immagazzinare i messaggi/feedback dal form.
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Campo per il nome (può essere nullo, ma lo rendiamo non nullo per semplicità)
    name = db.Column(db.String(80), nullable=False)
    # Campo per il contenuto del messaggio (testo lungo)
    message_content = db.Column(db.Text, nullable=False)
    # Campo per la data di creazione (default alla data/ora corrente)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Metodo per una rappresentazione leggibile dell'oggetto Message
    def __repr__(self):
        return f"<Message {self.id}: {self.name}>"
    
# Route per la pagina principale con il form e la lista dei messaggi
@app.route('/', methods=['GET','POST'])
def home():
    error = None
    success = None

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
                with app.app_context(): # Necessario per operazioni DB fuori contesto richiesta
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

# Ottieni tutti i messaggi
@app.route('/api/messages', methods=['GET'])
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

# Ottieni un singolo messaggio per ID
@app.route('/api/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    with app.app_context():
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

# Endpoint di "health check"
# Un endpoint di health check serve per verificare che il servizio sia attivo e funzionante.
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Microservizio attivo!"}), 200

# Endpoint API semplice: /greet
# Questo endpoint risponde a una richiesta GET e può opzionalmente prendere un nome.
@app.route('/greet', methods=['GET'])
def greet_user():
    # Recuperiamo il parametro 'name' dalla query string (es. /greet?name=Alice)
    name = request.args.get('name', 'Ospite') # 'Ospite' è il valore di default se 'name' non è fornito

    # Restituiamo una risposta JSON
    return jsonify({"message": f"Ciao, {name}!"}), 200

# Punto di ingresso dell'applicazione
# Questo blocco assicura che il server Flask venga avviato solo quando il file app.py viene eseguito direttamente.
if __name__ == '__main__':
    # Avviamo il server Flask in modalità debug (utile per lo sviluppo, ricarica automaticamente le modifiche)
    # Il server sarà in ascolto su http://127.0.0.1:5000
    app.run(debug=True, host='0.0.0.0', port=5000)
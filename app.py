from flask import Flask, jsonify, request # Importiamo i moduli necessari

# Inizializziamo l'applicazione Flask
app = Flask(__name__)

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
    app.run(debug=True, port=5000)
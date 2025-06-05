import os

def clean_requirements_file(filename="requirements.txt"):
    """
    Pulisce il file requirements.txt rimuovendo le righe
    che contengono percorsi locali (es. '@ file:///').
    """
    try:
        with open(filename, 'r') as f_in:
            lines = f_in.readlines()

        cleaned_lines = []
        for line in lines:
            # Ignora le righe che contengono '@ file:///'
            if '@ file:///' not in line:
                cleaned_lines.append(line)
            else:
                # Per le righe con '@ file:///', estrai solo il nome del pacchetto e la versione.
                # Questo gestisce casi come 'Flask @ file:///...'
                parts = line.split(' @ file:///')
                if len(parts) > 0 and parts[0].strip():
                    # Aggiungiamo solo la parte prima del '@'
                    cleaned_lines.append(parts[0].strip() + '\n')

        # Rimuovi eventuali duplicati o righe vuote e ordina per pulizia
        cleaned_lines = sorted(list(set([line.strip() for line in cleaned_lines if line.strip()])))

        with open(filename, 'w') as f_out:
            for line in cleaned_lines:
                f_out.write(line + '\n') # Aggiungi newline per ogni riga

        print(f"File '{filename}' pulito con successo. Rimossi i percorsi locali.")

    except FileNotFoundError:
        print(f"Errore: Il file '{filename}' non è stato trovato.")
    except Exception as e:
        print(f"Si è verificato un errore durante la pulizia del file: {e}")

if __name__ == '__main__':
    clean_requirements_file()
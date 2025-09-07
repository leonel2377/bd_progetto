from app import create_app
from app.models import Utente, CompagniaAerea, Volo, Aeroporto, Prenotazione, Biglietto

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Utente': Utente,
        'CompagniaAerea': CompagniaAerea,
        'Volo': Volo,
        'Aeroporto': Aeroporto,
        'Prenotazione': Prenotazione,
        'Biglietto': Biglietto
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
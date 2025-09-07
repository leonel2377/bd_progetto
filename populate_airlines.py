from app import create_app, db
from app.models import CompagniaAerea, Utente
from werkzeug.security import generate_password_hash

def populate_airlines():
    """Popola il database con alcune compagnie aeree di esempio"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verifica se ci sono già compagnie nel database
            if CompagniaAerea.query.first():
                print("Il database contiene già delle compagnie aeree. Vuoi procedere comunque? (s/n)")
                if input().lower() != 's':
                    return
                # Elimina tutte le compagnie esistenti
                CompagniaAerea.query.delete()
                db.session.commit()
            
            # Lista di compagnie aeree di esempio
            compagnie = [
                {
                    'nome': 'Alitalia',
                    'codice_iata': 'AZ',
                    'sede': 'Roma',
                    'email': 'admin@alitalia.it',
                    'password': 'az123'  # Password più corta
                },
                {
                    'nome': 'Ryanair',
                    'codice_iata': 'FR',
                    'sede': 'Dublino',
                    'email': 'admin@ryanair.com',
                    'password': 'fr123'  # Password più corta
                },
                {
                    'nome': 'EasyJet',
                    'codice_iata': 'U2',
                    'sede': 'Luton',
                    'email': 'admin@easyjet.com',
                    'password': 'u2123'  # Password più corta
                },
                {
                    'nome': 'Lufthansa',
                    'codice_iata': 'LH',
                    'sede': 'Colonia',
                    'email': 'admin@lufthansa.com',
                    'password': 'lh123'  # Password più corta
                },
                {
                    'nome': 'Air France',
                    'codice_iata': 'AF',
                    'sede': 'Parigi',
                    'email': 'admin@airfrance.com',
                    'password': 'af123'  # Password più corta
                }
            ]
            
            # Inserisci le compagnie nel database
            for comp in compagnie:
                # Crea l'utente amministratore della compagnia
                admin = Utente(
                    email=comp['email'],
                    password=generate_password_hash(comp['password']),
                    nome='Admin',
                    cognome=comp['nome'],
                    is_airline=True
                )
                db.session.add(admin)
                db.session.flush()  # Per ottenere l'ID dell'utente
                
                # Crea la compagnia aerea
                compagnia = CompagniaAerea(
                    utente_id=admin.id,
                    nome_compagnia=comp['nome'],
                    codice_iata=comp['codice_iata'],
                    sede_legale=comp['sede']
                )
                db.session.add(compagnia)
            
            db.session.commit()
            print(f"Inserite {len(compagnie)} compagnie aeree nel database con successo!")
            print("\nCredenziali di accesso per le compagnie:")
            for comp in compagnie:
                print(f"{comp['nome']}: {comp['email']} / {comp['password']}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Errore durante l'inserimento delle compagnie aeree: {str(e)}")

if __name__ == '__main__':
    populate_airlines() 
from app import create_app, db
from app.models import Volo, CompagniaAerea, Aeroporto
from datetime import datetime, timedelta
import random

def populate_flights():
    """Popola il database con voli di esempio"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verifica se ci sono già voli nel database
            if Volo.query.first():
                print("Il database contiene già dei voli. Vuoi procedere comunque? (s/n)")
                if input().lower() != 's':
                    return
                # Elimina tutti i voli esistenti
                Volo.query.delete()
                db.session.commit()
            
            # Recupera compagnie e aeroporti
            compagnie = CompagniaAerea.query.all()
            aeroporti = Aeroporto.query.all()
            
            if not compagnie:
                print("Errore: Nessuna compagnia aerea trovata nel database.")
                print("Esegui prima populate_airlines.py")
                return
                
            if not aeroporti:
                print("Errore: Nessun aeroporto trovato nel database.")
                print("Esegui prima populate_airports.py")
                return
            
            # Genera voli per i prossimi 7 giorni
            oggi = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            voli_generati = 0
            
            for giorno in range(7):
                data = oggi + timedelta(days=giorno)
                
                # Per ogni compagnia, genera alcuni voli
                for compagnia in compagnie:
                    # Genera 3-5 voli al giorno per compagnia
                    num_voli = random.randint(3, 5)
                    
                    for _ in range(num_voli):
                        # Seleziona aeroporti casuali (diversi tra loro)
                        aeroporto_partenza = random.choice(aeroporti)
                        aeroporto_arrivo = random.choice([a for a in aeroporti if a.id != aeroporto_partenza.id])
                        
                        # Genera orari casuali
                        ora_partenza = random.randint(6, 20)  # Tra le 6:00 e le 20:00
                        minuto_partenza = random.choice([0, 15, 30, 45])
                        durata_volo = random.randint(1, 4)  # 1-4 ore
                        
                        data_partenza = data.replace(hour=ora_partenza, minute=minuto_partenza)
                        data_arrivo = data_partenza + timedelta(hours=durata_volo)
                        
                        # Genera numero volo
                        numero_volo = f"{compagnia.codice_iata}{random.randint(1000, 9999)}"
                        
                        # Genera posti e prezzi
                        posti_totali = random.randint(100, 200)
                        posti_economy = int(posti_totali * 0.7)  # 70% economy
                        posti_business = int(posti_totali * 0.2)  # 20% business
                        posti_first = posti_totali - posti_economy - posti_business  # 10% first
                        
                        # Prezzi base per tratta
                        prezzo_base = random.randint(50, 200)
                        prezzo_economy = prezzo_base
                        prezzo_business = prezzo_base * 2
                        prezzo_first = prezzo_base * 3
                        
                        # Crea il volo
                        volo = Volo(
                            compagnia_id=compagnia.id,
                            numero_volo=numero_volo,
                            departure_airport_id=aeroporto_partenza.id,
                            arrival_airport_id=aeroporto_arrivo.id,
                            data_partenza=data_partenza,
                            data_arrivo=data_arrivo,
                            posti_totali=posti_totali,
                            posti_economy=posti_economy,
                            posti_business=posti_business,
                            posti_first=posti_first,
                            prezzo_economy=prezzo_economy,
                            prezzo_business=prezzo_business,
                            prezzo_first=prezzo_first
                        )
                        
                        db.session.add(volo)
                        voli_generati += 1
            
            db.session.commit()
            print(f"Inseriti {voli_generati} voli nel database con successo!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Errore durante l'inserimento dei voli: {str(e)}")

if __name__ == '__main__':
    populate_flights() 
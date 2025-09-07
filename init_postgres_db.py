from app import create_app, db
from app.models import Utente, CompagniaAerea, Aeroporto, Volo, Prenotazione, Biglietto
from datetime import datetime, timedelta
import random

def init_postgres_database():
    app = create_app()
    
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        print("✅ Tables créées avec succès!")
        
        # Vérifier si les données existent déjà
        if Aeroporto.query.first():
            print("⚠️ La base de données contient déjà des données. Suppression...")
            db.session.query(Biglietto).delete()
            db.session.query(Prenotazione).delete()
            db.session.query(Volo).delete()
            db.session.query(CompagniaAerea).delete()
            db.session.query(Utente).delete()
            db.session.query(Aeroporto).delete()
            db.session.commit()
        
        # Ajouter des aéroports de test
        aeroporti = [
            {'codice_iata': 'FCO', 'nome': 'Leonardo da Vinci', 'città': 'Roma', 'paese': 'Italia'},
            {'codice_iata': 'MXP', 'nome': 'Malpensa', 'città': 'Milano', 'paese': 'Italia'},
            {'codice_iata': 'LIN', 'nome': 'Linate', 'città': 'Milano', 'paese': 'Italia'},
            {'codice_iata': 'NAP', 'nome': 'Capodichino', 'città': 'Napoli', 'paese': 'Italia'},
            {'codice_iata': 'VCE', 'nome': 'Marco Polo', 'città': 'Venezia', 'paese': 'Italia'},
            {'codice_iata': 'CDG', 'nome': 'Charles de Gaulle', 'città': 'Parigi', 'paese': 'Francia'},
            {'codice_iata': 'LHR', 'nome': 'Heathrow', 'città': 'Londra', 'paese': 'Regno Unito'},
            {'codice_iata': 'FRA', 'nome': 'Frankfurt', 'città': 'Francoforte', 'paese': 'Germania'},
        ]
        
        print("📊 Ajout des aéroports...")
        for aeroporto_data in aeroporti:
            aeroporto = Aeroporto(**aeroporto_data)
            db.session.add(aeroporto)
        db.session.commit()
        print(f"✅ {len(aeroporti)} aéroports ajoutés")
        
        # Ajouter des utilisateurs de test
        utenti = [
            {
                'email': 'admin@test.com',
                'password': 'admin123',
                'nome': 'Admin',
                'cognome': 'Test',
                'is_airline': False
            },
            {
                'email': 'airline@test.com',
                'password': 'airline123',
                'nome': 'Compagnia',
                'cognome': 'Test',
                'is_airline': True
            }
        ]
        
        print("👥 Ajout des utilisateurs...")
        for utente_data in utenti:
            utente = Utente(
                email=utente_data['email'],
                nome=utente_data['nome'],
                cognome=utente_data['cognome'],
                is_airline=utente_data['is_airline']
            )
            utente.set_password(utente_data['password'])
            db.session.add(utente)
        db.session.commit()
        print(f"✅ {len(utenti)} utilisateurs ajoutés")
        
        # Ajouter une compagnie aérienne
        print("✈️ Ajout de la compagnie aérienne...")
        utente_airline = Utente.query.filter_by(email='airline@test.com').first()
        compagnia = CompagniaAerea(
            utente_id=utente_airline.id,
            nome_compagnia='Test Airlines',
            codice_iata='TA',
            sede_legale='Milano, Italia'
        )
        db.session.add(compagnia)
        db.session.commit()
        print("✅ Compagnie aérienne ajoutée")
        
        # Ajouter des vols de test
        print("🛫 Ajout des vols...")
        aeroporti_db = Aeroporto.query.all()
        compagnia_db = CompagniaAerea.query.first()
        
        for i in range(5):
            partenza = random.choice(aeroporti_db)
            arrivo = random.choice([a for a in aeroporti_db if a.id != partenza.id])
            
            data_partenza = datetime.now() + timedelta(days=random.randint(1, 30))
            data_arrivo = data_partenza + timedelta(hours=random.randint(1, 6))
            
            volo = Volo(
                numero_volo=f'TA{100 + i}',
                compagnia_id=compagnia_db.id,
                aeroporto_partenza_id=partenza.id,
                aeroporto_arrivo_id=arrivo.id,
                data_partenza=data_partenza,
                data_arrivo=data_arrivo,
                posti_economy=random.randint(50, 200),
                posti_business=random.randint(10, 50),
                posti_first=random.randint(5, 20),
                prezzo_economy=random.uniform(50, 300),
                prezzo_business=random.uniform(200, 800),
                prezzo_first=random.uniform(500, 1500)
            )
            db.session.add(volo)
        
        db.session.commit()
        print("✅ 5 vols ajoutés")
        
        print("\n🎉 Base de données PostgreSQL initialisée avec succès!")
        print(f"📊 Aéroports: {len(aeroporti)}")
        print(f"👥 Utilisateurs: {len(utenti)}")
        print(f"✈️ Vols: 5")
        print("\n🔑 Comptes de test:")
        print("   - Admin: admin@test.com / admin123")
        print("   - Compagnie: airline@test.com / airline123")

if __name__ == '__main__':
    init_postgres_database()

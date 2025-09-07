from app import create_app, db
from app.models import Aeroporto

def populate_airports():
    app = create_app()
    with app.app_context():
        # Lista degli aeroporti principali
        airports = [
            # Italia
            {'codice_iata': 'FCO', 'nome': 'Leonardo da Vinci', 'città': 'Roma', 'paese': 'Italia'},
            {'codice_iata': 'MXP', 'nome': 'Malpensa', 'città': 'Milano', 'paese': 'Italia'}, # Secondo aeroporto italiano per traffico passeggeri, voli internazionali
            {'codice_iata': 'LIN', 'nome': 'Linate', 'città': 'Milano', 'paese': 'Italia'}, # Principalmente voli domestici e brevi tratte europee
            {'codice_iata': 'BGY', 'nome': 'Orio al Serio', 'città': 'Bergamo', 'paese': 'Italia'}, # Aeroporto in crescita, molte compagnie low-cost
            {'codice_iata': 'NAP', 'nome': 'Capodichino', 'città': 'Napoli', 'paese': 'Italia'}, # Serve la Campania, collegamenti internazionali
            {'codice_iata': 'BLQ', 'nome': 'Guglielmo Marconi', 'città': 'Bologna', 'paese': 'Italia'}, # Importante per il centro Italia
            {'codice_iata': 'VCE', 'nome': 'Marco Polo', 'città': 'Venezia', 'paese': 'Italia'}, # Aeroporto importante per turismo e collegamenti con Europa Est e Medio Oriente
            {'codice_iata': 'FLR', 'nome': 'Peretola', 'città': 'Firenze', 'paese': 'Italia'}, # Serve la Toscana
            {'codice_iata': 'PSA', 'nome': 'Galileo Galilei', 'città': 'Pisa', 'paese': 'Italia'}, # Serve la Toscana
            {'codice_iata': 'BRI', 'nome': 'Karol Wojtyla', 'città': 'Bari', 'paese': 'Italia'}, # Serve la Puglia
            {'codice_iata': 'CTA', 'nome': 'Fontanarossa', 'città': 'Catania', 'paese': 'Italia'}, # Serve la Sicilia orientale
            {'codice_iata': 'TRN', 'nome': 'Caselle', 'città': 'Torino', 'paese': 'Italia'}, # Serve il Piemonte
            {'codice_iata': 'GOA', 'nome': 'Cristoforo Colombo', 'città': 'Genova', 'paese': 'Italia'},
            {'codice_iata': 'PMO', 'nome': 'Falcone e Borsellino', 'città': 'Palermo', 'paese': 'Italia'}, # Serve la Sicilia occidentale
            {'codice_iata': 'OLB', 'nome': 'Costa Smeralda', 'città': 'Olbia', 'paese': 'Italia'},
            {'codice_iata': 'AHO', 'nome': 'Fertilia', 'città': 'Alghero', 'paese': 'Italia'},
            {'codice_iata': 'VRN', 'nome': 'Valerio Catullo', 'città': 'Verona', 'paese': 'Italia'},
            {'codice_iata': 'TSF', 'nome': 'Antonio Canova', 'città': 'Treviso', 'paese': 'Italia'},
            {'codice_iata': 'TRS', 'nome': 'Ronchi dei Legionari', 'città': 'Trieste', 'paese': 'Italia'},
            {'codice_iata': 'AOI', 'nome': 'Raffaello Sanzio', 'città': 'Ancona', 'paese': 'Italia'},
            {'codice_iata': 'PSR', 'nome': 'Abruzzo', 'città': 'Pescara', 'paese': 'Italia'},
            {'codice_iata': 'SUF', 'nome': 'Lamezia Terme', 'città': 'Lamezia Terme', 'paese': 'Italia'},
            {'codice_iata': 'REG', 'nome': 'Tito Minniti', 'città': 'Reggio Calabria', 'paese': 'Italia'},
            {'codice_iata': 'CAG', 'nome': 'Elmas', 'città': 'Cagliari', 'paese': 'Italia'},
            {'codice_iata': 'PEG', 'nome': "San Francesco d'Assisi", 'città': 'Perugia', 'paese': 'Italia'},
            {'codice_iata': 'BDS', 'nome': 'Papola Casale', 'città': 'Brindisi', 'paese': 'Italia'},
            
            # Europa
            {'codice_iata': 'CDG', 'nome': 'Charles de Gaulle', 'città': 'Parigi', 'paese': 'Francia'},
            {'codice_iata': 'ORY', 'nome': 'Orly', 'città': 'Parigi', 'paese': 'Francia'},
            {'codice_iata': 'LHR', 'nome': 'Heathrow', 'città': 'Londra', 'paese': 'Regno Unito'},
            {'codice_iata': 'LGW', 'nome': 'Gatwick', 'città': 'Londra', 'paese': 'Regno Unito'},
            {'codice_iata': 'FRA', 'nome': 'Frankfurt', 'città': 'Francoforte', 'paese': 'Germania'},
            {'codice_iata': 'MUC', 'nome': 'Franz Josef Strauss', 'città': 'Monaco', 'paese': 'Germania'},
            {'codice_iata': 'AMS', 'nome': 'Schiphol', 'città': 'Amsterdam', 'paese': 'Paesi Bassi'},
            {'codice_iata': 'MAD', 'nome': 'Barajas', 'città': 'Madrid', 'paese': 'Spagna'},
            {'codice_iata': 'BCN', 'nome': 'El Prat', 'città': 'Barcellona', 'paese': 'Spagna'},
            {'codice_iata': 'ZRH', 'nome': 'Zurigo', 'città': 'Zurigo', 'paese': 'Svizzera'},
            {'codice_iata': 'VIE', 'nome': 'Schwechat', 'città': 'Vienna', 'paese': 'Austria'},
            {'codice_iata': 'BRU', 'nome': 'Zaventem', 'città': 'Bruxelles', 'paese': 'Belgio'},
            {'codice_iata': 'CPH', 'nome': 'Kastrup', 'città': 'Copenaghen', 'paese': 'Danimarca'},
            {'codice_iata': 'HEL', 'nome': 'Vantaa', 'città': 'Helsinki', 'paese': 'Finlandia'},
            {'codice_iata': 'OSL', 'nome': 'Gardermoen', 'città': 'Oslo', 'paese': 'Norvegia'},
            {'codice_iata': 'ARN', 'nome': 'Arlanda', 'città': 'Stoccolma', 'paese': 'Svezia'},
            {'codice_iata': 'IST', 'nome': 'Istanbul', 'città': 'Istanbul', 'paese': 'Turchia'},
            {'codice_iata': 'ATH', 'nome': 'Eleftherios Venizelos', 'città': 'Atene', 'paese': 'Grecia'},
            {'codice_iata': 'LIS', 'nome': 'Portela', 'città': 'Lisbona', 'paese': 'Portogallo'},
            {'codice_iata': 'DUB', 'nome': 'Dublin', 'città': 'Dublino', 'paese': 'Irlanda'},
            
            # Africa
            {'codice_iata': 'CAI', 'nome': 'International', 'città': 'Il Cairo', 'paese': 'Egitto'},
            {'codice_iata': 'CMN', 'nome': 'Mohammed V', 'città': 'Casablanca', 'paese': 'Marocco'},
            {'codice_iata': 'TUN', 'nome': 'Carthage', 'città': 'Tunisi', 'paese': 'Tunisia'},
            {'codice_iata': 'JNB', 'nome': 'O.R. Tambo', 'città': 'Johannesburg', 'paese': 'Sudafrica'},
            {'codice_iata': 'CPT', 'nome': 'Cape Town', 'città': 'Città del Capo', 'paese': 'Sudafrica'},
            {'codice_iata': 'NBO', 'nome': 'Jomo Kenyatta', 'città': 'Nairobi', 'paese': 'Kenya'},
            {'codice_iata': 'ADD', 'nome': 'Bole', 'città': 'Addis Abeba', 'paese': 'Etiopia'},
            {'codice_iata': 'LOS', 'nome': 'Murtala Muhammed', 'città': 'Lagos', 'paese': 'Nigeria'},
            {'codice_iata': 'DSS', 'nome': 'Blaise Diagne', 'città': 'Dakar', 'paese': 'Senegal'},
            {'codice_iata': 'RBA', 'nome': 'Sale', 'città': 'Rabat', 'paese': 'Marocco'},
            {'codice_iata': 'TNG', 'nome': 'Ibn Battouta', 'città': 'Tangeri', 'paese': 'Marocco'},
            {'codice_iata': 'LAD', 'nome': 'Quatro de Fevereiro', 'città': 'Luanda', 'paese': 'Angola'},
            {'codice_iata': 'LUN', 'nome': 'Kenneth Kaunda', 'città': 'Lusaka', 'paese': 'Zambia'},
            {'codice_iata': 'HRE', 'nome': 'Robert Gabriel Mugabe', 'città': 'Harare', 'paese': 'Zimbabwe'},
            
            # Altri continenti (mantenuti per completezza)
            {'codice_iata': 'JFK', 'nome': 'John F. Kennedy', 'città': 'New York', 'paese': 'Stati Uniti'},
            {'codice_iata': 'LAX', 'nome': 'Los Angeles International', 'città': 'Los Angeles', 'paese': 'Stati Uniti'},
            {'codice_iata': 'DXB', 'nome': 'Dubai International', 'città': 'Dubai', 'paese': 'Emirati Arabi Uniti'},
            {'codice_iata': 'HKG', 'nome': 'Hong Kong International', 'città': 'Hong Kong', 'paese': 'Cina'},
            {'codice_iata': 'SIN', 'nome': 'Changi', 'città': 'Singapore', 'paese': 'Singapore'},
            {'codice_iata': 'NRT', 'nome': 'Narita', 'città': 'Tokyo', 'paese': 'Giappone'},
            {'codice_iata': 'SYD', 'nome': 'Kingsford Smith', 'città': 'Sydney', 'paese': 'Australia'},
            {'codice_iata': 'DOH', 'nome': 'Hamad International', 'città': 'Doha', 'paese': 'Qatar'}
        ]

        try:
            # Rimuovi tutti gli aeroporti esistenti
            Aeroporto.query.delete()
            db.session.commit()
            
            # Inserisci i nuovi aeroporti
            for airport in airports:
                aeroporto = Aeroporto(**airport)
                db.session.add(aeroporto)
            
            db.session.commit()
            print(f"Aeroporti inseriti con successo! Totale: {len(airports)} aeroporti")
            
        except Exception as e:
            db.session.rollback()
            print(f"Errore durante l'inserimento degli aeroporti: {e}")

if __name__ == '__main__':
    populate_airports() 
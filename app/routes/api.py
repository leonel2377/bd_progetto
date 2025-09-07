from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime, timedelta
from .. import db
from ..models import Utente, Volo, CompagniaAerea, Aeroporto, Prenotazione, Biglietto
from ..queries import (
    cerca_voli_diretti,
    cerca_voli_scalo,
    statistiche_compagnia,
    prenotazioni_utente,
    verifica_disponibilità_posti
)

api = Blueprint('api', __name__, url_prefix='/api/v1')

# Schemi di validazione
class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    nome = fields.Str(required=True)
    cognome = fields.Str(required=True)
    is_airline = fields.Bool(required=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class FlightSearchSchema(Schema):
    aeroporto_partenza = fields.Str(required=True, validate=validate.Length(equal=3))
    aeroporto_arrivo = fields.Str(required=True, validate=validate.Length(equal=3))
    data = fields.Date(required=True)
    passeggeri = fields.Int(required=True, validate=validate.Range(min=1, max=9))
    classe = fields.Str(validate=validate.OneOf(['economy', 'business', 'first']))
    ordina_per = fields.Str(validate=validate.OneOf(['prezzo', 'tempo']))

class BookingSchema(Schema):
    volo_id = fields.Int(required=True)
    classe = fields.Str(required=True, validate=validate.OneOf(['economy', 'business', 'first']))
    passeggeri = fields.Int(required=True, validate=validate.Range(min=1, max=9))
    bagaglio_extra = fields.Bool()
    servizi_extra = fields.Str()

# Inizializzazione degli schemi
user_schema = UserSchema()
login_schema = LoginSchema()
flight_search_schema = FlightSearchSchema()
booking_schema = BookingSchema()

# Gestione errori
@api.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({'error': error.messages}), 400

@api.errorhandler(Exception)
def handle_error(error):
    return jsonify({'error': str(error)}), 500

# Autenticazione
@api.route('/auth/register', methods=['POST'])
def register():
    try:
        data = user_schema.load(request.json)
        
        if Utente.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email già registrata'}), 400
            
        user = Utente(
            email=data['email'],
            nome=data['nome'],
            cognome=data['cognome'],
            is_airline=data['is_airline']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'message': 'Registrazione completata',
            'access_token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api.route('/auth/login', methods=['POST'])
def login():
    try:
        data = login_schema.load(request.json)
        user = Utente.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nome': user.nome,
                    'cognome': user.cognome,
                    'is_airline': user.is_airline
                }
            })
            
        return jsonify({'error': 'Credenziali non valide'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Ricerca voli
@api.route('/flights/search', methods=['POST'])
@jwt_required()
def search_flights():
    try:
        data = flight_search_schema.load(request.json)
        
        # Convertir la chaîne de date en objet datetime
        if isinstance(data['data'], str):
            data['data'] = datetime.strptime(data['data'], '%Y-%m-%d')
        elif hasattr(data['data'], 'date'):
            # Si c'est un objet date, le convertir en datetime
            data['data'] = datetime.combine(data['data'], datetime.min.time())
        
        # Cerca voli diretti
        voli_diretti = cerca_voli_diretti(
            data['aeroporto_partenza'],
            data['aeroporto_arrivo'],
            data['data'],
            data.get('passeggeri', 1),
            data.get('classe', 'economy'),
            data.get('ordina_per', 'prezzo')
        )
        
        # Cerca voli con scalo
        voli_scalo = cerca_voli_scalo(
            data['aeroporto_partenza'],
            data['aeroporto_arrivo'],
            data['data']
        )
        
        return jsonify({
            'voli_diretti': [
                {
                    'id': v.id,
                    'numero_volo': v.numero_volo,
                    'compagnia': v.nome_compagnia,
                    'partenza': v.città_partenza,
                    'arrivo': v.città_arrivo,
                    'data_partenza': v.data_partenza.isoformat(),
                    'data_arrivo': v.data_arrivo.isoformat(),
                    'posti_disponibili': v.posti_disponibili,
                    'prezzo': float(v.prezzo)
                } for v in voli_diretti
            ],
            'voli_scalo': [
                {
                    'volo1': {
                        'id': v.volo1_id,
                        'numero': v.volo1_numero,
                        'compagnia': v.compagnia1,
                        'partenza': v.città_partenza,
                        'arrivo': v.città_scalo,
                        'data_partenza': v.data_partenza.isoformat(),
                        'data_arrivo': v.scalo_arrivo.isoformat()
                    },
                    'volo2': {
                        'id': v.volo2_id,
                        'numero': v.volo2_numero,
                        'compagnia': v.compagnia2,
                        'partenza': v.città_scalo,
                        'arrivo': v.città_arrivo,
                        'data_partenza': v.scalo_partenza.isoformat(),
                        'data_arrivo': v.data_arrivo.isoformat()
                    },
                    'prezzi': {
                        'economy': float(v.prezzo_totale_economy),
                        'business': float(v.prezzo_totale_business),
                        'first': float(v.prezzo_totale_first)
                    }
                } for v in voli_scalo
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Prenotazioni
@api.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    try:
        data = booking_schema.load(request.json)
        user_id = int(get_jwt_identity())
        
        # Verifica disponibilità
        disponibilità = verifica_disponibilità_posti(data['volo_id'])
        posti_disponibili = getattr(disponibilità, f'posti_{data["classe"]}_disponibili')
        
        if posti_disponibili < data['passeggeri']:
            return jsonify({'error': 'Posti non disponibili'}), 400
            
        # Crea prenotazione
        with db.session.begin():
            prenotazione = Prenotazione(
                user_id=user_id,
                stato='confermata',
                prezzo_totale=0
            )
            db.session.add(prenotazione)
            db.session.flush()
            
            # Crea biglietti
            volo = Volo.query.get_or_404(data['volo_id'])
            prezzo_base = getattr(volo, f'prezzo_{data["classe"]}')
            prezzo_totale = 0
            
            for i in range(data['passeggeri']):
                biglietto = Biglietto(
                    booking_id=prenotazione.id,
                    flight_id=data['volo_id'],
                    classe=data['classe'],
                    numero_posto=f"{data['classe'][0].upper()}{i+1}",
                    prezzo=prezzo_base,
                    bagaglio_extra=data.get('bagaglio_extra', False),
                    servizi_extra=data.get('servizi_extra', '')
                )
                db.session.add(biglietto)
                prezzo_totale += prezzo_base
                
            prenotazione.prezzo_totale = prezzo_totale
            
        return jsonify({
            'message': 'Prenotazione creata con successo',
            'prenotazione_id': prenotazione.id,
            'prezzo_totale': prezzo_totale
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api.route('/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    try:
        user_id = int(get_jwt_identity())
        prenotazioni = prenotazioni_utente(user_id)
        
        return jsonify({
            'prenotazioni': [
                {
                    'id': p.prenotazione_id,
                    'data': p.data_prenotazione.isoformat(),
                    'stato': p.stato,
                    'prezzo_totale': float(p.prezzo_totale),
                    'biglietti': p.dettagli_biglietti
                } for p in prenotazioni
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Statistiche
@api.route('/airlines/<int:airline_id>/statistics', methods=['GET'])
@jwt_required()
def get_airline_statistics(airline_id):
    try:
        user_id = int(get_jwt_identity())
        user = Utente.query.get_or_404(user_id)
        
        if not user.is_airline or user.airline.id != airline_id:
            return jsonify({'error': 'Non autorizzato'}), 403
            
        data_inizio = request.args.get('data_inizio', 
            datetime.now().replace(day=1).strftime('%Y-%m-%d'))
        data_fine = request.args.get('data_fine',
            datetime.now().strftime('%Y-%m-%d'))
            
        statistiche = statistiche_compagnia(
            airline_id,
            datetime.strptime(data_inizio, '%Y-%m-%d'),
            datetime.strptime(data_fine, '%Y-%m-%d')
        )
        
        if not statistiche:
            return jsonify({'error': 'Nessuna statistica disponibile'}), 404
            
        return jsonify({
            'compagnia': statistiche.nome_compagnia,
            'periodo': {
                'inizio': data_inizio,
                'fine': data_fine
            },
            'statistiche': {
                'numero_voli': statistiche.numero_voli,
                'numero_passeggeri': statistiche.numero_passeggeri,
                'guadagno_totale': float(statistiche.guadagno_totale or 0),
                'prezzo_medio': float(statistiche.prezzo_medio or 0),
                'distribuzione_classi': {
                    'economy': statistiche.passeggeri_economy,
                    'business': statistiche.passeggeri_business,
                    'first': statistiche.passeggeri_first
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400 
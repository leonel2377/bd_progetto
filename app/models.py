from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class Utente(db.Model, UserMixin):
    __tablename__ = 'utente'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    is_airline = db.Column(db.Boolean, default=False)
    data_registrazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    compagnia = db.relationship('CompagniaAerea', back_populates='utente', uselist=False)
    prenotazioni = db.relationship('Prenotazione', back_populates='utente', cascade='all, delete-orphan')
    biglietti = db.relationship('Biglietto', back_populates='passeggero', foreign_keys='Biglietto.passeggero_id')
    
    @property
    def is_passenger(self):
        return not self.is_airline
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<Utente {self.email}>'

class CompagniaAerea(db.Model):
    __tablename__ = 'compagnia_aerea'
    
    id = db.Column(db.Integer, primary_key=True)
    utente_id = db.Column(db.Integer, db.ForeignKey('utente.id'), unique=True, nullable=False)
    nome_compagnia = db.Column(db.String(100), nullable=False)
    codice_iata = db.Column(db.String(2), unique=True, nullable=True)
    sede_legale = db.Column(db.String(200), nullable=True)
    
    # Relazioni
    utente = db.relationship('Utente', back_populates='compagnia')
    voli = db.relationship('Volo', back_populates='compagnia', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CompagniaAerea {self.nome_compagnia}>'

class Aeroporto(db.Model):
    __tablename__ = 'aeroporto'
    
    id = db.Column(db.Integer, primary_key=True)
    codice_iata = db.Column(db.String(3), nullable=False, unique=True)
    nome = db.Column(db.String(100), nullable=False)
    città = db.Column(db.String(100), nullable=False)
    paese = db.Column(db.String(100), nullable=False)
    
    # Relazioni
    voli_partenza = db.relationship('Volo', foreign_keys='Volo.aeroporto_partenza_id', back_populates='aeroporto_partenza')
    voli_arrivo = db.relationship('Volo', foreign_keys='Volo.aeroporto_arrivo_id', back_populates='aeroporto_arrivo')
    
    def __repr__(self):
        return f'<Aeroporto {self.codice_iata}>'

class Volo(db.Model):
    __tablename__ = 'volo'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_volo = db.Column(db.String(10), nullable=False)
    compagnia_id = db.Column(db.Integer, db.ForeignKey('compagnia_aerea.id'), nullable=False)
    aeroporto_partenza_id = db.Column(db.Integer, db.ForeignKey('aeroporto.id'), nullable=False)
    aeroporto_arrivo_id = db.Column(db.Integer, db.ForeignKey('aeroporto.id'), nullable=False)
    data_partenza = db.Column(db.DateTime, nullable=False)
    data_arrivo = db.Column(db.DateTime, nullable=False)
    posti_economy = db.Column(db.Integer, nullable=False, default=0)
    posti_business = db.Column(db.Integer, nullable=False, default=0)
    posti_first = db.Column(db.Integer, nullable=False, default=0)
    posti_totali = db.Column(db.Integer, nullable=False)
    prezzo_economy = db.Column(db.Float, nullable=False)
    prezzo_business = db.Column(db.Float, nullable=False)
    prezzo_first = db.Column(db.Float, nullable=False)
    
    # Relazioni
    compagnia = db.relationship('CompagniaAerea', back_populates='voli')
    aeroporto_partenza = db.relationship('Aeroporto', foreign_keys=[aeroporto_partenza_id], back_populates='voli_partenza')
    aeroporto_arrivo = db.relationship('Aeroporto', foreign_keys=[aeroporto_arrivo_id], back_populates='voli_arrivo')
    biglietti = db.relationship('Biglietto', back_populates='volo', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Volo, self).__init__(**kwargs)
        # Il calcolo dei posti totali è ora gestito dal trigger
    
    def __repr__(self):
        return f'<Volo {self.numero_volo}>'
    
    # La validazione delle date è ora gestita dal trigger
    # La gestione dei posti disponibili è ora gestita dal trigger

class Prenotazione(db.Model):
    __tablename__ = 'prenotazione'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utente.id'), nullable=False)
    data_prenotazione = db.Column(db.DateTime, default=datetime.utcnow)
    stato = db.Column(db.String(20), default='confermata')
    prezzo_totale = db.Column(db.Float, nullable=False)
    
    # Relazioni
    utente = db.relationship('Utente', back_populates='prenotazioni')
    biglietti = db.relationship('Biglietto', back_populates='prenotazione', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Prenotazione {self.id} - Utente {self.user_id}>'

class Biglietto(db.Model):
    __tablename__ = 'biglietto'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('prenotazione.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('volo.id'), nullable=False)
    passeggero_id = db.Column(db.Integer, db.ForeignKey('utente.id'), nullable=False)
    classe = db.Column(db.String(20), nullable=False)
    numero_posto = db.Column(db.String(10))
    prezzo = db.Column(db.Float, nullable=False)
    bagaglio_extra = db.Column(db.Boolean, default=False)
    servizi_extra = db.Column(db.String(200))
    
    # Relazioni
    prenotazione = db.relationship('Prenotazione', back_populates='biglietti')
    volo = db.relationship('Volo', back_populates='biglietti')
    passeggero = db.relationship('Utente', back_populates='biglietti')
    
    def __repr__(self):
        return f'<Biglietto {self.id} - Volo {self.flight_id}>'

@login_manager.user_loader
def load_user(user_id):
    return Utente.query.get(int(user_id)) 
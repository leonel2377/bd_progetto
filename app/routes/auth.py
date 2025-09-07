from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from .. import db
from ..models import Utente, CompagniaAerea
import random
import string

auth = Blueprint('auth', __name__)

def generate_temp_iata():
    """Genera un codice IATA temporaneo univoco"""
    while True:
        # Genera un codice IATA casuale di 2 lettere
        temp_iata = ''.join(random.choices(string.ascii_uppercase, k=2))
        # Verifica se esiste già
        if not CompagniaAerea.query.filter_by(codice_iata=temp_iata).first():
            return temp_iata

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Gestisce il login degli utenti"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = request.form.get('remember', False)
            
            # Validazione input
            if not email or not password:
                flash('Inserisci email e password', 'error')
                return render_template('auth/login.html')
            
            # Cerca l'utente nel database
            user = Utente.query.filter_by(email=email).first()
            
            # Verifica credenziali
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash('Login effettuato con successo!', 'success')
                
                # Redirect in base al tipo di utente
                if user.is_airline and user.compagnia:
                    return redirect(url_for('main.visualizza_statistiche', 
                                          compagnia_id=user.compagnia.id))
                return redirect(url_for('main.index'))
            else:
                flash('Email o password non validi', 'error')
                
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Errore durante il login', 'error')
            
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Gestisce la registrazione di nuovi utenti"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            nome = request.form.get('nome')
            cognome = request.form.get('cognome')
            tipo_utente = request.form.get('tipo_utente')
            nome_compagnia = request.form.get('nome_compagnia')

            # Validazione base per tutti gli utenti
            if not all([email, password, confirm_password, nome, cognome, tipo_utente]):
                flash('I campi Nome, Cognome, Email, Password e Tipo Utente sono obbligatori', 'error')
                return render_template('auth/register.html')

            # Validazione password
            if password != confirm_password:
                flash('Le password non coincidono', 'error')
                return render_template('auth/register.html')

            # Validazione specifica per compagnie aeree
            if tipo_utente == 'compagnia':
                if not nome_compagnia:
                    flash('Il nome della compagnia è obbligatorio per le compagnie aeree', 'error')
                    return render_template('auth/register.html')

            # Verifica se l'email esiste già
            if Utente.query.filter_by(email=email).first():
                flash('Email già registrata', 'error')
                return render_template('auth/register.html')

            try:
                # Creazione nuovo utente
                nuovo_utente = Utente(
                    email=email,
                    nome=nome,
                    cognome=cognome,
                    is_airline=(tipo_utente == 'compagnia')
                )
                nuovo_utente.set_password(password)
                db.session.add(nuovo_utente)
                db.session.flush()  # Per ottenere l'ID dell'utente

                # Se è una compagnia aerea, crea il record nella tabella compagnia_aerea
                if tipo_utente == 'compagnia':
                    # Genera un codice IATA temporaneo
                    temp_iata = generate_temp_iata()
                    nuova_compagnia = CompagniaAerea(
                        utente_id=nuovo_utente.id,
                        nome_compagnia=nome_compagnia,
                        codice_iata=temp_iata,  # Usa il codice IATA temporaneo
                        sede_legale='Da definire'  # Valore di default per la sede legale
                    )
                    db.session.add(nuova_compagnia)

                db.session.commit()
                flash('Registrazione completata con successo!', 'success')
                return redirect(url_for('auth.login'))

            except Exception as e:
                db.session.rollback()
                flash(f'Errore durante la registrazione: {str(e)}', 'error')
                return render_template('auth/register.html')

        except Exception as e:
            flash(f'Errore durante la registrazione: {str(e)}', 'error')
            return render_template('auth/register.html')

    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    """Gestisce il logout degli utenti"""
    logout_user()
    flash('Logout effettuato con successo', 'success')
    return redirect(url_for('main.index'))

@auth.route('/profilo', methods=['GET', 'POST'])
@login_required
def profilo():
    """Gestisce la visualizzazione e modifica del profilo utente"""
    if request.method == 'POST':
        try:
            # Recupera i dati dal form
            nome = request.form.get('nome')
            cognome = request.form.get('cognome')
            email = request.form.get('email')
            password_attuale = request.form.get('password_attuale')
            nuova_password = request.form.get('nuova_password')
            conferma_password = request.form.get('conferma_password')
            
            # Validazione input
            if not all([nome, cognome, email]):
                flash('Nome, cognome ed email sono obbligatori', 'error')
                return render_template('auth/profilo.html')
            
            # Verifica se l'email è già in uso da un altro utente
            if email != current_user.email:
                if Utente.query.filter(Utente.email == email, 
                                     Utente.id != current_user.id).first():
                    flash('Email già in uso', 'error')
                    return render_template('auth/profilo.html')
            
            # Aggiorna i dati base
            current_user.nome = nome
            current_user.cognome = cognome
            current_user.email = email
            
            # Se richiesta modifica password
            if password_attuale and nuova_password:
                if not current_user.check_password(password_attuale):
                    flash('Password attuale non valida', 'error')
                    return render_template('auth/profilo.html')
                    
                if nuova_password != conferma_password:
                    flash('Le nuove password non coincidono', 'error')
                    return render_template('auth/profilo.html')
                    
                current_user.set_password(nuova_password)
            
            # Se è una compagnia aerea, aggiorna anche i dati della compagnia
            if current_user.is_airline:
                nome_compagnia = request.form.get('nome_compagnia')
                if nome_compagnia:
                    current_user.airline.nome_compagnia = nome_compagnia
            
            db.session.commit()
            flash('Profilo aggiornato con successo', 'success')
            return redirect(url_for('auth.profilo'))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Errore durante l\'aggiornamento del profilo', 'error')
            
    return render_template('auth/profilo.html') 
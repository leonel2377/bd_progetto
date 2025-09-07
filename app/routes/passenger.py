from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Volo, Prenotazione, Biglietto, Aeroporto
from app import db
from datetime import datetime
from sqlalchemy import and_, or_

passenger = Blueprint('passenger', __name__, url_prefix='/passenger')

@passenger.route('/prenotazioni')
@login_required
def prenotazioni():
    if not (hasattr(current_user, 'is_airline') and not current_user.is_airline):
        flash('Accesso non autorizzato', 'error')
        return redirect(url_for('main.index'))
    
    prenotazioni = Prenotazione.query.filter_by(user_id=current_user.id).all()
    return render_template('passenger/prenotazioni.html', prenotazioni=prenotazioni)

@passenger.route('/prenota/<int:flight_id>', methods=['GET', 'POST'])
@login_required
def prenota_volo(flight_id):
    if not (hasattr(current_user, 'is_airline') and not current_user.is_airline):
        flash('Accesso non autorizzato', 'error')
        return redirect(url_for('main.index'))
    
    volo = Volo.query.get_or_404(flight_id)
    
    if request.method == 'POST':
        try:
            # Crea la prenotazione
            prenotazione = Prenotazione(
                user_id=current_user.id,
                prezzo_totale=0  # Verrà aggiornato dopo
            )
            db.session.add(prenotazione)
            db.session.flush()  # Per ottenere l'ID della prenotazione
            
            # Crea il biglietto
            classe = request.form.get('classe')
            prezzo = getattr(volo, f'prezzo_{classe}')
            
            biglietto = Biglietto(
                booking_id=prenotazione.id,
                flight_id=volo.id,
                classe=classe,
                numero_posto=request.form.get('numero_posto'),
                prezzo=prezzo,
                bagaglio_extra=request.form.get('bagaglio_extra') == 'on',
                servizi_extra=request.form.get('servizi_extra')
            )
            
            # Aggiorna il prezzo totale
            prenotazione.prezzo_totale = prezzo
            if biglietto.bagaglio_extra:
                prenotazione.prezzo_totale += 30  # Costo bagaglio extra
            
            # Aggiorna i posti disponibili
            setattr(volo, f'posti_{classe}', getattr(volo, f'posti_{classe}') - 1)
            
            db.session.add(biglietto)
            db.session.commit()
            
            flash('Prenotazione effettuata con successo!', 'success')
            return redirect(url_for('passenger.prenotazioni'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la prenotazione: {str(e)}', 'error')
    
    return render_template('passenger/prenota_volo.html', volo=volo)

@passenger.route('/api/posti_disponibili/<int:flight_id>')
@login_required
def posti_disponibili(flight_id):
    volo = Volo.query.get_or_404(flight_id)
    classe = request.args.get('classe', 'economy')
    
    posti_disponibili = getattr(volo, f'posti_{classe}')
    posti_occupati = Biglietto.query.filter_by(
        flight_id=flight_id,
        classe=classe
    ).count()
    
    return jsonify({
        'totali': posti_disponibili,
        'occupati': posti_occupati,
        'disponibili': posti_disponibili - posti_occupati
    })

@passenger.route('/cancella_prenotazione/<int:booking_id>', methods=['POST'])
@login_required
def cancella_prenotazione(booking_id):
    if not (hasattr(current_user, 'is_airline') and not current_user.is_airline):
        flash('Accesso non autorizzato', 'error')
        return redirect(url_for('main.index'))
    
    prenotazione = Prenotazione.query.get_or_404(booking_id)
    if prenotazione.user_id != current_user.id:
        flash('Accesso non autorizzato', 'error')
        return redirect(url_for('passenger.prenotazioni'))
    
    try:
        # Ripristina i posti disponibili
        for biglietto in prenotazione.biglietti:
            volo = biglietto.volo
            setattr(volo, f'posti_{biglietto.classe}',
                   getattr(volo, f'posti_{biglietto.classe}') + 1)
        
        # Cancella la prenotazione (cascade cancellerà i biglietti)
        db.session.delete(prenotazione)
        db.session.commit()
        flash('Prenotazione cancellata con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante la cancellazione: {str(e)}', 'error')
    
    return redirect(url_for('passenger.prenotazioni')) 
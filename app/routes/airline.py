from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Volo, Aeroporto, CompagniaAerea, Biglietto
from app import db
from datetime import datetime
from sqlalchemy import func

airline = Blueprint('airline', __name__, url_prefix='/airline')

@airline.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_airline:
        flash('Accesso non autorizzato', 'error')
        return redirect(url_for('main.index'))
    
    # Recupera i voli della compagnia
    voli = Volo.query.filter_by(compagnia_id=current_user.compagnia.id).all()
    
    # Calcola statistiche
    totale_passeggeri = Biglietto.query.join(Volo).filter(
        Volo.compagnia_id == current_user.compagnia.id
    ).count()
    
    guadagno_totale = db.session.query(func.sum(Biglietto.prezzo)).join(Volo).filter(
        Volo.compagnia_id == current_user.compagnia.id
    ).scalar() or 0
    
    return render_template('airline/dashboard.html',
                         voli=voli,
                         totale_passeggeri=totale_passeggeri,
                         guadagno_totale=guadagno_totale)

@airline.route('/nuovo_volo', methods=['GET', 'POST'])
@login_required
def nuovo_volo():
    if not current_user.is_airline:
        flash('Accesso non autorizzato.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Recupera i dati dal form
            numero_volo = request.form.get('numero_volo')
            aeroporto_partenza_id = request.form.get('aeroporto_partenza_id')
            aeroporto_arrivo_id = request.form.get('aeroporto_arrivo_id')
            data_partenza = datetime.strptime(request.form.get('data_partenza'), '%Y-%m-%dT%H:%M')
            data_arrivo = datetime.strptime(request.form.get('data_arrivo'), '%Y-%m-%dT%H:%M')
            
            # Recupera i posti disponibili per ogni classe
            posti_economy = int(request.form.get('posti_economy', 0) or 0)
            posti_business = int(request.form.get('posti_business', 0) or 0)
            posti_first = int(request.form.get('posti_first', 0) or 0)
            
            # Calcola il totale dei posti
            posti_totali = posti_economy + posti_business + posti_first
            
            # Recupera i prezzi per ogni classe
            prezzo_economy = float(request.form.get('prezzo_economy', 0) or 0)
            prezzo_business = float(request.form.get('prezzo_business', 0) or 0)
            prezzo_first = float(request.form.get('prezzo_first', 0) or 0)
            
            # Crea il nuovo volo
            nuovo_volo = Volo(
                numero_volo=numero_volo,
                compagnia_id=current_user.compagnia.id,
                aeroporto_partenza_id=aeroporto_partenza_id,
                aeroporto_arrivo_id=aeroporto_arrivo_id,
                data_partenza=data_partenza,
                data_arrivo=data_arrivo,
                posti_economy=posti_economy,
                posti_business=posti_business,
                posti_first=posti_first,
                posti_totali=posti_totali,
                prezzo_economy=prezzo_economy,
                prezzo_business=prezzo_business,
                prezzo_first=prezzo_first
            )
            
            # Il calcolo dei posti totali è ora gestito dal trigger
            # La validazione delle date è ora gestita dal trigger
            
            db.session.add(nuovo_volo)
            db.session.commit()
            
            flash('Volo aggiunto con successo!', 'success')
            return redirect(url_for('airline.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante l\'aggiunta del volo: {str(e)}', 'danger')
    
    # GET request: mostra il form
    aeroporti = Aeroporto.query.all()
    return render_template('airline/nuovo_volo.html', aeroporti=aeroporti)

@airline.route('/statistiche')
@login_required
def statistiche():
    if not current_user.is_airline:
        flash('Accesso non autorizzato', 'error')
        return redirect(url_for('main.index'))
    
    # Statistiche per tratta
    tratte = db.session.query(
        Aeroporto.città.label('partenza'),
        func.count(Volo.id).label('numero_voli'),
        func.count(Biglietto.id).label('passeggeri'),
        func.sum(Biglietto.prezzo).label('guadagno')
    ).join(
        Volo, Volo.departure_airport_id == Aeroporto.id
    ).join(
        Biglietto, Biglietto.flight_id == Volo.id
    ).filter(
        Volo.compagnia_id == current_user.compagnia.id
    ).group_by(
        Aeroporto.città
    ).all()
    
    return render_template('airline/statistiche.html', tratte=tratte)

@airline.route('/lista_voli')
@login_required
def lista_voli():
    # Verifica che l'utente sia una compagnia aerea
    if not current_user.is_airline:
        flash('Non hai i permessi per accedere a questa pagina.', 'danger')
        return redirect(url_for('main.index'))
    
    # Recupera i voli della compagnia
    voli = Volo.query.filter_by(compagnia_id=current_user.compagnia.id).order_by(Volo.data_partenza.desc()).all()
    
    return render_template('airline/lista_voli.html', voli=voli, now=datetime.now())

@airline.route('/modifica_volo/<int:volo_id>', methods=['GET', 'POST'])
@login_required
def modifica_volo(volo_id):
    if not current_user.is_airline:
        flash('Accesso non autorizzato.', 'danger')
        return redirect(url_for('main.index'))

    volo = Volo.query.get_or_404(volo_id)
    aeroporti = Aeroporto.query.all()

    if request.method == 'POST':
        try:
            volo.numero_volo = request.form.get('numero_volo')
            volo.aeroporto_partenza_id = request.form.get('aeroporto_partenza_id')
            volo.aeroporto_arrivo_id = request.form.get('aeroporto_arrivo_id')
            volo.data_partenza = datetime.strptime(request.form.get('data_partenza'), '%Y-%m-%dT%H:%M')
            volo.data_arrivo = datetime.strptime(request.form.get('data_arrivo'), '%Y-%m-%dT%H:%M')
            volo.posti_economy = int(request.form.get('posti_economy', 0) or 0)
            volo.posti_business = int(request.form.get('posti_business', 0) or 0)
            volo.posti_first = int(request.form.get('posti_first', 0) or 0)
            volo.prezzo_economy = float(request.form.get('prezzo_economy', 0) or 0)
            volo.prezzo_business = float(request.form.get('prezzo_business', 0) or 0)
            volo.prezzo_first = float(request.form.get('prezzo_first', 0) or 0)
            # Il calcolo dei posti_totali è gestito dal trigger
            db.session.commit()
            flash('Volo modificato con successo!', 'success')
            return redirect(url_for('airline.lista_voli'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica del volo: {str(e)}', 'danger')
    # GET: mostra il form precompilato
    return render_template('airline/modifica_volo.html', volo=volo, aeroporti=aeroporti)

@airline.route('/elimina_volo/<int:volo_id>', methods=['POST'])
@login_required
def elimina_volo(volo_id):
    if not current_user.is_airline:
        flash('Accesso non autorizzato.', 'danger')
        return redirect(url_for('main.index'))
    volo = Volo.query.get_or_404(volo_id)
    if volo.compagnia_id != current_user.compagnia.id:
        flash('Non puoi eliminare un volo che non appartiene alla tua compagnia.', 'danger')
        return redirect(url_for('airline.lista_voli'))
    try:
        db.session.delete(volo)
        db.session.commit()
        flash('Volo eliminato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione del volo: {str(e)}', 'danger')
    return redirect(url_for('airline.lista_voli')) 
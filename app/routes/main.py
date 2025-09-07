from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from .. import db
from ..models import Volo, Prenotazione, Biglietto, CompagniaAerea, Aeroporto
from ..queries import (
    cerca_voli_diretti,
    cerca_voli_scalo,
    statistiche_compagnia,
    prenotazioni_utente,
    verifica_disponibilità_posti
)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Homepage dell'applicazione"""
    aeroporti = Aeroporto.query.all()
    return render_template('index.html', aeroporti=aeroporti)

@main.route('/cerca_voli', methods=['GET', 'POST'])
def cerca_voli():
    """Pagina di ricerca voli"""
    # Recupera la lista degli aeroporti
    aeroporti = Aeroporto.query.all()
    
    if request.method == 'POST':
        try:
            # Recupera i parametri dal form
            aeroporto_partenza = request.form.get('aeroporto_partenza')
            aeroporto_arrivo = request.form.get('aeroporto_arrivo')
            data = datetime.strptime(request.form.get('data'), '%Y-%m-%d')
            passeggeri = int(request.form.get('passeggeri', 1))
            classe = request.form.get('classe', 'economy')
            ordina_per = request.form.get('ordina_per', 'prezzo')
            
            # Cerca voli diretti
            voli_diretti = cerca_voli_diretti(
                aeroporto_partenza,
                aeroporto_arrivo,
                data,
                passeggeri,
                classe,
                ordina_per
            )
            
            # Cerca voli con scalo
            voli_scalo = cerca_voli_scalo(
                aeroporto_partenza,
                aeroporto_arrivo,
                data
            )
            
            return render_template(
                'risultati_ricerca.html',
                voli_diretti=voli_diretti,
                voli_scalo=voli_scalo,
                aeroporto_partenza=aeroporto_partenza,
                aeroporto_arrivo=aeroporto_arrivo,
                data=data
            )
            
        except ValueError as e:
            flash('Errore nei dati inseriti. Verifica i campi.', 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Errore durante la ricerca dei voli.', 'error')
            
    return render_template('cerca_voli.html', aeroporti=aeroporti)

@main.route('/prenota/<int:volo_id>', methods=['GET', 'POST'])
@login_required
def prenota_volo(volo_id):
    """Pagina di prenotazione di un volo"""
    if request.method == 'POST':
        try:
            disponibilità = verifica_disponibilità_posti(volo_id)
            classe = request.form.get('classe')
            passeggeri = int(request.form.get('passeggeri', 1))
            
            posti_disponibili = getattr(disponibilità, f'posti_{classe}_disponibili')
            if posti_disponibili < passeggeri:
                raise ValueError('Non ci sono abbastanza posti disponibili')
            
            prenotazione = Prenotazione(
                user_id=current_user.id,
                stato='confermata',
                prezzo_totale=0
            )
            db.session.add(prenotazione)
            db.session.flush()
            
            volo = Volo.query.get(volo_id)
            prezzo_base = getattr(volo, f'prezzo_{classe}')
            
            bagaglio_extra_checked = request.form.get('bagaglio_extra') == 'on'
            servizi_extra_checked = request.form.get('servizi_extra') == 'on'
            
            prezzo_per_biglietto = prezzo_base
            servizi_extra_str = ""
            if bagaglio_extra_checked:
                prezzo_per_biglietto += 30
            if servizi_extra_checked:
                prezzo_per_biglietto += 20
                servizi_extra_str = "Servizi Extra"

            prezzo_totale = 0
            for i in range(passeggeri):
                biglietto = Biglietto(
                    booking_id=prenotazione.id,
                    flight_id=volo_id,
                    passeggero_id=current_user.id,
                    classe=classe,
                    numero_posto=f"{classe[0].upper()}{i+1}",
                    prezzo=prezzo_per_biglietto,
                    bagaglio_extra=bagaglio_extra_checked,
                    servizi_extra=servizi_extra_str
                )
                db.session.add(biglietto)
                prezzo_totale += prezzo_per_biglietto
            
            prenotazione.prezzo_totale = prezzo_totale
            db.session.commit()
            
            flash('Prenotazione effettuata con successo!', 'success')
            return redirect(url_for('main.le_mie_prenotazioni'))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Errore durante la prenotazione: {str(e)}', 'error')
    
    volo = Volo.query.get_or_404(volo_id)
    disponibilità = verifica_disponibilità_posti(volo_id)
    return render_template(
        'prenota_volo.html',
        volo=volo,
        disponibilità=disponibilità
    )

@main.route('/le_mie_prenotazioni')
@login_required
def le_mie_prenotazioni():
    """Pagina delle prenotazioni dell'utente"""
    try:
        prenotazioni = prenotazioni_utente(current_user.id)
        return render_template('le_mie_prenotazioni.html', prenotazioni=prenotazioni)
    except SQLAlchemyError as e:
        flash('Errore nel recupero delle prenotazioni.', 'error')
        return redirect(url_for('main.index'))

@main.route('/statistiche/<int:compagnia_id>')
@login_required
def visualizza_statistiche(compagnia_id):
    # Verifica che l'utente sia una compagnia aerea e che stia accedendo alle proprie statistiche
    if not current_user.is_airline or current_user.compagnia.id != compagnia_id:
        flash('Non hai i permessi per accedere a questa pagina.', 'danger')
        return redirect(url_for('main.index'))
    
    # Recupera i dati della compagnia
    compagnia = CompagniaAerea.query.get_or_404(compagnia_id)
    
    # Recupera i voli della compagnia
    voli = Volo.query.filter_by(compagnia_id=compagnia_id).all()

    # Calcola le statistiche
    totale_voli = len(voli)
    voli_completati = sum(1 for volo in voli if volo.data_arrivo < datetime.now())
    voli_in_corso = sum(1 for volo in voli if volo.data_partenza <= datetime.now() <= volo.data_arrivo)
    voli_futuri = sum(1 for volo in voli if volo.data_partenza > datetime.now())

    # Calcola il totale dei posti venduti e disponibili per classe
    posti_economy_venduti = 0
    posti_business_venduti = 0
    posti_first_venduti = 0
    posti_economy_disponibili = 0
    posti_business_disponibili = 0
    posti_first_disponibili = 0

    for volo in voli:
        disponibilita = verifica_disponibilità_posti(volo.id)
        posti_economy_disponibili += disponibilita.posti_economy_disponibili
        posti_business_disponibili += disponibilita.posti_business_disponibili
        posti_first_disponibili += disponibilita.posti_first_disponibili
        posti_economy_venduti += volo.posti_economy - disponibilita.posti_economy_disponibili
        posti_business_venduti += volo.posti_business - disponibilita.posti_business_disponibili
        posti_first_venduti += volo.posti_first - disponibilita.posti_first_disponibili

    # Calcola il totale dei posti per classe
    posti_economy_totali = sum(volo.posti_economy for volo in voli)
    posti_business_totali = sum(volo.posti_business for volo in voli)
    posti_first_totali = sum(volo.posti_first for volo in voli)

    # Calcola le percentuali di occupazione per classe
    occupazione_economy = (posti_economy_venduti / posti_economy_totali * 100) if posti_economy_totali > 0 else 0
    occupazione_business = (posti_business_venduti / posti_business_totali * 100) if posti_business_totali > 0 else 0
    occupazione_first = (posti_first_venduti / posti_first_totali * 100) if posti_first_totali > 0 else 0

    # Calcola il totale dei biglietti venduti
    totale_biglietti = posti_economy_venduti + posti_business_venduti + posti_first_venduti

    # Calcola il totale dei posti disponibili
    totale_posti_disponibili = posti_economy_disponibili + posti_business_disponibili + posti_first_disponibili

    # Calcola il totale dei posti
    totale_posti = posti_economy_totali + posti_business_totali + posti_first_totali

    # Calcola la percentuale di occupazione totale
    occupazione_totale = (totale_biglietti / totale_posti * 100) if totale_posti > 0 else 0

    return render_template('main/statistiche.html',
                         compagnia=compagnia,
                         totale_voli=totale_voli,
                         voli_completati=voli_completati,
                         voli_in_corso=voli_in_corso,
                         voli_futuri=voli_futuri,
                         posti_economy_venduti=posti_economy_venduti,
                         posti_business_venduti=posti_business_venduti,
                         posti_first_venduti=posti_first_venduti,
                         posti_economy_disponibili=posti_economy_disponibili,
                         posti_business_disponibili=posti_business_disponibili,
                         posti_first_disponibili=posti_first_disponibili,
                         posti_economy_totali=posti_economy_totali,
                         posti_business_totali=posti_business_totali,
                         posti_first_totali=posti_first_totali,
                         occupazione_economy=occupazione_economy,
                         occupazione_business=occupazione_business,
                         occupazione_first=occupazione_first,
                         totale_biglietti=totale_biglietti,
                         totale_posti_disponibili=totale_posti_disponibili,
                         totale_posti=totale_posti,
                         occupazione_totale=occupazione_totale)

@main.route('/api/verifica_disponibilità/<int:volo_id>')
def api_verifica_disponibilità(volo_id):
    """API per verificare la disponibilità dei posti di un volo"""
    try:
        disponibilità = verifica_disponibilità_posti(volo_id)
        return jsonify({
            'economy': disponibilità.posti_economy_disponibili,
            'business': disponibilità.posti_business_disponibili,
            'first': disponibilità.posti_first_disponibili
        })
    except SQLAlchemyError as e:
        return jsonify({'error': 'Errore nel recupero della disponibilità'}), 500

@main.route('/compagnie')
def lista_compagnie():
    """Visualizza la lista di tutte le compagnie aeree registrate."""
    compagnie = CompagniaAerea.query.all()
    return render_template('main/compagnie.html', compagnie=compagnie)

@main.route('/acquista_biglietto/<int:volo_id>', methods=['GET', 'POST'])
@login_required
def acquista_biglietto(volo_id):
    if not current_user.is_passenger:
        flash('Solo i passeggeri possono acquistare biglietti.', 'danger')
        return redirect(url_for('main.index'))
    
    volo = Volo.query.get_or_404(volo_id)
    
    if request.method == 'POST':
        try:
            classe = request.form.get('classe')
            prezzo = getattr(volo, f'prezzo_{classe}')
            
            # Crea il biglietto
            biglietto = Biglietto(
                passeggero_id=current_user.id,
                flight_id=volo.id,
                classe=classe,
                prezzo=prezzo,
                data_acquisto=datetime.utcnow()
            )
            
            # La gestione dei posti disponibili è ora gestita dal trigger
            
            db.session.add(biglietto)
            db.session.commit()
            
            flash('Biglietto acquistato con successo!', 'success')
            return redirect(url_for('main.le_mie_prenotazioni'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante l\'acquisto del biglietto: {str(e)}', 'danger')
    
    return render_template('main/acquista_biglietto.html', volo=volo) 
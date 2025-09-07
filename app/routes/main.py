from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
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

@main.route('/stampa_prenotazione/<int:prenotazione_id>')
@login_required
def stampa_prenotazione(prenotazione_id):
    """Genera e scarica il PDF dei biglietti di una prenotazione"""
    try:
        # Recupera la prenotazione e verifica che appartenga all'utente corrente
        prenotazione = Prenotazione.query.get_or_404(prenotazione_id)
        if prenotazione.user_id != current_user.id:
            flash('Non sei autorizzato ad accedere a questa prenotazione', 'error')
            return redirect(url_for('main.le_mie_prenotazioni'))
        
        # Crea il PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Titolo
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.darkblue,
            spaceAfter=30,
            alignment=1  # Centrato
        )
        story.append(Paragraph("BIGLIETTI VOLO", title_style))
        story.append(Spacer(1, 20))
        
        # Informazioni prenotazione
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10
        )
        
        prenotazione_info = [
            f"<b>Numero Prenotazione:</b> #{prenotazione.id}",
            f"<b>Data Prenotazione:</b> {prenotazione.data_prenotazione.strftime('%d/%m/%Y %H:%M')}",
            f"<b>Stato:</b> {prenotazione.stato.title()}",
            f"<b>Passeggero:</b> {current_user.nome} {current_user.cognome}",
            f"<b>Email:</b> {current_user.email}",
            f"<b>Prezzo Totale:</b> €{prenotazione.prezzo_totale:.2f}"
        ]
        
        for info in prenotazione_info:
            story.append(Paragraph(info, info_style))
        
        story.append(Spacer(1, 30))
        
        # Dettagli biglietti
        story.append(Paragraph("<b>DETTAGLI BIGLIETTI</b>", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        for biglietto in prenotazione.biglietti:
            # Recupera i dettagli del volo
            volo = biglietto.volo
            aeroporto_partenza = volo.aeroporto_partenza
            aeroporto_arrivo = volo.aeroporto_arrivo
            compagnia = volo.compagnia
            
            # Crea una tabella per ogni biglietto
            biglietto_data = [
                ['Volo', volo.numero_volo],
                ['Compagnia', compagnia.nome_compagnia],
                ['Da', f"{aeroporto_partenza.nome} ({aeroporto_partenza.codice_iata})"],
                ['A', f"{aeroporto_arrivo.nome} ({aeroporto_arrivo.codice_iata})"],
                ['Partenza', volo.data_partenza.strftime('%d/%m/%Y %H:%M')],
                ['Arrivo', volo.data_arrivo.strftime('%d/%m/%Y %H:%M')],
                ['Classe', biglietto.classe.title()],
                ['Posto', biglietto.numero_posto or 'Da assegnare'],
                ['Prezzo', f"€{biglietto.prezzo:.2f}"],
            ]
            
            if biglietto.bagaglio_extra:
                biglietto_data.append(['Bagaglio Extra', 'Incluso'])
            
            if biglietto.servizi_extra:
                biglietto_data.append(['Servizi Extra', biglietto.servizi_extra])
            
            biglietto_table = Table(biglietto_data, colWidths=[2*inch, 4*inch])
            biglietto_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(biglietto_table)
            story.append(Spacer(1, 20))
        
        # Note finali
        story.append(Spacer(1, 30))
        note_style = ParagraphStyle(
            'NoteStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=1  # Centrato
        )
        
        note_text = """
        <b>IMPORTANTE:</b><br/>
        • Presentarsi all'aeroporto almeno 2 ore prima della partenza per voli internazionali<br/>
        • Presentarsi all'aeroporto almeno 1 ora prima della partenza per voli nazionali<br/>
        • Portare con sé un documento di identità valido<br/>
        • Verificare le restrizioni sui bagagli presso la compagnia aerea
        """
        
        story.append(Paragraph(note_text, note_style))
        
        # Genera il PDF
        doc.build(story)
        buffer.seek(0)
        
        # Crea la risposta HTTP
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=biglietti_prenotazione_{prenotazione_id}.pdf'
        
        return response
        
    except Exception as e:
        flash(f'Errore durante la generazione del PDF: {str(e)}', 'error')
        return redirect(url_for('main.le_mie_prenotazioni'))
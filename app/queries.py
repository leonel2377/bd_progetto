from datetime import datetime, timedelta
from sqlalchemy import func, case, and_, or_, desc, extract, text
from sqlalchemy.sql import expression
from sqlalchemy.dialects.postgresql import JSON
from .models import db, Volo, CompagniaAerea, Aeroporto, Prenotazione, Biglietto, Utente
from sqlalchemy.orm import aliased

def cerca_voli_diretti(aeroporto_partenza, aeroporto_arrivo, data, passeggeri=1, classe='economy', ordina_per='prezzo'):
    """
    Cerca voli diretti tra due aeroporti in una data specifica.
    
    Args:
        aeroporto_partenza (str): Codice IATA dell'aeroporto di partenza
        aeroporto_arrivo (str): Codice IATA dell'aeroporto di arrivo
        data (datetime/date): Data del volo
        passeggeri (int): Numero di passeggeri
        classe (str): Classe del volo ('economy', 'business', 'first')
        ordina_per (str): Criterio di ordinamento ('prezzo' o 'tempo')
    
    Returns:
        list: Lista di voli disponibili
    """
    # Normaliser la data
    if hasattr(data, 'date'):
        search_date = data.date()
    else:
        search_date = data
    
    posti_map = {
        'economy': Volo.posti_economy,
        'business': Volo.posti_business,
        'first': Volo.posti_first
    }
    
    prezzo_map = {
        'economy': Volo.prezzo_economy,
        'business': Volo.prezzo_business,
        'first': Volo.prezzo_first
    }
    
    AeroportoPartenza = aliased(Aeroporto, name='aeroporto_partenza')
    AeroportoArrivo = aliased(Aeroporto, name='aeroporto_arrivo')
    
    query = db.session.query(
        Volo.id,
        Volo.numero_volo,
        CompagniaAerea.nome_compagnia,
        AeroportoPartenza.città.label('città_partenza'),
        AeroportoArrivo.città.label('città_arrivo'),
        Volo.data_partenza,
        Volo.data_arrivo,
        posti_map[classe].label('posti_disponibili'),
        prezzo_map[classe].label('prezzo')
    ).join(
        CompagniaAerea, Volo.compagnia_id == CompagniaAerea.id
    ).join(
        AeroportoPartenza, Volo.aeroporto_partenza_id == AeroportoPartenza.id
    ).join(
        AeroportoArrivo, Volo.aeroporto_arrivo_id == AeroportoArrivo.id
    ).filter(
        AeroportoPartenza.codice_iata == aeroporto_partenza,
        AeroportoArrivo.codice_iata == aeroporto_arrivo,
        func.date(Volo.data_partenza) == search_date,
        posti_map[classe] >= passeggeri
    )
    
    if ordina_per == 'prezzo':
        query = query.order_by(prezzo_map[classe])
    else:
        query = query.order_by(Volo.data_arrivo - Volo.data_partenza)
    
    return query.all()

def cerca_voli_scalo(città_partenza, città_arrivo, data, tempo_min_scalo=timedelta(hours=2)):
    """
    Cerca voli con uno scalo tra due città in una data specifica.
    """
    # Normaliser la data
    if hasattr(data, 'date'):
        search_date = data.date()
    else:
        search_date = data
    
    AeroportoP = aliased(Aeroporto, name='aeroporto_p')
    AeroportoA = aliased(Aeroporto, name='aeroporto_a')

    # Subquery per trovare tutti i voli disponibili con le città di partenza/arrivo
    voli_disponibili = db.session.query(
        Volo,
        AeroportoP.città.label('città_partenza'),
        AeroportoA.città.label('città_arrivo')
    ).join(
        AeroportoP, Volo.aeroporto_partenza_id == AeroportoP.id
    ).join(
        AeroportoA, Volo.aeroporto_arrivo_id == AeroportoA.id
    ).filter(
        func.date(Volo.data_partenza) == search_date
    ).subquery()

    volo1 = aliased(voli_disponibili, name='volo1')
    volo2 = aliased(voli_disponibili, name='volo2')
    compagnia1 = aliased(CompagniaAerea, name='compagnia1')
    compagnia2 = aliased(CompagniaAerea, name='compagnia2')

    query = db.session.query(
        volo1.c.id.label('volo1_id'),
        volo1.c.numero_volo.label('volo1_numero'),
        compagnia1.nome_compagnia.label('compagnia1'),
        volo1.c.città_partenza.label('città_partenza'),
        volo1.c.città_arrivo.label('città_scalo'),
        volo1.c.data_partenza.label('volo1_data_partenza'),
        volo1.c.data_arrivo.label('volo1_data_arrivo'),

        volo2.c.id.label('volo2_id'),
        volo2.c.numero_volo.label('volo2_numero'),
        compagnia2.nome_compagnia.label('compagnia2'),
        volo2.c.città_arrivo.label('città_arrivo'),
        volo2.c.data_partenza.label('volo2_data_partenza'),
        volo2.c.data_arrivo.label('volo2_data_arrivo'),

        (volo1.c.prezzo_economy + volo2.c.prezzo_economy).label('prezzo_totale')
    ).select_from(volo1).join(
        volo2, and_(
            volo1.c.città_arrivo == volo2.c.città_partenza,
            volo1.c.città_partenza == città_partenza,
            volo2.c.città_arrivo == città_arrivo,
            volo2.c.data_partenza > volo1.c.data_arrivo,
            (volo2.c.data_partenza - volo1.c.data_arrivo) >= tempo_min_scalo
        )
    ).join(compagnia1, volo1.c.compagnia_id == compagnia1.id
    ).join(compagnia2, volo2.c.compagnia_id == compagnia2.id)

    return query.all()

def statistiche_compagnia(compagnia_id, data_inizio, data_fine):
    """
    Calcola le statistiche per una compagnia aerea in un periodo specifico.
    
    Args:
        compagnia_id (int): ID della compagnia aerea
        data_inizio (datetime): Data di inizio periodo
        data_fine (datetime): Data di fine periodo
    
    Returns:
        dict: Statistiche della compagnia o None se non ci sono dati
    """
    # Prima verifica se la compagnia esiste
    compagnia = CompagniaAerea.query.get(compagnia_id)
    if not compagnia:
        return None
        
    # Query per le statistiche
    query = db.session.query(
        CompagniaAerea.nome_compagnia,
        func.count(func.distinct(Volo.id)).label('numero_voli'),
        func.count(Biglietto.id).label('numero_passeggeri'),
        func.coalesce(func.sum(Biglietto.prezzo), 0).label('guadagno_totale'),
        func.coalesce(func.avg(Biglietto.prezzo), 0).label('prezzo_medio'),
        func.count(func.distinct(case(
            (Biglietto.classe == 'economy', Biglietto.id),
            else_=None
        ))).label('passeggeri_economy'),
        func.count(func.distinct(case(
            (Biglietto.classe == 'business', Biglietto.id),
            else_=None
        ))).label('passeggeri_business'),
        func.count(func.distinct(case(
            (Biglietto.classe == 'first', Biglietto.id),
            else_=None
        ))).label('passeggeri_first')
    ).join(
        Volo, CompagniaAerea.id == Volo.compagnia_id
    ).outerjoin(
        Biglietto, Volo.id == Biglietto.flight_id
    ).filter(
        CompagniaAerea.id == compagnia_id,
        Volo.data_partenza >= data_inizio,
        Volo.data_partenza <= data_fine
    ).group_by(
        CompagniaAerea.id,
        CompagniaAerea.nome_compagnia
    )
    
    result = query.first()
    
    # Se non ci sono voli nel periodo, restituisci statistiche a zero
    if not result or result.numero_voli == 0:
        return type('Statistiche', (), {
            'nome_compagnia': compagnia.nome_compagnia,
            'numero_voli': 0,
            'numero_passeggeri': 0,
            'guadagno_totale': 0,
            'prezzo_medio': 0,
            'passeggeri_economy': 0,
            'passeggeri_business': 0,
            'passeggeri_first': 0
        })
    
    return result

def prenotazioni_utente(user_id):
    """
    Recupera tutte le prenotazioni di un utente con i dettagli dei biglietti.
    
    Args:
        user_id (int): ID dell'utente
    
    Returns:
        list: Lista di prenotazioni con dettagli
    """
    AeroportoPartenza = aliased(Aeroporto)
    AeroportoArrivo = aliased(Aeroporto)
    
    # Query per le prenotazioni
    prenotazioni = db.session.query(
        Prenotazione
    ).filter(
        Prenotazione.user_id == user_id
    ).order_by(
        desc(Prenotazione.data_prenotazione)
    ).all()
    
    # Per ogni prenotazione, recupera i dettagli dei biglietti
    for prenotazione in prenotazioni:
        biglietti = db.session.query(
            Biglietto,
            Volo.numero_volo.label('volo'),
            CompagniaAerea.nome_compagnia.label('compagnia'),
            AeroportoPartenza.città.label('partenza'),
            AeroportoArrivo.città.label('arrivo'),
            Volo.data_partenza,
            Volo.data_arrivo
        ).join(
            Volo, Biglietto.flight_id == Volo.id
        ).join(
            CompagniaAerea, Volo.compagnia_id == CompagniaAerea.id
        ).join(
            AeroportoPartenza, Volo.aeroporto_partenza_id == AeroportoPartenza.id
        ).join(
            AeroportoArrivo, Volo.aeroporto_arrivo_id == AeroportoArrivo.id
        ).filter(
            Biglietto.booking_id == prenotazione.id
        ).all()
        
        # Aggiungi i dettagli dei biglietti alla prenotazione
        prenotazione.dettagli_biglietti = []
        for biglietto, volo, compagnia, partenza, arrivo, data_partenza, data_arrivo in biglietti:
            biglietto_obj = type('BigliettoDettagli', (), {
                'volo': volo,
                'compagnia': compagnia,
                'partenza': partenza,
                'arrivo': arrivo,
                'data_partenza': data_partenza,
                'data_arrivo': data_arrivo,
                'classe': biglietto.classe,
                'posto': biglietto.numero_posto,
                'prezzo': biglietto.prezzo,
                'bagaglio_extra': biglietto.bagaglio_extra,
                'servizi_extra': biglietto.servizi_extra
            })()
            prenotazione.dettagli_biglietti.append(biglietto_obj)
    
    return prenotazioni

def verifica_disponibilità_posti(volo_id):
    """
    Verifica la disponibilità dei posti per un volo specifico.
    
    Args:
        volo_id (int): ID del volo
    
    Returns:
        dict: Disponibilità posti per ogni classe
    """
    query = db.session.query(
        Volo.id,
        Volo.numero_volo,
        (Volo.posti_economy - func.count(case((Biglietto.classe == 'economy', 1)))).label('posti_economy_disponibili'),
        (Volo.posti_business - func.count(case((Biglietto.classe == 'business', 1)))).label('posti_business_disponibili'),
        (Volo.posti_first - func.count(case((Biglietto.classe == 'first', 1)))).label('posti_first_disponibili')
    ).outerjoin(
        Biglietto, Volo.id == Biglietto.flight_id
    ).filter(
        Volo.id == volo_id
    ).group_by(
        Volo.id,
        Volo.numero_volo,
        Volo.posti_economy,
        Volo.posti_business,
        Volo.posti_first
    )
    
    return query.first() 
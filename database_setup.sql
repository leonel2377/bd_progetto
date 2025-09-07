-- Creazione del database
CREATE DATABASE flight_booking WITH 
    ENCODING = 'UTF8',
    LC_COLLATE = 'Italian_Italy.1252',
    LC_CTYPE = 'Italian_Italy.1252',
    TEMPLATE = template0;

\c flight_booking

-- Creazione delle tabelle con vincoli di integrità
CREATE TABLE utente (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    nome VARCHAR(64),
    cognome VARCHAR(64),
    tipo_utente VARCHAR(20) CHECK (tipo_utente IN ('compagnia', 'passeggero')),
    data_registrazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE compagnia_aerea (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES utente(id) ON DELETE CASCADE,
    nome_compagnia VARCHAR(100) NOT NULL,
    codice_iata CHAR(2) UNIQUE NOT NULL,
    sede_legale VARCHAR(100)
);

CREATE TABLE aeroporto (
    id SERIAL PRIMARY KEY,
    codice_iata CHAR(3) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    città VARCHAR(100) NOT NULL,
    paese VARCHAR(100) NOT NULL
);

CREATE TABLE volo (
    id SERIAL PRIMARY KEY,
    airline_id INTEGER REFERENCES compagnia_aerea(id) ON DELETE CASCADE,
    numero_volo VARCHAR(10) NOT NULL,
    departure_airport_id INTEGER REFERENCES aeroporto(id),
    arrival_airport_id INTEGER REFERENCES aeroporto(id),
    data_partenza TIMESTAMP NOT NULL,
    data_arrivo TIMESTAMP NOT NULL,
    posti_totali INTEGER NOT NULL,
    posti_economy INTEGER NOT NULL,
    posti_business INTEGER NOT NULL,
    posti_first INTEGER NOT NULL,
    prezzo_economy DECIMAL(10,2) NOT NULL,
    prezzo_business DECIMAL(10,2) NOT NULL,
    prezzo_first DECIMAL(10,2) NOT NULL,
    CONSTRAINT check_date CHECK (data_arrivo > data_partenza),
    CONSTRAINT check_posti CHECK (
        posti_totali = posti_economy + posti_business + posti_first
        AND posti_economy >= 0
        AND posti_business >= 0
        AND posti_first >= 0
    ),
    CONSTRAINT check_prezzi CHECK (
        prezzo_economy > 0
        AND prezzo_business > 0
        AND prezzo_first > 0
    )
);

CREATE TABLE prenotazione (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES utente(id) ON DELETE CASCADE,
    data_prenotazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stato VARCHAR(20) DEFAULT 'confermata' CHECK (stato IN ('confermata', 'cancellata', 'completata')),
    prezzo_totale DECIMAL(10,2) NOT NULL CHECK (prezzo_totale > 0)
);

CREATE TABLE biglietto (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES prenotazione(id) ON DELETE CASCADE,
    flight_id INTEGER REFERENCES volo(id) ON DELETE CASCADE,
    classe VARCHAR(20) NOT NULL CHECK (classe IN ('economy', 'business', 'first')),
    numero_posto VARCHAR(10),
    prezzo DECIMAL(10,2) NOT NULL CHECK (prezzo > 0),
    bagaglio_extra BOOLEAN DEFAULT FALSE,
    servizi_extra VARCHAR(200)
);

-- Creazione degli indici
CREATE INDEX idx_utente_email ON utente(email);
CREATE INDEX idx_compagnia_codice ON compagnia_aerea(codice_iata);
CREATE INDEX idx_aeroporto_codice ON aeroporto(codice_iata);
CREATE INDEX idx_volo_ricerca ON volo(departure_airport_id, arrival_airport_id, data_partenza);
CREATE INDEX idx_biglietto_volo_classe ON biglietto(flight_id, classe);
CREATE INDEX idx_prenotazione_user ON prenotazione(user_id);
CREATE INDEX idx_biglietto_booking ON biglietto(booking_id);

-- Funzioni e trigger per la gestione automatica
CREATE OR REPLACE FUNCTION verifica_disponibilita_posti()
RETURNS TRIGGER AS $$
BEGIN
    -- Verifica se ci sono posti disponibili per la classe selezionata
    IF NEW.classe = 'economy' AND 
       (SELECT posti_economy FROM volo WHERE id = NEW.flight_id) <= 0 THEN
        RAISE EXCEPTION 'Nessun posto economy disponibile per questo volo';
    ELSIF NEW.classe = 'business' AND 
          (SELECT posti_business FROM volo WHERE id = NEW.flight_id) <= 0 THEN
        RAISE EXCEPTION 'Nessun posto business disponibile per questo volo';
    ELSIF NEW.classe = 'first' AND 
          (SELECT posti_first FROM volo WHERE id = NEW.flight_id) <= 0 THEN
        RAISE EXCEPTION 'Nessun posto first class disponibile per questo volo';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_verifica_posti
    BEFORE INSERT ON biglietto
    FOR EACH ROW
    EXECUTE FUNCTION verifica_disponibilita_posti();

CREATE OR REPLACE FUNCTION aggiorna_posti_disponibili()
RETURNS TRIGGER AS $$
BEGIN
    -- Aggiorna i posti disponibili quando viene inserito un nuovo biglietto
    IF NEW.classe = 'economy' THEN
        UPDATE volo SET posti_economy = posti_economy - 1 WHERE id = NEW.flight_id;
    ELSIF NEW.classe = 'business' THEN
        UPDATE volo SET posti_business = posti_business - 1 WHERE id = NEW.flight_id;
    ELSIF NEW.classe = 'first' THEN
        UPDATE volo SET posti_first = posti_first - 1 WHERE id = NEW.flight_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_aggiorna_posti
    AFTER INSERT ON biglietto
    FOR EACH ROW
    EXECUTE FUNCTION aggiorna_posti_disponibili();

CREATE OR REPLACE FUNCTION ripristina_posti_disponibili()
RETURNS TRIGGER AS $$
BEGIN
    -- Ripristina i posti disponibili quando viene cancellato un biglietto
    IF OLD.classe = 'economy' THEN
        UPDATE volo SET posti_economy = posti_economy + 1 WHERE id = OLD.flight_id;
    ELSIF OLD.classe = 'business' THEN
        UPDATE volo SET posti_business = posti_business + 1 WHERE id = OLD.flight_id;
    ELSIF OLD.classe = 'first' THEN
        UPDATE volo SET posti_first = posti_first + 1 WHERE id = OLD.flight_id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_ripristina_posti
    AFTER DELETE ON biglietto
    FOR EACH ROW
    EXECUTE FUNCTION ripristina_posti_disponibili();

-- Viste materializzate per le statistiche
CREATE MATERIALIZED VIEW statistiche_compagnie AS
SELECT 
    ca.id AS compagnia_id,
    ca.nome_compagnia,
    COUNT(DISTINCT v.id) AS numero_voli,
    COUNT(b.id) AS numero_passeggeri,
    SUM(b.prezzo) AS guadagno_totale,
    AVG(b.prezzo) AS prezzo_medio
FROM compagnia_aerea ca
LEFT JOIN volo v ON ca.id = v.airline_id
LEFT JOIN biglietto b ON v.id = b.flight_id
GROUP BY ca.id, ca.nome_compagnia;

CREATE MATERIALIZED VIEW tratte_popolari AS
SELECT 
    a1.città AS città_partenza,
    a2.città AS città_arrivo,
    COUNT(DISTINCT v.id) AS numero_voli,
    COUNT(b.id) AS numero_passeggeri,
    AVG(b.prezzo) AS prezzo_medio
FROM volo v
JOIN aeroporto a1 ON v.departure_airport_id = a1.id
JOIN aeroporto a2 ON v.arrival_airport_id = a2.id
LEFT JOIN biglietto b ON v.id = b.flight_id
GROUP BY a1.città, a2.città;

CREATE MATERIALIZED VIEW occupazione_classi AS
SELECT 
    v.id AS volo_id,
    v.numero_volo,
    v.posti_economy - COUNT(CASE WHEN b.classe = 'economy' THEN 1 END) AS posti_economy_disponibili,
    v.posti_business - COUNT(CASE WHEN b.classe = 'business' THEN 1 END) AS posti_business_disponibili,
    v.posti_first - COUNT(CASE WHEN b.classe = 'first' THEN 1 END) AS posti_first_disponibili
FROM volo v
LEFT JOIN biglietto b ON v.id = b.flight_id
GROUP BY v.id, v.numero_volo, v.posti_economy, v.posti_business, v.posti_first;

-- Funzione per aggiornare le viste materializzate
CREATE OR REPLACE FUNCTION aggiorna_statistiche()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY statistiche_compagnie;
    REFRESH MATERIALIZED VIEW CONCURRENTLY tratte_popolari;
    REFRESH MATERIALIZED VIEW CONCURRENTLY occupazione_classi;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger per aggiornare le statistiche quando cambiano i dati
CREATE TRIGGER trigger_aggiorna_statistiche
    AFTER INSERT OR UPDATE OR DELETE ON biglietto
    FOR EACH STATEMENT
    EXECUTE FUNCTION aggiorna_statistiche(); 
-- Création des tables pour le système de gestion des vols

-- Table UTENTE
CREATE TABLE UTENTE (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nome VARCHAR(100),
    cognome VARCHAR(100),
    tipo_utente VARCHAR(20) CHECK (tipo_utente IN ('compagnia', 'passeggero')),
    data_registrazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table COMPAGNIA_AEREA
CREATE TABLE COMPAGNIA_AEREA (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES UTENTE(id),
    nome_compagnia VARCHAR(100) NOT NULL,
    codice_iata VARCHAR(3) UNIQUE NOT NULL,
    sede_legale VARCHAR(255)
);

-- Table AEROPORTO
CREATE TABLE AEROPORTO (
    id SERIAL PRIMARY KEY,
    codice_iata VARCHAR(3) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    città VARCHAR(100) NOT NULL,
    paese VARCHAR(100) NOT NULL
);

-- Table VOLO
CREATE TABLE VOLO (
    id SERIAL PRIMARY KEY,
    airline_id INTEGER REFERENCES COMPAGNIA_AEREA(id),
    numero_volo VARCHAR(10) NOT NULL,
    departure_airport_id INTEGER REFERENCES AEROPORTO(id),
    arrival_airport_id INTEGER REFERENCES AEROPORTO(id),
    data_partenza TIMESTAMP NOT NULL,
    data_arrivo TIMESTAMP NOT NULL,
    posti_totali INTEGER NOT NULL,
    posti_economy INTEGER NOT NULL CHECK (posti_economy >= 0),
    posti_business INTEGER NOT NULL CHECK (posti_business >= 0),
    posti_first INTEGER NOT NULL CHECK (posti_first >= 0),
    prezzo_economy DECIMAL(10,2) NOT NULL CHECK (prezzo_economy > 0),
    prezzo_business DECIMAL(10,2) NOT NULL CHECK (prezzo_business > 0),
    prezzo_first DECIMAL(10,2) NOT NULL CHECK (prezzo_first > 0),
    CHECK (data_arrivo > data_partenza),
    CHECK (posti_totali = posti_economy + posti_business + posti_first)
);

-- Table PRENOTAZIONE
CREATE TABLE PRENOTAZIONE (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES UTENTE(id),
    data_prenotazione TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stato VARCHAR(20) CHECK (stato IN ('confermata', 'cancellata', 'completata')),
    prezzo_totale DECIMAL(10,2) NOT NULL CHECK (prezzo_totale > 0)
);

-- Table BIGLIETTO
CREATE TABLE BIGLIETTO (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES PRENOTAZIONE(id),
    flight_id INTEGER REFERENCES VOLO(id),
    classe VARCHAR(20) CHECK (classe IN ('economy', 'business', 'first')),
    numero_posto VARCHAR(10),
    prezzo DECIMAL(10,2) NOT NULL CHECK (prezzo > 0),
    bagaglio_extra BOOLEAN DEFAULT FALSE,
    servizi_extra TEXT
);

-- Création des index
CREATE INDEX idx_utente_email ON UTENTE(email);
CREATE INDEX idx_compagnia_codice_iata ON COMPAGNIA_AEREA(codice_iata);
CREATE INDEX idx_aeroporto_codice_iata ON AEROPORTO(codice_iata);
CREATE INDEX idx_volo_ricerca ON VOLO(departure_airport_id, arrival_airport_id, data_partenza);
CREATE INDEX idx_biglietto_volo_classe ON BIGLIETTO(flight_id, classe);

-- Trigger pour vérifier la disponibilité dei posti
CREATE OR REPLACE FUNCTION check_seat_availability()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.classe = 'economy' THEN
        IF (SELECT posti_economy FROM VOLO WHERE id = NEW.flight_id) <= 0 THEN
            RAISE EXCEPTION 'Non ci sono più posti disponibili in economy';
        END IF;
    ELSIF NEW.classe = 'business' THEN
        IF (SELECT posti_business FROM VOLO WHERE id = NEW.flight_id) <= 0 THEN
            RAISE EXCEPTION 'Non ci sono più posti disponibili in business';
        END IF;
    ELSIF NEW.classe = 'first' THEN
        IF (SELECT posti_first FROM VOLO WHERE id = NEW.flight_id) <= 0 THEN
            RAISE EXCEPTION 'Non ci sono più posti disponibili in first';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_seats_before_insert
BEFORE INSERT ON BIGLIETTO
FOR EACH ROW
EXECUTE FUNCTION check_seat_availability();

-- Trigger per aggiornare i posti disponibili
CREATE OR REPLACE FUNCTION update_available_seats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.classe = 'economy' THEN
        UPDATE VOLO SET posti_economy = posti_economy - 1 WHERE id = NEW.flight_id;
    ELSIF NEW.classe = 'business' THEN
        UPDATE VOLO SET posti_business = posti_business - 1 WHERE id = NEW.flight_id;
    ELSIF NEW.classe = 'first' THEN
        UPDATE VOLO SET posti_first = posti_first - 1 WHERE id = NEW.flight_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_seats_after_insert
AFTER INSERT ON BIGLIETTO
FOR EACH ROW
EXECUTE FUNCTION update_available_seats();

-- Trigger per calcolare il prezzo totale della prenotazione
CREATE OR REPLACE FUNCTION update_booking_total()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE PRENOTAZIONE 
    SET prezzo_totale = (
        SELECT SUM(prezzo) 
        FROM BIGLIETTO 
        WHERE booking_id = NEW.booking_id
    )
    WHERE id = NEW.booking_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_booking_total_after_ticket
AFTER INSERT OR UPDATE OR DELETE ON BIGLIETTO
FOR EACH ROW
EXECUTE FUNCTION update_booking_total(); 
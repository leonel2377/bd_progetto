-- Funzione per calcolare i posti totali
CREATE OR REPLACE FUNCTION calcola_posti_totali()
RETURNS TRIGGER AS $$
BEGIN
    NEW.posti_totali := NEW.posti_economy + NEW.posti_business + NEW.posti_first;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per calcolare automaticamente i posti totali
CREATE TRIGGER trigger_calcola_posti_totali
    BEFORE INSERT OR UPDATE ON volo
    FOR EACH ROW
    EXECUTE FUNCTION calcola_posti_totali();

-- Funzione per validare le date dei voli
CREATE OR REPLACE FUNCTION valida_date_volo()
RETURNS TRIGGER AS $$
BEGIN
    -- Verifica che la data di partenza non sia nel passato
    IF NEW.data_partenza < CURRENT_TIMESTAMP THEN
        RAISE EXCEPTION 'La data di partenza non può essere nel passato';
    END IF;
    
    -- Verifica che la data di arrivo sia successiva alla data di partenza
    IF NEW.data_arrivo <= NEW.data_partenza THEN
        RAISE EXCEPTION 'La data di arrivo deve essere successiva alla data di partenza';
    END IF;
    
    -- Verifica che la durata del volo sia ragionevole (max 24 ore)
    IF (NEW.data_arrivo - NEW.data_partenza) > INTERVAL '24 hours' THEN
        RAISE EXCEPTION 'La durata del volo non può superare le 24 ore';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per validare le date dei voli
CREATE TRIGGER trigger_valida_date_volo
    BEFORE INSERT OR UPDATE ON volo
    FOR EACH ROW
    EXECUTE FUNCTION valida_date_volo();

-- Funzione per aggiornare i posti disponibili
CREATE OR REPLACE FUNCTION aggiorna_posti_disponibili()
RETURNS TRIGGER AS $$
DECLARE
    posti_disponibili INTEGER;
BEGIN
    -- Verifica la disponibilità dei posti per la classe selezionata
    IF NEW.classe = 'economy' THEN
        SELECT posti_economy INTO posti_disponibili
        FROM volo
        WHERE id = NEW.flight_id
        FOR UPDATE;
        
        IF posti_disponibili <= 0 THEN
            RAISE EXCEPTION 'Non ci sono più posti disponibili in classe economy';
        END IF;
        
        UPDATE volo
        SET posti_economy = posti_economy - 1
        WHERE id = NEW.flight_id;
        
    ELSIF NEW.classe = 'business' THEN
        SELECT posti_business INTO posti_disponibili
        FROM volo
        WHERE id = NEW.flight_id
        FOR UPDATE;
        
        IF posti_disponibili <= 0 THEN
            RAISE EXCEPTION 'Non ci sono più posti disponibili in classe business';
        END IF;
        
        UPDATE volo
        SET posti_business = posti_business - 1
        WHERE id = NEW.flight_id;
        
    ELSIF NEW.classe = 'first' THEN
        SELECT posti_first INTO posti_disponibili
        FROM volo
        WHERE id = NEW.flight_id
        FOR UPDATE;
        
        IF posti_disponibili <= 0 THEN
            RAISE EXCEPTION 'Non ci sono più posti disponibili in classe first';
        END IF;
        
        UPDATE volo
        SET posti_first = posti_first - 1
        WHERE id = NEW.flight_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per aggiornare i posti disponibili
CREATE TRIGGER trigger_aggiorna_posti_disponibili
    BEFORE INSERT ON biglietto
    FOR EACH ROW
    EXECUTE FUNCTION aggiorna_posti_disponibili();

-- Funzione per il logging delle modifiche
CREATE OR REPLACE FUNCTION log_modifiche_volo()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log_modifiche (
        tabella,
        id_record,
        tipo_operazione,
        dati_vecchi,
        dati_nuovi,
        data_modifica,
        utente
    ) VALUES (
        'volo',
        NEW.id,
        CASE
            WHEN TG_OP = 'INSERT' THEN 'INSERT'
            WHEN TG_OP = 'UPDATE' THEN 'UPDATE'
            WHEN TG_OP = 'DELETE' THEN 'DELETE'
        END,
        CASE
            WHEN TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN row_to_json(OLD)
            ELSE NULL
        END,
        CASE
            WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN row_to_json(NEW)
            ELSE NULL
        END,
        CURRENT_TIMESTAMP,
        current_user
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per il logging delle modifiche
CREATE TRIGGER trigger_log_modifiche_volo
    AFTER INSERT OR UPDATE OR DELETE ON volo
    FOR EACH ROW
    EXECUTE FUNCTION log_modifiche_volo();

-- Tabella per il logging delle modifiche
CREATE TABLE IF NOT EXISTS log_modifiche (
    id SERIAL PRIMARY KEY,
    tabella VARCHAR(50) NOT NULL,
    id_record INTEGER NOT NULL,
    tipo_operazione VARCHAR(10) NOT NULL,
    dati_vecchi JSONB,
    dati_nuovi JSONB,
    data_modifica TIMESTAMP NOT NULL,
    utente VARCHAR(100) NOT NULL
); 
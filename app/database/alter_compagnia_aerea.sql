-- Modifica la tabella compagnia_aerea per rendere i campi codice_iata e sede_legale nullable
ALTER TABLE compagnia_aerea 
    ALTER COLUMN codice_iata DROP NOT NULL,
    ALTER COLUMN sede_legale DROP NOT NULL; 
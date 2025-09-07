-- Inserimento dati di esempio
-- Nota: le password sono hash di 'password123' per tutti gli utenti

-- Inserimento utenti e compagnie aeree
INSERT INTO utente (email, password_hash, nome, cognome, tipo_utente) VALUES
('alitalia@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/IeG', 'Alitalia', 'S.p.A.', 'compagnia'),
('ryanair@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/IeG', 'Ryanair', 'Holdings', 'compagnia'),
('easyjet@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/IeG', 'EasyJet', 'Airline', 'compagnia'),
('mario.rossi@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/IeG', 'Mario', 'Rossi', 'passeggero'),
('laura.bianchi@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/IeG', 'Laura', 'Bianchi', 'passeggero');

INSERT INTO compagnia_aerea (user_id, nome_compagnia, codice_iata, sede_legale) VALUES
(1, 'Alitalia', 'AZ', 'Roma'),
(2, 'Ryanair', 'FR', 'Dublino'),
(3, 'EasyJet', 'U2', 'Londra');

-- Inserimento aeroporti
INSERT INTO aeroporto (codice_iata, nome, città, paese) VALUES
('FCO', 'Leonardo da Vinci', 'Roma', 'Italia'),
('MXP', 'Malpensa', 'Milano', 'Italia'),
('LHR', 'Heathrow', 'Londra', 'Regno Unito'),
('CDG', 'Charles de Gaulle', 'Parigi', 'Francia'),
('FRA', 'Francoforte', 'Francoforte', 'Germania'),
('MAD', 'Barajas', 'Madrid', 'Spagna'),
('BCN', 'El Prat', 'Barcellona', 'Spagna'),
('AMS', 'Schiphol', 'Amsterdam', 'Paesi Bassi');

-- Inserimento voli
INSERT INTO volo (airline_id, numero_volo, departure_airport_id, arrival_airport_id, 
                 data_partenza, data_arrivo, posti_totali, posti_economy, posti_business, 
                 posti_first, prezzo_economy, prezzo_business, prezzo_first) VALUES
-- Alitalia
(1, 'AZ100', 1, 3, '2024-04-15 10:00:00', '2024-04-15 12:00:00', 180, 150, 20, 10, 150.00, 300.00, 500.00),
(1, 'AZ101', 3, 1, '2024-04-15 14:00:00', '2024-04-15 16:00:00', 180, 150, 20, 10, 150.00, 300.00, 500.00),
(1, 'AZ200', 1, 4, '2024-04-15 08:00:00', '2024-04-15 10:00:00', 180, 150, 20, 10, 120.00, 250.00, 450.00),
-- Ryanair
(2, 'FR100', 2, 3, '2024-04-15 09:00:00', '2024-04-15 11:00:00', 189, 189, 0, 0, 50.00, 0.00, 0.00),
(2, 'FR101', 3, 2, '2024-04-15 13:00:00', '2024-04-15 15:00:00', 189, 189, 0, 0, 50.00, 0.00, 0.00),
(2, 'FR200', 2, 6, '2024-04-15 07:00:00', '2024-04-15 09:00:00', 189, 189, 0, 0, 40.00, 0.00, 0.00),
-- EasyJet
(3, 'U2100', 1, 5, '2024-04-15 11:00:00', '2024-04-15 13:00:00', 156, 156, 0, 0, 80.00, 0.00, 0.00),
(3, 'U2101', 5, 1, '2024-04-15 15:00:00', '2024-04-15 17:00:00', 156, 156, 0, 0, 80.00, 0.00, 0.00),
(3, 'U2200', 1, 7, '2024-04-15 16:00:00', '2024-04-15 18:00:00', 156, 156, 0, 0, 70.00, 0.00, 0.00);

-- Inserimento alcune prenotazioni di esempio
INSERT INTO prenotazione (user_id, data_prenotazione, stato, prezzo_totale) VALUES
(4, '2024-04-01 10:00:00', 'confermata', 150.00),
(4, '2024-04-02 15:30:00', 'confermata', 50.00),
(5, '2024-04-03 09:15:00', 'confermata', 120.00);

-- Inserimento biglietti
INSERT INTO biglietto (booking_id, flight_id, classe, numero_posto, prezzo, bagaglio_extra, servizi_extra) VALUES
(1, 1, 'economy', '15A', 150.00, true, '{"pastorizzazione": true}'),
(2, 4, 'economy', '22B', 50.00, false, NULL),
(3, 3, 'economy', '10C', 120.00, true, '{"bagaglio_extra": true, "priority_boarding": true}'); 
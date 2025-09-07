# Progetto Basi di Dati - Sistema di Prenotazione Voli ✈️

Anno accademico 2024/2025

**Autori:**
- AWAMBO Lionel (882999)
- ONNA Mercy
- Gandini Gianmarco (898066)

## 📋 Descrizione del Progetto

Sistema di gestione e prenotazione voli sviluppato con Flask. Il progetto include:

- 🔐 Sistema di autenticazione utenti
- ✈️ Gestione compagnie aeree
- 🎫 Sistema di prenotazione e biglietteria
- 📊 API REST con JWT
- 🗄️ Database PostgreSQL/SQLite

## 🚀 Setup Veloce

### Prerequisiti
- Python 3.8 o superiore
- Git

### Installazione Automatica

1. **Clona il repository:**
   ```bash
   git clone https://github.com/leonel2377/bd_progetto.git
   cd bd_progetto
   ```

2. **Esegui lo script di setup:**
   ```bash
   python setup.py
   ```

3. **Attiva l'ambiente virtuale:**
   ```bash
   # Su Linux/Mac:
   source venv/bin/activate
   
   # Su Windows:
   .\\venv\\Scripts\\activate
   ```

4. **Avvia l'applicazione:**
   ```bash
   python run.py
   ```

5. **Apri il browser su:** `http://localhost:5000`

### Account di Test 🔑

- **Admin:** `admin@test.com` / `admin123`
- **Compagnia Aerea:** `airline@test.com` / `airline123`

## 🛠️ Setup Manuale

Se preferisci installare manualmente:

### 1. Ambiente Virtuale
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
.\\venv\\Scripts\\activate  # Windows
```

### 2. Dipendenze
```bash
pip install -r requirements.txt
```

### 3. Configurazione
```bash
cp .env.example .env
# Modifica .env con le tue configurazioni
```

### 4. Database

**Per SQLite (sviluppo):**
```bash
python init_sqlite_db.py
```

**Per PostgreSQL (produzione):**
```bash
# Prima crea il database PostgreSQL
createdb flight_booking

# Poi esegui:
python init_postgres_db.py
```

### 5. Avvio
```bash
python run.py
```

## 🏗️ Struttura del Progetto

```
bd_progetto/
├── app/                    # Applicazione Flask
│   ├── __init__.py        # Factory dell'app
│   ├── models.py          # Modelli database
│   ├── routes/            # Blueprint delle route
│   │   ├── main.py        # Route principali
│   │   ├── auth.py        # Autenticazione
│   │   ├── airline.py     # Gestione compagnie
│   │   ├── passenger.py   # Gestione passeggeri
│   │   └── api.py         # API REST
│   ├── templates/         # Template HTML
│   └── static/           # File statici (CSS, JS)
├── migrations/           # Migrazioni database
├── config.py            # Configurazioni
├── run.py              # Entry point applicazione
├── setup.py            # Script di setup
└── requirements.txt    # Dipendenze Python
```

## 🔧 Configurazione Database

### SQLite (Default - Sviluppo)
Il progetto usa SQLite di default per semplicità. Il database viene creato automaticamente.

### PostgreSQL (Produzione)
Per usare PostgreSQL, modifica il file `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/flight_booking
```

## 📚 API Endpoints

### Autenticazione
- `POST /api/login` - Login utente
- `POST /api/register` - Registrazione utente

### Voli
- `GET /api/flights` - Lista voli
- `GET /api/flights/search` - Ricerca voli
- `POST /api/flights` - Crea volo (solo compagnie)

### Prenotazioni
- `POST /api/bookings` - Crea prenotazione
- `GET /api/bookings` - Lista prenotazioni utente

## 🧪 Test

Esegui i test dell'applicazione:
```bash
python test_application.py
python test_api.py
```

## 📁 File di Utilità

- `populate_*.py` - Script per popolare il database
- `queries_principali.sql` - Query SQL di esempio
- `create_tables.sql` - Schema database
- `apply_*.py` - Script per modifiche database

## 🔍 Troubleshooting

### Errore "No module named 'app'"
Assicurati di essere nella directory del progetto e di aver attivato l'ambiente virtuale.

### Errore database
1. Verifica che il database sia inizializzato: `python init_sqlite_db.py`
2. Per PostgreSQL, verifica che il servizio sia avviato
3. Controlla le configurazioni in `.env`

### Errore dipendenze
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🤝 Contributi

Per contribuire al progetto:
1. Fork del repository
2. Crea un branch per la feature
3. Commit delle modifiche
4. Push al branch
5. Crea una Pull Request

## 📄 Licenza

Progetto sviluppato per il corso di Basi di Dati - Università degli Studi.

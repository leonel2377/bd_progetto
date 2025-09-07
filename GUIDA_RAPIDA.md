# 🚀 GUIDA RAPIDA - Come inizializzare e aprire il progetto

## Per chi vuole iniziare SUBITO:

### 1️⃣ Metodo Automatico (Raccomandato)
```bash
# Clona il repository
git clone https://github.com/leonel2377/bd_progetto.git
cd bd_progetto

# Esegui lo script di setup automatico
python setup.py

# Avvia l'applicazione
python run.py
```

### 2️⃣ Metodo con Script di Avvio
```bash
# Dopo aver eseguito il setup, usa lo script di avvio:

# Su Linux/Mac:
./start.sh

# Su Windows:
start.bat
```

## 🔍 Verifica che tutto funzioni:
```bash
python check_setup.py
```

## 🌐 Accesso all'applicazione:
- Apri il browser su: **http://localhost:5000**
- Account test: **admin@test.com** / **admin123**

---

## 📋 Cosa fa lo script di setup automaticamente:

1. ✅ Verifica versione Python (3.8+)
2. ✅ Crea ambiente virtuale (`venv/`)
3. ✅ Installa tutte le dipendenze
4. ✅ Configura le variabili d'ambiente
5. ✅ Inizializza il database SQLite
6. ✅ Popola il database con dati di test

## 🆘 Risoluzione problemi comuni:

### ❌ "python: command not found"
Installa Python 3.8+ dal sito ufficiale

### ❌ "No module named..."
```bash
pip install -r requirements.txt
```

### ❌ "Database error"
```bash
python init_sqlite_db.py
```

### ❌ L'app non si avvia
```bash
python check_setup.py  # per diagnosticare il problema
```

---

## 🎯 Cosa puoi fare nell'applicazione:

- **Admin**: Gestire utenti e visualizzare statistiche
- **Compagnia**: Aggiungere e gestire voli
- **Passeggero**: Cercare e prenotare voli
- **API**: Integrazioni esterne con JWT

## 📁 File importanti:

- `setup.py` - Script di inizializzazione automatica
- `check_setup.py` - Verifica configurazione
- `start.sh` / `start.bat` - Script di avvio
- `requirements.txt` - Dipendenze Python
- `.env.example` - Template configurazione
- `README.md` - Documentazione completa

---

*Per domande o problemi, consulta il README.md completo*
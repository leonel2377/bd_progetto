@echo off
REM Script di avvio per Windows

echo 🚀 Avvio Flight Booking System...

REM Verifica se l'ambiente virtuale esiste
if not exist "venv" (
    echo ❌ Ambiente virtuale non trovato. Esegui prima: python setup.py
    pause
    exit /b 1
)

REM Attiva l'ambiente virtuale
echo 🔄 Attivazione ambiente virtuale...
call venv\Scripts\activate.bat

REM Avvia l'applicazione
echo ✅ Avvio applicazione su http://localhost:5000
python run.py
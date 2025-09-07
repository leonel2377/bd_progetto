#!/bin/bash
# Script di avvio per Linux/Mac

echo "🚀 Avvio Flight Booking System..."

# Verifica se l'ambiente virtuale esiste
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtuale non trovato. Esegui prima: python setup.py"
    exit 1
fi

# Attiva l'ambiente virtuale
echo "🔄 Attivazione ambiente virtuale..."
source venv/bin/activate

# Avvia l'applicazione
echo "✅ Avvio applicazione su http://localhost:5000"
python run.py
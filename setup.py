#!/usr/bin/env python3
"""
Script di setup per il progetto Flight Booking
Questo script automatizza l'inizializzazione del progetto
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, check=True):
    """Esegue un comando shell e gestisce gli errori"""
    print(f"🔄 Eseguendo: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore nell'esecuzione del comando: {e}")
        if e.stderr:
            print(f"Errore: {e.stderr}")
        return None

def check_python_version():
    """Verifica che la versione di Python sia compatibile"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 o superiore è richiesto")
        return False
    print(f"✅ Python {sys.version.split()[0]} rilevato")
    return True

def create_virtual_environment():
    """Crea un ambiente virtuale se non esiste"""
    if not os.path.exists('venv'):
        print("🔄 Creazione ambiente virtuale...")
        if run_command("python -m venv venv"):
            print("✅ Ambiente virtuale creato")
        else:
            print("❌ Errore nella creazione dell'ambiente virtuale")
            return False
    else:
        print("✅ Ambiente virtuale già esistente")
    return True

def install_dependencies():
    """Installa le dipendenze del progetto"""
    print("🔄 Installazione dipendenze...")
    
    # Determina il comando di attivazione in base al sistema operativo
    if os.name == 'nt':  # Windows
        activate_cmd = ".\\venv\\Scripts\\activate && "
    else:  # Unix/Linux/Mac
        activate_cmd = "source venv/bin/activate && "
    
    cmd = f"{activate_cmd}pip install -r requirements.txt"
    if run_command(cmd):
        print("✅ Dipendenze installate con successo")
        return True
    else:
        print("❌ Errore nell'installazione delle dipendenze")
        return False

def setup_environment():
    """Configura le variabili d'ambiente"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ File .env creato da .env.example")
            print("📝 Modifica il file .env con le tue configurazioni se necessario")
        else:
            # Crea un .env di base
            with open('.env', 'w') as f:
                f.write("FLASK_ENV=development\nFLASK_DEBUG=true\n")
            print("✅ File .env creato con configurazioni di base")
    else:
        print("✅ File .env già esistente")

def initialize_database():
    """Inizializza il database"""
    print("🔄 Inizializzazione database...")
    
    # Determina il comando di attivazione
    if os.name == 'nt':  # Windows
        activate_cmd = ".\\venv\\Scripts\\activate && "
    else:  # Unix/Linux/Mac
        activate_cmd = "source venv/bin/activate && "
    
    # Usa SQLite per semplicità di setup
    cmd = f"{activate_cmd}python init_sqlite_db.py"
    if run_command(cmd):
        print("✅ Database inizializzato con successo")
        return True
    else:
        print("❌ Errore nell'inizializzazione del database")
        return False

def main():
    """Funzione principale dello script di setup"""
    print("🚀 Setup del progetto Flight Booking")
    print("=" * 50)
    
    # Verifica versione Python
    if not check_python_version():
        return False
    
    # Crea ambiente virtuale
    if not create_virtual_environment():
        return False
    
    # Installa dipendenze
    if not install_dependencies():
        return False
    
    # Setup environment
    setup_environment()
    
    # Inizializza database
    if not initialize_database():
        return False
    
    print("\n🎉 Setup completato con successo!")
    print("\n📝 Prossimi passi:")
    print("1. Attiva l'ambiente virtuale:")
    if os.name == 'nt':
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Avvia l'applicazione:")
    print("   python run.py")
    print("3. Apri il browser su: http://localhost:5000")
    print("\n🔑 Account di test:")
    print("   - Admin: admin@test.com / admin123")
    print("   - Compagnia: airline@test.com / airline123")
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        print("\n❌ Setup fallito. Controlla gli errori sopra.")
        sys.exit(1)
#!/usr/bin/env python3
"""
Script per verificare che l'applicazione sia configurata correttamente
"""

import sys
import os
import importlib.util

def check_imports():
    """Verifica che tutti i moduli necessari siano installati"""
    required_modules = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_migrate',
        'flask_jwt_extended',
        'dotenv',
        'werkzeug',
        'marshmallow'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module}")
    
    return len(missing_modules) == 0

def check_database():
    """Verifica che il database sia accessibile"""
    try:
        from app import create_app, db
        from app.models import Utente
        
        app = create_app()
        with app.app_context():
            # Prova a fare una query semplice
            utenti_count = Utente.query.count()
            print(f"✅ Database collegato - {utenti_count} utenti trovati")
            return True
    except Exception as e:
        print(f"❌ Errore database: {e}")
        return False

def check_config():
    """Verifica la configurazione"""
    try:
        from config import DevelopmentConfig
        config = DevelopmentConfig()
        print(f"✅ Configurazione caricata")
        print(f"   - Database URI: {config.SQLALCHEMY_DATABASE_URI[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Errore configurazione: {e}")
        return False

def main():
    """Funzione principale per la verifica"""
    print("🔍 Verifica configurazione progetto Flight Booking")
    print("=" * 50)
    
    print("\n📦 Verifica moduli Python:")
    imports_ok = check_imports()
    
    print("\n⚙️ Verifica configurazione:")
    config_ok = check_config()
    
    print("\n🗄️ Verifica database:")
    db_ok = check_database()
    
    print("\n" + "=" * 50)
    
    if imports_ok and config_ok and db_ok:
        print("🎉 Tutto configurato correttamente!")
        print("\n🚀 Puoi avviare l'applicazione con:")
        print("   python run.py")
        return True
    else:
        print("❌ Ci sono alcuni problemi da risolvere:")
        if not imports_ok:
            print("   - Installa le dipendenze: pip install -r requirements.txt")
        if not config_ok:
            print("   - Verifica il file config.py")
        if not db_ok:
            print("   - Inizializza il database: python init_sqlite_db.py")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
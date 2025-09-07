import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def create_database():
    try:
        # Connessione al server PostgreSQL
        conn = psycopg2.connect(
            user="postgres",
            password="7999",  # Mot de passe configuré
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Creazione del cursore
        cur = conn.cursor()
        
        # Verifica se il database esiste
        cur.execute("SELECT 1 FROM pg_database WHERE datname='flight_booking'")
        exists = cur.fetchone()
        
        if not exists:
            # Creazione del database
            cur.execute('CREATE DATABASE flight_booking')
            print("✅ Database 'flight_booking' creato con successo!")
        else:
            print("ℹ️ Il database 'flight_booking' esiste già.")
        
        # Chiusura della connessione
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Errore durante la creazione del database: {e}")
        print("💡 Assicurati che PostgreSQL sia in esecuzione e che il password sia corretto.")

if __name__ == "__main__":
    create_database() 
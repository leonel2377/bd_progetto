from app import db
from sqlalchemy import text

def apply_triggers():
    """Applica i trigger al database."""
    try:
        # Leggi il file SQL
        with open('app/database/triggers.sql', 'r') as file:
            sql_commands = file.read()
        
        # Esegui i comandi SQL
        with db.engine.connect() as connection:
            connection.execute(text(sql_commands))
            connection.commit()
        
        print("Trigger applicati con successo!")
        
    except Exception as e:
        print(f"Errore durante l'applicazione dei trigger: {str(e)}")
        raise

if __name__ == '__main__':
    apply_triggers() 
from app import db

def apply_alter_compagnia():
    try:
        # Esegui le query SQL per modificare la tabella
        db.session.execute('ALTER TABLE compagnia_aerea ALTER COLUMN codice_iata DROP NOT NULL')
        db.session.execute('ALTER TABLE compagnia_aerea ALTER COLUMN sede_legale DROP NOT NULL')
        db.session.commit()
        print("Modifica alla tabella compagnia_aerea applicata con successo!")
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante l'applicazione della modifica: {str(e)}")

if __name__ == '__main__':
    apply_alter_compagnia() 
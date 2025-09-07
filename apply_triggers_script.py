from app import create_app, db
from app.database.apply_triggers import apply_triggers

def main():
    app = create_app()
    with app.app_context():
        try:
            apply_triggers()
            print("Trigger applicati con successo!")
        except Exception as e:
            print(f"Errore durante l'applicazione dei trigger: {str(e)}")

if __name__ == '__main__':
    main() 
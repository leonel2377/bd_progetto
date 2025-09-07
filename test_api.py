import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000/api/v1'

def test_api():
    # Test registrazione
    print("\n1. Test Registrazione")
    register_data = {
        "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "password": "password123",
        "nome": "Test",
        "cognome": "User",
        "is_airline": False
    }
    
    response = requests.post(f'{BASE_URL}/auth/register', json=register_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code != 201:
        print("Registrazione fallita!")
        return
    
    # Test login
    print("\n2. Test Login")
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code != 200:
        print("Login fallito!")
        return
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test ricerca voli
    print("\n3. Test Ricerca Voli")
    search_data = {
        "aeroporto_partenza": "FCO",
        "aeroporto_arrivo": "MXP",
        "data": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        "passeggeri": 2,
        "classe": "economy",
        "ordina_per": "prezzo"
    }
    
    response = requests.post(f'{BASE_URL}/flights/search', 
                           json=search_data, 
                           headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 200:
        print("Ricerca voli fallita!")
        return
    
    # Se ci sono voli disponibili, testa la prenotazione
    if response.json()['voli_diretti']:
        volo_id = response.json()['voli_diretti'][0]['id']
        
        print("\n4. Test Creazione Prenotazione")
        booking_data = {
            "volo_id": volo_id,
            "classe": "economy",
            "passeggeri": 2,
            "bagaglio_extra": True
        }
        
        response = requests.post(f'{BASE_URL}/bookings', 
                               json=booking_data, 
                               headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("\n5. Test Visualizzazione Prenotazioni")
            response = requests.get(f'{BASE_URL}/bookings', headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\nTest completati!")

if __name__ == '__main__':
    test_api() 
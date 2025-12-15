import requests
import json
import time

BASE_URL = 'http://localhost:8000/api'

# Test 1: Verificar estado actual
print("=== Test 1: Estado de rotación ===")
response = requests.get(f'{BASE_URL}/scraping/ticker/rotation/status')
print(f"Status code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
print()

# Test 2: Iniciar rotación
print("=== Test 2: Iniciar rotación (30 segundos) ===")
payload = {
    "interval_seconds": 30,
    "separator_url": "https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg",
    "show_source_name": True
}
payload = {
    "interval_seconds": 30,
    "separator_url": "https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg",
    "show_source_name": True
}
response = requests.post(f'{BASE_URL}/scraping/ticker/rotation/start', json=payload)
print(f"Status code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
print()

# Test 3: Verificar estado después de iniciar
time.sleep(2)
print("=== Test 3: Estado después de iniciar ===")
response = requests.get(f'{BASE_URL}/scraping/ticker/rotation/status')
print(f"Response: {json.dumps(response.json(), indent=2)}")
print()

print("Rotación iniciada. Esperando 35 segundos para ver si rota...")
time.sleep(35)

# Test 4: Verificar que sigue corriendo
print("=== Test 4: Estado después de 35 segundos ===")
response = requests.get(f'{BASE_URL}/scraping/ticker/rotation/status')
print(f"Response: {json.dumps(response.json(), indent=2)}")
print()

# Test 5: Detener rotación
print("=== Test 5: Detener rotación ===")
response = requests.post(f'{BASE_URL}/scraping/ticker/rotation/stop')
print(f"Status code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

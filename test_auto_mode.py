"""
Script de prueba para el nuevo sistema Manual vs Automático

Prueba los 3 nuevos endpoints:
- POST /ticker/auto/start
- POST /ticker/auto/stop
- GET /ticker/auto/status
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000/api/scraping"

def test_auto_mode():
    print("=" * 60)
    print("TEST: Sistema Modo Manual vs Automático")
    print("=" * 60 + "\n")
    
    # 1. Verificar estado inicial
    print("1️⃣  Verificando estado inicial...")
    response = requests.get(f"{BASE_URL}/ticker/auto/status")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 2. Iniciar modo automático
    print("2️⃣  Iniciando modo automático...")
    payload = {
        "rotation_interval": 60,
        "scraping_interval": 10,
        "separator_url": "https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg",
        "show_source_name": True
    }
    response = requests.post(f"{BASE_URL}/ticker/auto/start", json=payload)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 3. Esperar y verificar estado
    print("3️⃣  Esperando 5 segundos y verificando estado...")
    time.sleep(5)
    response = requests.get(f"{BASE_URL}/ticker/auto/status")
    print(f"   Status: {response.status_code}")
    status = response.json()
    print(f"   Modo activo: {status.get('auto_mode_active')}")
    print(f"   Scheduler corriendo: {status.get('scheduler_running')}")
    print(f"   Rotación corriendo: {status.get('rotation_running')}")
    print(f"   Categoría actual: {status.get('current_category')}\n")
    
    # 4. Detener modo automático
    print("4️⃣  Deteniendo modo automático...")
    response = requests.post(f"{BASE_URL}/ticker/auto/stop")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 5. Verificar estado final
    print("5️⃣  Verificando estado final...")
    response = requests.get(f"{BASE_URL}/ticker/auto/status")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}\n")
    
    print("=" * 60)
    print("✅ TEST COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_auto_mode()
    except Exception as e:
        print(f"❌ ERROR: {e}")

"""Ejecutable de testing minimalista"""
import sys
print("="*60)
print("TEST 1: Print funciona")
print("="*60)

try:
    print("\nTEST 2: Importando platform...")
    import platform
    print(f"✓ Platform: {platform.system()}")
    
    print("\nTEST 3: Importando webview...")
    import webview
    print("✓ Webview importado")
    
    print("\nTEST 4: Importando uvicorn...")
    import uvicorn
    print("✓ Uvicorn importado")
    
    print("\nTEST 5: Importando pystray...")
    import pystray
    print("✓ Pystray importado")
    
    print("\nTEST 6: Importando PIL...")
    from PIL import Image
    print("✓ PIL importado")
    
    print("\n" + "="*60)
    print("TODOS LOS TESTS PASARON")
    print("="*60)
    
except Exception as e:
    import traceback
    print("\n" + "="*60)
    print(f"ERROR EN IMPORTS: {e}")
    print("="*60)
    traceback.print_exc()

input("\nPresiona Enter para cerrar...")

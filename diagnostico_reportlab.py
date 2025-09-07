#!/usr/bin/env python3
"""
Diagnóstico para verificar la instalación de ReportLab
"""

import sys
import subprocess

print("=== DIAGNÓSTICO DE REPORTLAB ===\n")

# Información del sistema
print(f"Python versión: {sys.version}")
print(f"Python ejecutable: {sys.executable}")
print(f"Ruta de Python: {sys.path[0]}")
print()

# Verificar si ReportLab está instalado
try:
    import reportlab
    print("✅ ReportLab está instalado")
    print(f"   Versión: {reportlab.__version__}")
    print(f"   Ubicación: {reportlab.__file__}")
except ImportError as e:
    print("❌ ReportLab NO está instalado")
    print(f"   Error: {e}")

print()

# Verificar pip
try:
    import pip
    print("✅ pip está disponible")
except ImportError:
    print("❌ pip NO está disponible")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ pip está disponible vía 'python -m pip'")
            print(f"   {result.stdout.strip()}")
        else:
            print("❌ pip NO está disponible vía 'python -m pip'")
    except Exception as e:
        print(f"❌ Error al verificar pip: {e}")

print()

# Listar paquetes instalados relacionados
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        report_packages = [line for line in lines if 'report' in line.lower()]
        if report_packages:
            print("📦 Paquetes relacionados con 'report' encontrados:")
            for pkg in report_packages:
                print(f"   {pkg}")
        else:
            print("❌ No se encontraron paquetes relacionados con 'report'")
    else:
        print("❌ No se pudo listar los paquetes instalados")
except Exception as e:
    print(f"❌ Error al listar paquetes: {e}")

print()
print("=== COMANDOS SUGERIDOS ===")
print("Para instalar ReportLab, pruebe uno de estos comandos:")
print("1. pip install reportlab")
print("2. pip3 install reportlab") 
print("3. python -m pip install reportlab")
print("4. python3 -m pip install reportlab")
print()
print("Si está usando un entorno virtual, active primero:")
print("   Linux/Mac: source venv/bin/activate")
print("   Windows:   venv\\Scripts\\activate")
print()
print("Después de instalar, reinicie la aplicación Streamlit.")
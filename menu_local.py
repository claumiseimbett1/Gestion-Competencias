#!/usr/bin/env python3
"""
Sistema TEN - Gestión de Competencias de Natación
Menú de acceso local para todas las funcionalidades
"""

import os
import sys
from datetime import datetime

def mostrar_logo():
    """Muestra el logo ASCII del sistema"""
    print("\n" + "="*60)
    print("    🏊‍♀️ SISTEMA TEN - GESTIÓN DE COMPETENCIAS 🏊‍♂️")
    print("          Tecnología En Natación")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*60)

def mostrar_menu_principal():
    """Muestra el menú principal de opciones"""
    print("\n📋 MENÚ PRINCIPAL")
    print("-" * 30)
    print("1. ✍️  Inscripción de Nadadores")
    print("2. 📊 Sembrado de Competencia")
    print("3. 🏆 Procesar Resultados")
    print("4. 📁 Gestión de Archivos")
    print("5. 🌐 Iniciar Aplicación Web")
    print("0. 🚪 Salir")
    print("-" * 30)

def mostrar_menu_sembrado():
    """Muestra el menú de opciones de sembrado"""
    print("\n📊 SEMBRADO DE COMPETENCIA")
    print("-" * 30)
    print("1. 📊 Sembrado por Categorías")
    print("2. ⏱️  Sembrado por Tiempo")
    print("0. ⬅️  Volver al menú principal")
    print("-" * 30)

def verificar_archivo(archivo, descripcion):
    """Verifica si un archivo existe"""
    if os.path.exists(archivo):
        print(f"✅ {descripcion}: {archivo}")
        return True
    else:
        print(f"❌ {descripcion}: {archivo} (NO ENCONTRADO)")
        return False

def mostrar_estado_archivos():
    """Muestra el estado de todos los archivos del sistema"""
    print("\n📁 ESTADO DE ARCHIVOS")
    print("-" * 40)
    
    archivos = {
        "planilla_inscripcion.xlsx": "Planilla de Inscripción",
        "BASE-DE-DATOS.xlsx": "Base de Datos de Atletas",
        "sembrado_competencia.xlsx": "Sembrado por Categorías",
        "sembrado_competencia_POR_TIEMPO.xlsx": "Sembrado por Tiempo",
        "resultados_con_tiempos.xlsx": "Resultados de Competencia",
        "reporte_premiacion_final_CORREGIDO.xlsx": "Reporte de Premiación"
    }
    
    for archivo, descripcion in archivos.items():
        verificar_archivo(archivo, descripcion)

def ejecutar_inscripcion():
    """Ejecuta el sistema de inscripción"""
    print("\n✍️ SISTEMA DE INSCRIPCIÓN DE NADADORES")
    print("=" * 45)
    
    try:
        # Importar y ejecutar el sistema de inscripción
        from importlib import util
        
        spec = util.spec_from_file_location("inscripcion", "1-inscripcion_nadadores.py")
        inscripcion_module = util.module_from_spec(spec)
        spec.loader.exec_module(inscripcion_module)
        
        # Crear instancia del sistema
        sistema = inscripcion_module.SwimmerRegistration()
        
        print("🔍 Sistema de inscripción iniciado.")
        print("📝 Este es un sistema completo con múltiples funcionalidades:")
        print("   • Inscripción manual de nadadores")
        print("   • Búsqueda en base de datos")
        print("   • Importación masiva desde Excel")
        print("   • Generación de reportes PDF")
        print("\n💡 Para acceso completo, usa la aplicación web con:")
        print("   python menu_local.py -> Opción 5")
        
    except Exception as e:
        print(f"❌ Error al cargar sistema de inscripción: {e}")

def ejecutar_sembrado_categoria():
    """Ejecuta el sembrado por categorías"""
    print("\n📊 GENERANDO SEMBRADO POR CATEGORÍAS...")
    
    if not verificar_archivo("planilla_inscripcion.xlsx", "Archivo de inscripciones"):
        print("⚠️  Necesitas el archivo de inscripciones para generar el sembrado.")
        return
    
    try:
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("sembrado", "2-generar_sembrado.py")
        sembrado_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sembrado_module)
        
        sembrado_module.main_full()
        
        if verificar_archivo("sembrado_competencia.xlsx", "Sembrado generado"):
            print("✅ ¡Sembrado por categorías generado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al generar sembrado: {e}")

def ejecutar_sembrado_tiempo():
    """Ejecuta el sembrado por tiempo"""
    print("\n⏱️ GENERANDO SEMBRADO POR TIEMPO...")
    
    if not verificar_archivo("planilla_inscripcion.xlsx", "Archivo de inscripciones"):
        print("⚠️  Necesitas el archivo de inscripciones para generar el sembrado.")
        return
    
    try:
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("sembrado_tiempo", "3-generar_sembrado_por_tiempo.py")
        sembrado_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sembrado_module)
        
        sembrado_module.main()
        
        if verificar_archivo("sembrado_competencia_POR_TIEMPO.xlsx", "Sembrado generado"):
            print("✅ ¡Sembrado por tiempo generado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al generar sembrado: {e}")

def ejecutar_procesamiento_resultados():
    """Ejecuta el procesamiento de resultados"""
    print("\n🏆 PROCESANDO RESULTADOS...")
    
    if not verificar_archivo("resultados_con_tiempos.xlsx", "Archivo de resultados"):
        print("⚠️  Necesitas el archivo de resultados para procesar.")
        return
    
    try:
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("procesar", "4-procesar_resultados.py")
        procesar_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(procesar_module)
        
        procesar_module.main_full()
        
        if verificar_archivo("reporte_premiacion_final_CORREGIDO.xlsx", "Reporte generado"):
            print("✅ ¡Resultados procesados exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al procesar resultados: {e}")

def iniciar_app_web():
    """Inicia la aplicación web Streamlit"""
    print("\n🌐 INICIANDO APLICACIÓN WEB...")
    print("🚀 La aplicación se abrirá en tu navegador")
    print("📡 URL local: http://localhost:8501")
    print("\n⏹️  Para detener: Presiona Ctrl+C en la terminal")
    
    try:
        import streamlit.web.cli as stcli
        import sys
        
        # Configurar argumentos para Streamlit
        sys.argv = ["streamlit", "run", "app.py"]
        stcli.main()
        
    except Exception as e:
        print(f"❌ Error al iniciar aplicación web: {e}")
        print("💡 Intenta ejecutar manualmente: streamlit run app.py")

def main():
    """Función principal del menú"""
    while True:
        mostrar_logo()
        mostrar_menu_principal()
        
        try:
            opcion = input("\n🔸 Selecciona una opción: ").strip()
            
            if opcion == "0":
                print("\n👋 ¡Gracias por usar el Sistema TEN!")
                print("🏊‍♀️ ¡Que tengas una excelente competencia!")
                break
                
            elif opcion == "1":
                ejecutar_inscripcion()
                
            elif opcion == "2":
                while True:
                    mostrar_menu_sembrado()
                    sub_opcion = input("\n🔸 Selecciona una opción: ").strip()
                    
                    if sub_opcion == "0":
                        break
                    elif sub_opcion == "1":
                        ejecutar_sembrado_categoria()
                    elif sub_opcion == "2":
                        ejecutar_sembrado_tiempo()
                    else:
                        print("❌ Opción inválida. Intenta de nuevo.")
                    
                    input("\n📋 Presiona Enter para continuar...")
                    
            elif opcion == "3":
                ejecutar_procesamiento_resultados()
                
            elif opcion == "4":
                mostrar_estado_archivos()
                
            elif opcion == "5":
                iniciar_app_web()
                
            else:
                print("❌ Opción inválida. Intenta de nuevo.")
            
            if opcion != "2":  # No pausar si estamos en el submenú de sembrado
                input("\n📋 Presiona Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Adiós!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            input("\n📋 Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
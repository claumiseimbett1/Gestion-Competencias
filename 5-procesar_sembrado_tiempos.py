#!/usr/bin/env python3
"""
Procesador de Sembrado con Tiempos de Competencia
Convierte archivos de sembrado con tiempos agregados en formato de resultados
"""

import pandas as pd
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

def process_seeding_with_times(input_file):
    """
    Procesa un archivo de sembrado que contiene tiempos de competencia
    y genera un archivo de resultados estructurado
    """
    if not os.path.exists(input_file):
        return False, f"Archivo no encontrado: {input_file}"
    
    try:
        # Leer archivo Excel
        df = pd.read_excel(input_file)
        
        # Verificar que tenga la columna de tiempo de competencia
        if 'Tiempo Competencia' not in df.columns:
            return False, "El archivo no contiene la columna 'Tiempo Competencia'"
        
        # Filtrar solo filas con tiempos de competencia
        df_with_times = df[pd.notna(df['Tiempo Competencia']) & (df['Tiempo Competencia'] != "")]
        
        if len(df_with_times) == 0:
            return False, "No se encontraron tiempos de competencia en el archivo"
        
        # Crear archivo de resultados
        output_file = f"resultados_desde_sembrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Resultados de Competencia"
        
        # Headers
        headers = ["Evento", "Nombre", "Equipo", "Edad", "Categoría", "Tiempo", "Serie", "Carril"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
        
        row = 2
        current_event = None
        current_series = None
        
        # Procesar cada fila
        for index, data_row in df_with_times.iterrows():
            # Detectar cambios de evento (esto puede necesitar ajuste según la estructura)
            # Por ahora asumimos que está en una columna o se puede inferir
            
            ws.cell(row=row, column=1, value=current_event or "Evento")  # Necesitarás ajustar esto
            ws.cell(row=row, column=2, value=data_row.get('Nombre', ''))
            ws.cell(row=row, column=3, value=data_row.get('Equipo', ''))
            ws.cell(row=row, column=4, value=data_row.get('Edad', ''))
            ws.cell(row=row, column=5, value=data_row.get('Categoría', ''))
            ws.cell(row=row, column=6, value=data_row.get('Tiempo Competencia', ''))
            ws.cell(row=row, column=7, value=current_series or 1)  # Necesitarás ajustar esto
            ws.cell(row=row, column=8, value=data_row.get('Carril', ''))
            
            row += 1
        
        # Ajustar ancho de columnas
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        wb.save(output_file)
        
        return True, f"Archivo de resultados generado: {output_file}"
        
    except Exception as e:
        return False, f"Error al procesar archivo: {str(e)}"

def main():
    """Función principal para uso desde línea de comandos"""
    print("=== PROCESADOR DE SEMBRADO CON TIEMPOS ===")
    
    # Buscar archivos de sembrado
    seeding_files = []
    if os.path.exists("sembrado_competencia.xlsx"):
        seeding_files.append("sembrado_competencia.xlsx")
    if os.path.exists("sembrado_competencia_POR_TIEMPO.xlsx"):
        seeding_files.append("sembrado_competencia_POR_TIEMPO.xlsx")
    
    if not seeding_files:
        print("❌ No se encontraron archivos de sembrado")
        print("💡 Primero genera un sembrado y agrega los tiempos de competencia")
        return
    
    print("\n📁 Archivos de sembrado encontrados:")
    for i, file in enumerate(seeding_files, 1):
        print(f"   {i}. {file}")
    
    try:
        choice = input(f"\n🔸 Selecciona archivo (1-{len(seeding_files)}): ")
        selected_file = seeding_files[int(choice) - 1]
        
        print(f"\n🔄 Procesando {selected_file}...")
        success, message = process_seeding_with_times(selected_file)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            
    except (ValueError, IndexError):
        print("❌ Selección inválida")
    except KeyboardInterrupt:
        print("\n👋 Operación cancelada")

if __name__ == "__main__":
    main()
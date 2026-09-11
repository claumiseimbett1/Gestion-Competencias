# generar_papeletas_excel.py
import pandas as pd
import os
from io import BytesIO
from pathlib import Path
from planilla_utils import inscrito_en_prueba, ordered_prueba_hoja_keys, titulo_prueba_numerada
import math
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# --- CONFIGURACIÓN ---
SCRIPT_DIR = Path(__file__).resolve().parent
ARCHIVO_PAPELETAS_EXCEL = str(SCRIPT_DIR / 'papeletas_jueces.xlsx')

def parse_time(time_val):
    """Convierte tiempo a segundos para ordenamiento"""
    if pd.isna(time_val): return float('inf')
    if hasattr(time_val, 'minute'): return time_val.minute * 60 + time_val.second + time_val.microsecond / 1_000_000
    time_str = str(time_val).replace(',', '.')
    try:
        parts = time_str.split(':')
        if len(parts) == 2: return int(parts[0]) * 60 + float(parts[1])
        return float(time_str)
    except (ValueError, IndexError): return float('inf')

def leer_datos_sembrado(session_state=None):
    """Lee series y carriles del sembrado manual guardado (no regenera sembrado)."""
    from planilla_utils import get_papeletas_from_manual_sembrado

    papeletas, skipped, error = get_papeletas_from_manual_sembrado(session_state=session_state)
    if error:
        print(f"Papeletas: {error}")
        return []
    if skipped:
        print(f"Papeletas: omitidos {skipped} nadador(es) no inscritos en planilla")
    return papeletas


def generar_papeletas_excel(session_state=None):
    """Genera papeletas con datos del sembrado manual, 3 por hoja."""
    papeletas_sembrado = leer_datos_sembrado(session_state=session_state)

    if not papeletas_sembrado:
        return False, "No se pudieron leer los datos del sembrado manual. Graba el sembrado en Sembrado → Manual primero.", None

    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Papeletas Jueces"
        
        # Configurar anchos de columna para dar espacio
        for col in range(1, 9):  # A hasta H
            ws.column_dimensions[get_column_letter(col)].width = 15
        
        # 3 papeletas por hoja
        fila_actual = 1
        
        # Estilos
        titulo_font = Font(bold=True, size=12, color='1E88E5')
        info_font = Font(size=9)
        serie_font = Font(bold=True, size=10)
        tiempo_font = Font(bold=True, size=14, color='FF0000')
        
        border_thin = Border(
            left=Side(style='thin'),
            right=Side(style='thin'), 
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        border_thick = Border(
            left=Side(style='thick'),
            right=Side(style='thick'),
            top=Side(style='thick'), 
            bottom=Side(style='thick')
        )
        
        # Configurar anchos de columna para mejor distribución (3 papeletas por fila)
        for col in range(1, 10):  # A hasta I (3 papeletas × 3 columnas cada una)
            ws.column_dimensions[get_column_letter(col)].width = 11
        
        # Agregar título del documento
        ws.merge_cells('A1:I1')
        title_cell = ws.cell(row=1, column=1, value="PAPELETAS DE JUECES - COMPETENCIA DE NATACIÓN TEN")
        title_cell.font = Font(bold=True, size=14, color='1E88E5')
        title_cell.alignment = Alignment(horizontal='center')
        
        fila_actual = 3  # Empezar después del título
        contador_papeletas = 0
        
        for papeleta in papeletas_sembrado:
            # Calcular posición (3 papeletas por fila)
            pos_en_fila = contador_papeletas % 3  # 0, 1, 2
            if pos_en_fila == 0 and contador_papeletas > 0:
                fila_actual += 8  # Espacio entre filas de papeletas (reducido)
            
            col_inicio = pos_en_fila * 3 + 1  # 1, 4, 7
            
            fila_base = fila_actual
            
            # PRIMERA FILA: Prueba
            ws.merge_cells(start_row=fila_base, start_column=col_inicio, 
                         end_row=fila_base, end_column=col_inicio + 2)
            cell = ws.cell(row=fila_base, column=col_inicio, value=papeleta['prueba'])
            cell.font = titulo_font
            cell.alignment = Alignment(horizontal='center', wrap_text=True)
            cell.border = border_thick
            
            # SEGUNDA FILA: Nadador, Equipo, Categoría  
            fila_base += 1
            ws.merge_cells(start_row=fila_base, start_column=col_inicio,
                         end_row=fila_base, end_column=col_inicio + 2)
            cell = ws.cell(row=fila_base, column=col_inicio,
                         value=f"{papeleta['nombre']}\n{papeleta['equipo']} - {papeleta['categoria']}")
            cell.font = info_font
            cell.alignment = Alignment(horizontal='center', wrap_text=True)
            cell.border = border_thin
            ws.row_dimensions[fila_base].height = 30
            
            # TERCERA FILA: Serie y Carril YA ASIGNADOS
            fila_base += 1
            ws.merge_cells(start_row=fila_base, start_column=col_inicio,
                         end_row=fila_base, end_column=col_inicio + 2)
            cell = ws.cell(row=fila_base, column=col_inicio, 
                         value=f"SERIE: {papeleta['serie']}  |  CARRIL: {papeleta['carril']}")
            cell.font = serie_font
            cell.alignment = Alignment(horizontal='center')
            cell.border = border_thin
            
            # CUARTA FILA: TIEMPO DE COMPETENCIA (título)
            fila_base += 1
            ws.merge_cells(start_row=fila_base, start_column=col_inicio,
                         end_row=fila_base, end_column=col_inicio + 2)
            cell = ws.cell(row=fila_base, column=col_inicio, value="TIEMPO DE COMPETENCIA:")
            cell.font = tiempo_font
            cell.alignment = Alignment(horizontal='center')
            cell.border = border_thin
            
            # QUINTA FILA: Línea para anotación (EN BLANCO) - más compacta
            fila_base += 1
            ws.merge_cells(start_row=fila_base, start_column=col_inicio,
                         end_row=fila_base, end_column=col_inicio + 2)
            cell = ws.cell(row=fila_base, column=col_inicio, value="_____ : _____ . _____")
            cell.font = Font(bold=True, size=14)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border_thick
            
            # SEXTA FILA: Juez (más compacta)
            fila_base += 1
            ws.merge_cells(start_row=fila_base, start_column=col_inicio,
                         end_row=fila_base, end_column=col_inicio + 2)
            cell = ws.cell(row=fila_base, column=col_inicio, value="Juez: ___________________")
            cell.font = Font(size=8, color='666666')
            cell.alignment = Alignment(horizontal='center')
            cell.border = border_thin
            
            # Ajustar altura de las filas
            ws.row_dimensions[fila_base - 1].height = 25  # Fila de tiempo
            ws.row_dimensions[fila_base].height = 15      # Fila de juez
            
            contador_papeletas += 1
        
        # Configurar márgenes de página para impresión optimizada
        ws.page_margins.left = 0.3
        ws.page_margins.right = 0.3
        ws.page_margins.top = 0.4 
        ws.page_margins.bottom = 0.3
        ws.page_margins.header = 0.2
        ws.page_margins.footer = 0.2
        
        # Configurar orientación horizontal para mejor aprovechamiento
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        
        # Configurar escala de impresión para que quepa todo
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0  # Sin límite de altura
        
        # Configurar repetir filas en la parte superior (título)
        ws.print_title_rows = '1:2'
        
        # Configurar líneas de cuadrícula para impresión
        ws.print_options.gridLines = True
        ws.print_options.gridLinesSet = True
        
        buffer = BytesIO()
        wb.save(buffer)
        xlsx_bytes = buffer.getvalue()
        Path(ARCHIVO_PAPELETAS_EXCEL).write_bytes(xlsx_bytes)
        msg = (
            f"Papeletas Excel generadas: {len(papeletas_sembrado)} papeletas "
            f"desde sembrado manual"
        )
        return True, msg, xlsx_bytes
        
    except Exception as e:
        return False, f"Error al generar papeletas Excel: {e}", None

def main():
    """Función principal para ejecutar desde línea de comandos"""
    print("Generando papeletas Excel para jueces...")
    
    if not os.path.exists('planilla_inscripcion.xlsx'):
        print("ERROR: No se encontro el archivo 'planilla_inscripcion.xlsx'")
        print("Este archivo es necesario para generar las papeletas.")
        return
    
    success, message, _xlsx_bytes = generar_papeletas_excel()
    print(message)
    
    if success:
        total_papeletas = len(leer_datos_sembrado())
        print(f"Total de papeletas generadas: {total_papeletas}")
        print(f"Archivo guardado como: {ARCHIVO_PAPELETAS_EXCEL}")
        print(f"Formato: 3 papeletas por hoja, con serie y carril asignados")

if __name__ == "__main__":
    main()
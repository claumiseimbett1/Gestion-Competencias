# procesar_resultados.py (Versión Final Corregida)

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font

# --- CONFIGURACIÓN ---
ARCHIVO_ENTRADA_RESULTADOS = 'resultados_con_tiempos.xlsx'
ARCHIVO_SALIDA_PREMIACION = 'reporte_premiacion_final_CORREGIDO.xlsx'
PUNTOS = {1: 9, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}

# (Las funciones de ayuda como parse_time, format_time_value y apply_styles_and_width no cambian)
# ... [copiarlas de la respuesta anterior] ...

def procesar_resultados_excel_corregido(filepath):
    """Lee el archivo de resultados que ahora incluye la columna 'Categoría'."""
    try:
        df_raw = pd.read_excel(filepath, header=None)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{filepath}'.")
        return None
    
    all_results = []
    current_prueba = ""

    for index, row in df_raw.iterrows():
        # Detectar el nombre de la prueba
        if " - " in str(row[0]) and pd.isna(row[1]):
            current_prueba = row[0]
            continue
        
        # Detectar la cabecera de la tabla de resultados
        if str(row[0]).strip() == "Carril":
            # Empezar a leer los nadadores de esta tabla
            for i in range(index + 1, len(df_raw)):
                nadador_row = df_raw.iloc[i]
                # Parar si la fila está vacía o es una nueva cabecera de serie/categoría
                if pd.isna(nadador_row[0]) or "Serie" in str(nadador_row[0]) or "Categoría" in str(nadador_row[0]):
                    break
                
                # <-- ¡CORRECCIÓN CLAVE! Leemos los datos por posición de columna
                # Col A(0): Carril, B(1): Nombre, C(2): Equipo, D(3): Edad, E(4): Categoría, G(6): Tiempo Final
                if pd.notna(nadador_row[1]): # Si hay un nombre
                    all_results.append({
                        "Prueba": current_prueba,
                        "Nombre": nadador_row[1],
                        "Equipo": nadador_row[2],
                        "Edad": nadador_row[3],
                        "Categoria": nadador_row[4], # <-- Leemos la categoría de su propia columna
                        "Tiempo Final": nadador_row[6] if len(nadador_row) > 6 else None
                    })
    return pd.DataFrame(all_results)

# ... [La función main y las de ayuda deben ser copiadas de la respuesta anterior, pero usando esta nueva función de lectura] ...

if __name__ == "__main__":
    # Copia aquí las funciones auxiliares (parse_time, format_time_value, apply_styles_and_width)
    # y la función main() completa de la respuesta anterior, pero asegúrate de que llame a:
    # df_results = procesar_resultados_excel_corregido(ARCHIVO_ENTRADA_RESULTADOS)
    def main():
        print("Iniciando el procesamiento de resultados (versión final corregida)...")
        
        # Llama a la nueva función de lectura
        df_results = procesar_resultados_excel_corregido(ARCHIVO_ENTRADA_RESULTADOS)

        if df_results is None or df_results.empty:
            print("No se encontraron datos para procesar. Finalizando.")
            return

        # El resto del proceso es idéntico al de la respuesta anterior...
        df_results['tiempo_final_segundos'] = df_results['Tiempo Final'].apply(parse_time)
        df_results['Sexo'] = df_results['Prueba'].apply(lambda x: 'F' if 'Mujeres' in x else 'M')
        df_results['Lugar'] = df_results.groupby(['Prueba', 'Categoria'])['tiempo_final_segundos'].rank(method='min').astype(int)
        df_results['Puntos'] = df_results['Lugar'].map(PUNTOS).fillna(0).astype(int)
        
        # ... (copia el resto de la función main de la respuesta anterior aquí para generar los 3 reportes) ...
        print(f"¡Éxito! Reporte final '{ARCHIVO_SALIDA_PREMIACION}' generado correctamente.")
    
    # Para que este script sea autocontenido, aquí está el main completo y las funciones auxiliares
    def format_time_value(time_val):
        if pd.isna(time_val): return 'N/A'
        if hasattr(time_val, 'strftime'): return time_val.strftime('%M:%S.%f')[:-4]
        return str(time_val)

    def apply_styles_and_width(ws):
        from openpyxl.styles import Font, Border, Side
        font_header = Font(bold=True)
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        for row in ws.iter_rows():
            for cell in row:
                if cell.value:
                    cell.border = border
        for column_cells in ws.columns:
            length = max(len(str(cell.value or "")) for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = length + 4

    def parse_time(time_val):
        if pd.isna(time_val) or time_val == '': return float('inf')
        if hasattr(time_val, 'minute'): return time_val.minute * 60 + time_val.second + time_val.microsecond / 1_000_000
        time_str = str(time_val).replace(',', '.')
        try:
            parts = time_str.split(':')
            if len(parts) == 2: return int(parts[0]) * 60 + float(parts[1])
            return float(time_str)
        except (ValueError, IndexError): return float('inf')


    # --- FUNCIÓN MAIN COMPLETA ---
    def main_full():
        print("Iniciando el procesamiento de resultados (versión final corregida)...")
        
        df_results = procesar_resultados_excel_corregido(ARCHIVO_ENTRADA_RESULTADOS)
        if df_results is None or df_results.empty:
            print("No se encontraron datos para procesar. Finalizando.")
            return

        df_results['tiempo_final_segundos'] = df_results['Tiempo Final'].apply(parse_time)
        df_results['Sexo'] = df_results['Prueba'].apply(lambda x: 'F' if 'Mujeres' in x else 'M')
        df_results['Lugar'] = df_results.groupby(['Prueba', 'Categoria'])['tiempo_final_segundos'].rank(method='min').astype(int)
        df_results['Puntos'] = df_results['Lugar'].map(PUNTOS).fillna(0).astype(int)
        
        df_individual = df_results.groupby(['Categoria', 'Sexo', 'Nombre', 'Equipo']).agg(Puntos_Totales=('Puntos', 'sum')).reset_index()
        df_individual['Lugar'] = df_individual.groupby(['Categoria', 'Sexo'])['Puntos_Totales'].rank(method='min', ascending=False).astype(int)
        reporte_individual = df_individual.sort_values(by=['Categoria', 'Sexo', 'Lugar'])

        df_clubes = df_results.groupby('Equipo').agg(Puntos_Totales=('Puntos', 'sum')).reset_index()
        df_clubes['Lugar'] = df_clubes['Puntos_Totales'].rank(method='min', ascending=False).astype(int)
        reporte_clubes = df_clubes.sort_values(by='Lugar')[['Lugar', 'Equipo', 'Puntos_Totales']]

        wb = Workbook()
        
        ws1 = wb.active
        ws1.title = "Resultados por Prueba"
        fila_actual = 1
        font_titulo_prueba = Font(bold=True, size=16)
        font_titulo_cat = Font(bold=True, size=14)
        font_header_tabla = Font(bold=True)
        
        for prueba_nombre in df_results['Prueba'].unique():
            ws1.cell(row=fila_actual, column=1, value=prueba_nombre).font = font_titulo_prueba
            fila_actual += 2
            df_prueba = df_results[df_results['Prueba'] == prueba_nombre].sort_values(by='Categoria')
            for cat_nombre in df_prueba['Categoria'].unique():
                ws1.cell(row=fila_actual, column=1, value=f"Categoría: {cat_nombre}").font = font_titulo_cat
                fila_actual += 1
                df_grupo = df_prueba[df_prueba['Categoria'] == cat_nombre].sort_values(by='Lugar')
                df_grupo_display = df_grupo[['Lugar', 'Nombre', 'Equipo', 'Tiempo Final', 'Puntos']]
                df_grupo_display['Tiempo Final'] = df_grupo_display['Tiempo Final'].apply(format_time_value)
                
                headers = list(df_grupo_display.columns)
                for col, header_text in enumerate(headers, 1):
                    ws1.cell(row=fila_actual, column=col, value=header_text).font = font_header_tabla
                fila_actual += 1

                for _, r in df_grupo_display.iterrows():
                    ws1.append(list(r))
                fila_actual += len(df_grupo_display) + 1
        apply_styles_and_width(ws1)

        ws2 = wb.create_sheet("Premiacion Individual")
        fila_actual = 1
        for (cat, sexo), df_grupo in reporte_individual.groupby(['Categoria', 'Sexo']):
            sexo_texto = "(Hombres)" if sexo == 'M' else "(Mujeres)"
            titulo = f"Premiación - {cat} {sexo_texto}"
            ws2.cell(row=fila_actual, column=1, value=titulo).font = font_titulo_prueba
            fila_actual += 2

            df_grupo_display = df_grupo[['Lugar', 'Nombre', 'Equipo', 'Puntos_Totales']]
            headers = list(df_grupo_display.columns)
            for col, header_text in enumerate(headers, 1):
                ws2.cell(row=fila_actual, column=col, value=header_text).font = font_header_tabla
            fila_actual += 1
            
            for _, r in df_grupo_display.iterrows():
                ws2.append(list(r))
            fila_actual += len(df_grupo_display) + 2
        apply_styles_and_width(ws2)

        ws3 = wb.create_sheet("Puntuacion por Clubes")
        ws3.cell(row=1, column=1, value="Puntuación General por Clubes").font = font_titulo_prueba
        fila_actual = 3
        headers = list(reporte_clubes.columns)
        for col, header_text in enumerate(headers, 1):
            ws3.cell(row=fila_actual, column=col, value=header_text).font = font_header_tabla
        fila_actual += 1
        for _, r in reporte_clubes.iterrows():
            ws3.append(list(r))
        apply_styles_and_width(ws3)

        try:
            wb.save(ARCHIVO_SALIDA_PREMIACION)
            print("-" * 50)
            print("¡Proceso completado con éxito!")
            print(f"El reporte de premiación mejorado ha sido generado en:")
            print(f"'{ARCHIVO_SALIDA_PREMIACION}'")
            print("-" * 50)
        except Exception as e:
            print(f"Error al guardar el archivo de salida: {e}")

    main_full()
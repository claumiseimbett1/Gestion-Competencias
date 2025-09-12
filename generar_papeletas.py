# generar_papeletas.py
import pandas as pd
import os
import math
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# --- CONFIGURACIÓN ---
ARCHIVO_SEMBRADO = 'sembrado_competencia.xlsx'
ARCHIVO_PAPELETAS = 'papeletas_jueces.pdf'
CARRILES_POR_PAGINA = 8
LOGO_PATH = 'img/TEN.png'

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

def leer_datos_sembrado():
    """Lee los datos del sembrado desde el archivo Excel generado"""
    try:
        # Leer desde la planilla de inscripción directamente
        df = pd.read_excel('planilla_inscripcion.xlsx')
        info_cols = ['NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO']
        event_cols = [col for col in df.columns if col not in info_cols and 'Nø' not in col and 'FECHA DE NA' not in col]
        
        eventos = {}
        for index, row in df.iterrows():
            if pd.isna(row['NOMBRE Y AP']): continue
            sexo = row['SEXO'].upper()
            
            for prueba in event_cols:
                if pd.notna(row[prueba]):
                    nombre_prueba = f"{prueba} - {'Mujeres' if sexo == 'F' else 'Hombres'}"
                    if nombre_prueba not in eventos: eventos[nombre_prueba] = []
                    
                    nadador_info = {
                        "nombre": row['NOMBRE Y AP'], 
                        "equipo": row['EQUIPO'], 
                        "edad": int(row['EDAD']),
                        "categoria": row['CAT.'],
                        "tiempo_inscripcion": row[prueba], 
                        "tiempo_en_segundos": parse_time(row[prueba])
                    }
                    eventos[nombre_prueba].append(nadador_info)
        
        # Agrupar por categoría y crear series
        sembrado_estructurado = []
        for nombre_prueba, nadadores in eventos.items():
            nadadores_por_categoria = {}
            for nadador in nadadores:
                cat = nadador['categoria']
                if cat not in nadadores_por_categoria: 
                    nadadores_por_categoria[cat] = []
                nadadores_por_categoria[cat].append(nadador)
            
            for categoria, lista_nadadores in sorted(nadadores_por_categoria.items()):
                # Ordenar por tiempo
                lista_nadadores_ordenada = sorted(lista_nadadores, key=lambda x: x['tiempo_en_segundos'])
                
                # Crear series de 8 nadadores
                num_nadadores = len(lista_nadadores_ordenada)
                num_series = math.ceil(num_nadadores / 8)
                
                for serie_num in range(1, num_series + 1):
                    inicio = (serie_num - 1) * 8
                    fin = min(serie_num * 8, num_nadadores)
                    nadadores_serie = lista_nadadores_ordenada[inicio:fin]
                    
                    # Asignar carriles usando el orden estándar
                    lane_order = [4, 5, 3, 6, 2, 7, 1, 8]
                    carriles_serie = [None] * 8
                    
                    for i, nadador in enumerate(nadadores_serie):
                        if i < len(lane_order):
                            carril_pos = lane_order[i] - 1
                            carriles_serie[carril_pos] = nadador
                    
                    sembrado_estructurado.append({
                        'prueba': nombre_prueba,
                        'categoria': categoria,
                        'serie': serie_num,
                        'carriles': carriles_serie
                    })
        
        return sembrado_estructurado
    
    except Exception as e:
        print(f"Error al leer datos del sembrado: {e}")
        return []

def crear_papeleta_serie(serie_data, styles):
    """Crea una papeleta para una serie específica"""
    elements = []
    
    # Título de la serie
    title_style = ParagraphStyle(
        'SerieTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1E88E5'),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    serie_title = f"{serie_data['prueba']} - {serie_data['categoria']} - Serie {serie_data['serie']}"
    elements.append(Paragraph(serie_title, title_style))
    elements.append(Spacer(1, 6))
    
    # Crear tabla con carriles
    data = [['CARRIL', 'NADADOR', 'EQUIPO', 'TIEMPO COMPETENCIA']]
    
    for carril_num in range(1, 9):  # Carriles 1-8
        nadador = serie_data['carriles'][carril_num - 1]
        if nadador:
            nombre = nadador['nombre'][:25] + "..." if len(nadador['nombre']) > 25 else nadador['nombre']
            equipo = nadador['equipo'][:15] + "..." if len(nadador['equipo']) > 15 else nadador['equipo']
            data.append([str(carril_num), nombre, equipo, '___:___.__'])
        else:
            data.append([str(carril_num), '', '', ''])
    
    # Configurar la tabla
    table = Table(data, colWidths=[0.8*inch, 3.2*inch, 2*inch, 1.5*inch])
    table.setStyle(TableStyle([
        # Encabezados
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E88E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        
        # Celdas de datos
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
        
        # Columna de tiempo más destacada
        ('BACKGROUND', (3, 1), (3, -1), colors.HexColor('#FFF3E0')),
        ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
        
        # Altura de filas
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 15))
    
    # Información adicional
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_LEFT
    )
    
    info_text = f"Juez: __________________ Fecha: __________ Hora: __________"
    elements.append(Paragraph(info_text, info_style))
    elements.append(PageBreak())
    
    return elements

def generar_papeletas_pdf():
    """Genera el archivo PDF con todas las papeletas"""
    datos_sembrado = leer_datos_sembrado()
    
    if not datos_sembrado:
        return False, "No se pudieron leer los datos del sembrado"
    
    try:
        # Crear documento PDF en orientación horizontal
        doc = SimpleDocTemplate(
            ARCHIVO_PAPELETAS,
            pagesize=landscape(A4),
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        # Título principal
        title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Title'],
            fontSize=20,
            textColor=colors.HexColor('#1E88E5'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        elements.append(Paragraph("PAPELETAS DE JUECES - COMPETENCIA DE NATACIÓN", title_style))
        elements.append(Spacer(1, 12))
        elements.append(PageBreak())
        
        # Generar papeletas para cada serie
        for serie_data in datos_sembrado:
            papeleta_elements = crear_papeleta_serie(serie_data, styles)
            elements.extend(papeleta_elements)
        
        # Construir el PDF
        doc.build(elements)
        return True, f"Papeletas generadas exitosamente: {ARCHIVO_PAPELETAS}"
        
    except Exception as e:
        return False, f"Error al generar papeletas: {e}"

def main():
    """Función principal para ejecutar desde línea de comandos"""
    print("Generando papeletas para jueces...")
    
    # Verificar que existe el archivo de inscripción
    if not os.path.exists('planilla_inscripcion.xlsx'):
        print("ERROR: No se encontro el archivo 'planilla_inscripcion.xlsx'")
        print("Este archivo es necesario para generar las papeletas.")
        print("Primero genera el sembrado usando la aplicacion Streamlit.")
        return
    
    success, message = generar_papeletas_pdf()
    print(message)
    
    if success:
        total_series = len(leer_datos_sembrado())
        print(f"Total de series generadas: {total_series}")
        print(f"Archivo guardado como: {ARCHIVO_PAPELETAS}")

if __name__ == "__main__":
    main()
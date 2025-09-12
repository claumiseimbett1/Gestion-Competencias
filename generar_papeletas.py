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
    """Lee los datos del sembrado con series y carriles asignados"""
    try:
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
                        "sexo": sexo,
                        "tiempo_inscripcion": row[prueba], 
                        "tiempo_en_segundos": parse_time(row[prueba])
                    }
                    eventos[nombre_prueba].append(nadador_info)
        
        # Agrupar por categoría y crear series con carriles asignados
        papeletas_con_carriles = []
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
                    
                    for i, nadador in enumerate(nadadores_serie):
                        if i < len(lane_order):
                            carril_asignado = lane_order[i]
                            
                            papeleta = {
                                "nombre": nadador['nombre'],
                                "equipo": nadador['equipo'],
                                "categoria": nadador['categoria'],
                                "sexo": nadador['sexo'],
                                "prueba": nombre_prueba,
                                "serie": serie_num,
                                "carril": carril_asignado,
                                "tiempo_inscripcion": nadador['tiempo_inscripcion']
                            }
                            papeletas_con_carriles.append(papeleta)
        
        return papeletas_con_carriles
    
    except Exception as e:
        print(f"Error al leer datos del sembrado: {e}")
        return []

def crear_serie_con_papeletas(serie_data, styles):
    """Crea una página con múltiples papeletas de una serie"""
    elements = []
    
    if not serie_data:
        return elements
    
    # Información de la serie (primera papeleta como referencia)
    primera_papeleta = serie_data[0]
    
    # Título de la serie
    title_style = ParagraphStyle(
        'SerieTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1E88E5'),
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    elements.append(Paragraph(f"SERIE {primera_papeleta['serie']} - {primera_papeleta['prueba']}", title_style))
    elements.append(Spacer(1, 10))
    
    # Crear tabla con todas las papeletas de la serie
    data = [['CARRIL', 'NADADOR', 'EQUIPO', 'CAT.', 'TIEMPO COMP.']]
    
    # Ordenar por carril para mostrar en orden
    serie_ordenada = sorted(serie_data, key=lambda x: x['carril'])
    
    for papeleta in serie_ordenada:
        data.append([
            str(papeleta['carril']),
            papeleta['nombre'],
            papeleta['equipo'], 
            papeleta['categoria'],
            '___:___.___'
        ])
    
    # Rellenar carriles vacíos hasta 8
    while len(data) < 9:  # 8 carriles + header
        carril_num = len(data)
        data.append([str(carril_num), '(vacío)', '', '', ''])
    
    # Crear tabla
    table = Table(data, colWidths=[1*inch, 2.5*inch, 1.8*inch, 0.8*inch, 1.5*inch])
    
    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E88E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Información adicional del juez
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=10
    )
    
    elements.append(Paragraph("Juez: ________________________________    Fecha: ________________    Hora: ________________", info_style))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Observaciones: ____________________________________________________________________________________", info_style))
    elements.append(PageBreak())
    
    return elements

def generar_papeletas_pdf():
    """Genera el archivo PDF con papeletas organizadas por serie"""
    papeletas_sembrado = leer_datos_sembrado()
    
    if not papeletas_sembrado:
        return False, "No se pudieron leer los datos del sembrado"
    
    try:
        # Crear documento PDF en orientación horizontal
        doc = SimpleDocTemplate(
            ARCHIVO_PAPELETAS,
            pagesize=landscape(A4),
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        # Título principal
        title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#1E88E5'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        elements.append(Paragraph("PAPELETAS DE JUECES - COMPETENCIA DE NATACIÓN", title_style))
        elements.append(Spacer(1, 12))
        elements.append(PageBreak())
        
        # Agrupar papeletas por serie
        series = {}
        for papeleta in papeletas_sembrado:
            clave_serie = f"{papeleta['prueba']}_S{papeleta['serie']}"
            if clave_serie not in series:
                series[clave_serie] = []
            series[clave_serie].append(papeleta)
        
        # Generar una página por serie
        for clave_serie, papeletas_serie in sorted(series.items()):
            serie_elements = crear_serie_con_papeletas(papeletas_serie, styles)
            elements.extend(serie_elements)
        
        # Construir el PDF
        doc.build(elements)
        return True, f"Papeletas de jueces generadas exitosamente: {ARCHIVO_PAPELETAS}"
        
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
        total_papeletas = len(leer_datos_sembrado())
        print(f"Total de papeletas generadas: {total_papeletas}")
        print(f"Archivo guardado como: {ARCHIVO_PAPELETAS}")
        print(f"Formato: Una serie por página con series y carriles asignados")

if __name__ == "__main__":
    main()
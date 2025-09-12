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

def crear_papeleta_individual(papeleta_data, styles):
    """Crea una papeleta individual para un nadador específico"""
    elements = []
    
    # Título de la prueba
    title_style = ParagraphStyle(
        'PruebaTitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph(f"PRUEBA: {papeleta_data['prueba']}", title_style))
    elements.append(Spacer(1, 15))
    
    # Información del nadador con fondo
    nadador_style = ParagraphStyle(
        'NadadorInfo',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#F0F0F0'),
        borderPadding=10
    )
    
    nadador_info = f"{papeleta_data['nombre']} - {papeleta_data['equipo']} - {papeleta_data['categoria']}"
    elements.append(Paragraph(nadador_info, nadador_style))
    elements.append(Spacer(1, 25))
    
    # Crear tabla para Serie y Carril (lado a lado)
    serie_carril_data = [
        ['SERIE:', 'CARRIL:'],
        [str(papeleta_data['serie']), str(papeleta_data['carril'])]
    ]
    
    serie_carril_table = Table(serie_carril_data, colWidths=[2*inch, 2*inch])
    serie_carril_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('BOX', (0, 1), (0, 1), 2, colors.black),
        ('BOX', (1, 1), (1, 1), 2, colors.black),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e8f5e8')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, 1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 8)
    ]))
    
    elements.append(serie_carril_table)
    elements.append(Spacer(1, 30))
    
    # Título "TIEMPO DE COMPETENCIA"
    tiempo_title_style = ParagraphStyle(
        'TiempoTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#FF0000'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("TIEMPO DE COMPETENCIA:", tiempo_title_style))
    
    # Caja grande para el tiempo
    tiempo_style = ParagraphStyle(
        'TiempoLinea',
        parent=styles['Normal'],
        fontSize=28,
        alignment=TA_CENTER,
        fontName='Courier-Bold',
        spaceAfter=30
    )
    
    # Crear una tabla para el tiempo con borde grueso
    tiempo_data = [['_____ : _____ . _____']]
    tiempo_table = Table(tiempo_data, colWidths=[4*inch])
    tiempo_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, 0), 'Courier-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 28),
        ('BOX', (0, 0), (0, 0), 4, colors.black),
        ('BACKGROUND', (0, 0), (0, 0), colors.white),
        ('TOPPADDING', (0, 0), (0, 0), 20),
        ('BOTTOMPADDING', (0, 0), (0, 0), 20)
    ]))
    
    elements.append(tiempo_table)
    elements.append(Spacer(1, 40))
    
    # Información del juez (más pequeña, en gris)
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_LEFT,
        spaceAfter=5
    )
    
    elements.append(Paragraph("Juez: ________________________________", info_style))
    elements.append(Paragraph("Fecha: ______________    Hora: ______________", info_style))
    elements.append(PageBreak())
    
    return elements

def generar_papeletas_pdf():
    """Genera el archivo PDF con papeletas individuales"""
    papeletas_sembrado = leer_datos_sembrado()
    
    if not papeletas_sembrado:
        return False, "No se pudieron leer los datos del sembrado"
    
    try:
        # Crear documento PDF en orientación vertical (portrait)
        doc = SimpleDocTemplate(
            ARCHIVO_PAPELETAS,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        # Generar papeletas individuales (una por página)
        for papeleta_data in papeletas_sembrado:
            papeleta_elements = crear_papeleta_individual(papeleta_data, styles)
            elements.extend(papeleta_elements)
        
        # Construir el PDF
        doc.build(elements)
        return True, f"Papeletas individuales generadas exitosamente: {ARCHIVO_PAPELETAS}"
        
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
        print(f"Formato: Una papeleta individual por página con serie y carril asignados")

if __name__ == "__main__":
    main()
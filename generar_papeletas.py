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

def crear_papeleta_compacta(papeleta_data, styles):
    """Crea una papeleta compacta para múltiples por página"""
    elements = []
    
    # Título de la prueba (más compacto)
    title_style = ParagraphStyle(
        'PruebaTitle',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph(f"PRUEBA: {papeleta_data['prueba']}", title_style))
    
    # Información del nadador (más compacta)
    nadador_style = ParagraphStyle(
        'NadadorInfo',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    nadador_info = f"{papeleta_data['nombre']}<br/>{papeleta_data['equipo']} - {papeleta_data['categoria']}"
    elements.append(Paragraph(nadador_info, nadador_style))
    
    # Serie y Carril en tabla compacta
    serie_carril_data = [
        ['SERIE:', 'CARRIL:'],
        [str(papeleta_data['serie']), str(papeleta_data['carril'])]
    ]
    
    serie_carril_table = Table(serie_carril_data, colWidths=[0.8*inch, 0.8*inch])
    serie_carril_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('BOX', (0, 1), (0, 1), 1, colors.black),
        ('BOX', (1, 1), (1, 1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e8f5e8')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, 1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 4)
    ]))
    
    elements.append(serie_carril_table)
    elements.append(Spacer(1, 8))
    
    # Título "TIEMPO" (más compacto)
    tiempo_title_style = ParagraphStyle(
        'TiempoTitle',
        parent=styles['Heading1'],
        fontSize=10,
        textColor=colors.HexColor('#FF0000'),
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("TIEMPO DE COMPETENCIA:", tiempo_title_style))
    
    # Caja para el tiempo (más compacta)
    tiempo_data = [['_____ : _____ . _____']]
    tiempo_table = Table(tiempo_data, colWidths=[2*inch])
    tiempo_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, 0), 'Courier-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 16),
        ('BOX', (0, 0), (0, 0), 2, colors.black),
        ('BACKGROUND', (0, 0), (0, 0), colors.white),
        ('TOPPADDING', (0, 0), (0, 0), 8),
        ('BOTTOMPADDING', (0, 0), (0, 0), 8)
    ]))
    
    elements.append(tiempo_table)
    elements.append(Spacer(1, 6))
    
    # Línea para juez (más pequeña)
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=2
    )
    
    elements.append(Paragraph("Juez: _________________", info_style))
    
    return elements

def crear_pagina_con_3_papeletas(papeletas_grupo, styles):
    """Crea una página con 3 papeletas organizadas verticalmente"""
    elements = []
    
    for i, papeleta in enumerate(papeletas_grupo):
        if i > 0:
            elements.append(Spacer(1, 15))  # Separador entre papeletas
        
        # Crear una tabla que contenga toda la papeleta
        papeleta_elements = crear_papeleta_compacta(papeleta, styles)
        
        # Convertir elementos en una tabla para mejor control
        papeleta_content = []
        for element in papeleta_elements:
            if hasattr(element, 'text'):  # Es un Paragraph
                papeleta_content.append([element])
            elif hasattr(element, '_argW'):  # Es una Table
                papeleta_content.append([element])
            # Ignorar Spacers ya que controlamos el espaciado con la tabla
        
        # Crear tabla contenedora para la papeleta
        if papeleta_content:
            papeleta_table = Table(papeleta_content, colWidths=[6*inch])
            papeleta_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8)
            ]))
            elements.append(papeleta_table)
    
    elements.append(PageBreak())
    return elements

def crear_tabla_excel_style(papeletas_grupo, styles):
    """Crea una tabla estilo Excel con múltiples nadadores por página"""
    # Datos de la tabla: encabezados + filas de nadadores
    table_data = [
        ['Prueba', 'Serie', 'Carril', 'Nombre', 'Equipo', 'Categoría', 'Tiempo Inscripción', 'Tiempo Final']
    ]

    for papeleta in papeletas_grupo:
        table_data.append([
            papeleta['prueba'],
            str(papeleta['serie']),
            str(papeleta['carril']),
            papeleta['nombre'],
            papeleta['equipo'],
            papeleta['categoria'],
            str(papeleta.get('tiempo_inscripcion', '')),
            ''  # Campo vacío para tiempo final
        ])

    # Crear tabla con columnas ajustadas para landscape
    table = Table(table_data, colWidths=[
        2.5*inch,  # Prueba
        0.6*inch,  # Serie
        0.6*inch,  # Carril
        1.8*inch,  # Nombre
        1.3*inch,  # Equipo
        0.8*inch,  # Categoría
        1.0*inch,  # Tiempo Inscripción
        1.0*inch   # Tiempo Final
    ])

    # Estilo de la tabla
    table.setStyle(TableStyle([
        # Encabezados
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Filas de datos
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (2, -1), 'CENTER'),  # Serie y Carril centrados
        ('ALIGN', (6, 1), (7, -1), 'CENTER'),  # Tiempos centrados

        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Alternar colores de filas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),

        # Espacio en celdas
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))

    return table

def crear_papeleta_individual_excel(papeleta, width_per_papeleta):
    """Crea una papeleta individual en formato Excel"""
    papeleta_data = [
        ['PRUEBA:', papeleta['prueba']],
        ['SERIE:', str(papeleta['serie'])],
        ['CARRIL:', str(papeleta['carril'])],
        ['NADADOR:', papeleta['nombre']],
        ['EQUIPO:', papeleta['equipo']],
        ['CATEGORÍA:', papeleta['categoria']],
        ['T. INSCRIPCIÓN:', str(papeleta.get('tiempo_inscripcion', ''))],
        ['T. FINAL:', '']
    ]

    papeleta_table = Table(papeleta_data, colWidths=[width_per_papeleta * 0.4, width_per_papeleta * 0.6])

    papeleta_table.setStyle(TableStyle([
        # Estilo general
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),

        # Encabezados de campo en negrita
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E6F3FF')),

        # Campo de tiempo final resaltado
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFE6E6')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    return papeleta_table

def generar_papeletas_pdf_excel_3_per_row():
    """Genera papeletas exactas como Excel con 3 por fila para ahorrar papel"""
    papeletas_sembrado = leer_datos_sembrado()

    if not papeletas_sembrado:
        return False, "No se pudieron leer los datos del sembrado"

    try:
        # Crear documento PDF en orientación horizontal (landscape) para 3 columnas
        doc = SimpleDocTemplate(
            ARCHIVO_PAPELETAS.replace('.pdf', '_excel_3_per_row.pdf'),
            pagesize=landscape(A4),
            rightMargin=10*mm,
            leftMargin=10*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )

        styles = getSampleStyleSheet()
        elements = []

        # Título del documento
        title_style = ParagraphStyle(
            'DocumentTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph("PAPELETAS DE JUECES - COMPETENCIA DE NATACIÓN", title_style))
        elements.append(Spacer(1, 15))

        # Ancho disponible para 3 papeletas
        page_width = landscape(A4)[0] - 20*mm  # Restar márgenes
        width_per_papeleta = page_width / 3

        # Agrupar papeletas de 3 en 3
        PAPELETAS_POR_FILA = 3
        for i in range(0, len(papeletas_sembrado), PAPELETAS_POR_FILA):
            # Crear fila con hasta 3 papeletas
            fila_papeletas = papeletas_sembrado[i:i+PAPELETAS_POR_FILA]

            # Crear tablas individuales para cada papeleta
            tablas_fila = []
            for papeleta in fila_papeletas:
                tabla_papeleta = crear_papeleta_individual_excel(papeleta, width_per_papeleta)
                tablas_fila.append(tabla_papeleta)

            # Rellenar con espacios vacíos si quedan menos de 3
            while len(tablas_fila) < PAPELETAS_POR_FILA:
                tabla_vacia = Table([['', '']], colWidths=[width_per_papeleta * 0.4, width_per_papeleta * 0.6])
                tabla_vacia.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 1)]))
                tablas_fila.append(tabla_vacia)

            # Crear tabla contenedora para las 3 papeletas en una fila
            fila_table = Table([tablas_fila], colWidths=[width_per_papeleta] * PAPELETAS_POR_FILA)
            fila_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))

            elements.append(fila_table)
            elements.append(Spacer(1, 10))

            # Salto de página cada 4 filas (12 papeletas por página)
            if (i // PAPELETAS_POR_FILA + 1) % 4 == 0 and i + PAPELETAS_POR_FILA < len(papeletas_sembrado):
                elements.append(PageBreak())

        # Construir el PDF
        doc.build(elements)
        total_pages = math.ceil(len(papeletas_sembrado) / 12)  # 12 papeletas por página (4 filas x 3)
        return True, f"Papeletas Excel 3x3 generadas exitosamente: {ARCHIVO_PAPELETAS.replace('.pdf', '_excel_3_per_row.pdf')} ({len(papeletas_sembrado)} papeletas en ~{total_pages} páginas)"

    except Exception as e:
        return False, f"Error al generar papeletas Excel 3x3: {e}"

def generar_papeletas_pdf_excel_style():
    """Genera papeletas en formato de tabla Excel para ahorrar papel"""
    papeletas_sembrado = leer_datos_sembrado()

    if not papeletas_sembrado:
        return False, "No se pudieron leer los datos del sembrado"

    try:
        # Crear documento PDF en orientación horizontal (landscape) para más espacio
        doc = SimpleDocTemplate(
            ARCHIVO_PAPELETAS.replace('.pdf', '_excel_style.pdf'),
            pagesize=landscape(A4),
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )

        styles = getSampleStyleSheet()
        elements = []

        # Título del documento
        title_style = ParagraphStyle(
            'DocumentTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph("PAPELETAS DE JUECES - COMPETENCIA DE NATACIÓN", title_style))
        elements.append(Spacer(1, 10))

        # Agrupar eventos y series para optimizar espacio
        events_grouped = {}
        for papeleta in papeletas_sembrado:
            event_key = papeleta['prueba']
            if event_key not in events_grouped:
                events_grouped[event_key] = []
            events_grouped[event_key].append(papeleta)

        # Procesar cada evento
        for event_name, event_papeletas in events_grouped.items():
            # Título del evento
            event_title = ParagraphStyle(
                'EventTitle',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#4472C4'),
                alignment=TA_LEFT,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            elements.append(Paragraph(f"EVENTO: {event_name}", event_title))

            # Agrupar por series (máximo 15 nadadores por página para mantener legibilidad)
            NADADORES_POR_PAGINA = 15
            for i in range(0, len(event_papeletas), NADADORES_POR_PAGINA):
                grupo = event_papeletas[i:i+NADADORES_POR_PAGINA]
                table = crear_tabla_excel_style(grupo, styles)
                elements.append(table)
                elements.append(Spacer(1, 15))

                # Agregar salto de página si no es el último grupo
                if i + NADADORES_POR_PAGINA < len(event_papeletas):
                    elements.append(PageBreak())

            # Salto de página entre eventos
            if event_name != list(events_grouped.keys())[-1]:
                elements.append(PageBreak())

        # Construir el PDF
        doc.build(elements)
        total_pages = math.ceil(len(papeletas_sembrado) / 15)
        return True, f"Papeletas Excel-style generadas exitosamente: {ARCHIVO_PAPELETAS.replace('.pdf', '_excel_style.pdf')} ({len(papeletas_sembrado)} registros en ~{total_pages} páginas)"

    except Exception as e:
        return False, f"Error al generar papeletas Excel-style: {e}"

def generar_papeletas_pdf():
    """Genera el archivo PDF con 3 papeletas por página, optimizado para impresión"""
    papeletas_sembrado = leer_datos_sembrado()

    if not papeletas_sembrado:
        return False, "No se pudieron leer los datos del sembrado"

    try:
        # Crear documento PDF en orientación vertical (portrait) con márgenes optimizados
        doc = SimpleDocTemplate(
            ARCHIVO_PAPELETAS,
            pagesize=A4,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )

        styles = getSampleStyleSheet()
        elements = []

        # Título del documento
        title_style = ParagraphStyle(
            'DocumentTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph("PAPELETAS DE JUECES - COMPETENCIA DE NATACIÓN", title_style))
        elements.append(Spacer(1, 10))

        # Agrupar papeletas de 3 en 3 para cada página
        for i in range(0, len(papeletas_sembrado), 3):
            grupo_papeletas = papeletas_sembrado[i:i+3]
            pagina_elements = crear_pagina_con_3_papeletas(grupo_papeletas, styles)
            elements.extend(pagina_elements)

        # Construir el PDF
        doc.build(elements)
        return True, f"Papeletas PDF generadas exitosamente: {ARCHIVO_PAPELETAS} ({len(papeletas_sembrado)} papeletas en {math.ceil(len(papeletas_sembrado)/3)} páginas)"

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
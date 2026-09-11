# generar_papeletas.py
import pandas as pd
import os
from io import BytesIO
from planilla_utils import inscrito_en_prueba, ordered_prueba_hoja_keys, titulo_prueba_numerada
import math
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# --- CONFIGURACIÓN ---
SCRIPT_DIR = Path(__file__).resolve().parent
ARCHIVO_SEMBRADO = str(SCRIPT_DIR / 'sembrado_competencia.xlsx')
ARCHIVO_PAPELETAS = str(SCRIPT_DIR / 'papeletas_jueces.pdf')
ARCHIVO_PAPELETAS_3X2 = str(SCRIPT_DIR / 'papeletas_jueces_3x2.pdf')
ARCHIVO_PAPELETAS_EXCEL_STYLE = str(SCRIPT_DIR / 'papeletas_jueces_excel_style.pdf')
CARRILES_POR_PAGINA = 8
LOGO_PATH = str(SCRIPT_DIR / 'img' / 'TEN.png')

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
        if skipped:
            print(f"  Omitidos (no inscritos en planilla): {skipped}")
        return []
    if skipped:
        print(f"Papeletas: omitidos {skipped} nadador(es) no inscritos en planilla")
    return papeletas


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
    
    elements.append(Paragraph(papeleta_data['prueba'], title_style))
    
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

def _papeleta_paragraph(text, font_name='Helvetica', font_size=10, bold=False):
    """Texto con salto de línea automático para celdas de papeleta."""
    safe = str(text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    style = ParagraphStyle(
        'PapeletaCell',
        fontName='Helvetica-Bold' if bold else font_name,
        fontSize=font_size,
        leading=font_size + 3,
        wordWrap='CJK',
    )
    return Paragraph(safe, style)


def _papeleta_paragraph(text, font_name='Helvetica', font_size=10, bold=False):
    """Texto con salto de línea automático para celdas de papeleta."""
    safe = str(text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    style = ParagraphStyle(
        f'PapeletaCell_{font_size}_{"B" if bold else "R"}',
        fontName='Helvetica-Bold' if bold else font_name,
        fontSize=font_size,
        leading=font_size + 2,
        wordWrap='CJK',
    )
    return Paragraph(safe, style)


def _empty_papeleta_cell(width_per_papeleta, height):
    label_col = width_per_papeleta * 0.38
    value_col = width_per_papeleta * 0.62
    t = Table([['', '']], colWidths=[label_col, value_col], rowHeights=[height])
    t.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 1)]))
    return t


def crear_papeleta_individual_excel(papeleta, width_per_papeleta, large=False, max_height=None):
    """Crea una papeleta individual. `large=True` usa tipografía ampliada (layout 3x2)."""
    if large:
        label_size, value_size, pad = 9, 10, 4
        serie_size, carril_size = 12, 12
        final_size = 10
    else:
        label_size, value_size, pad = 8, 8, 3
        serie_size, carril_size = 8, 8
        final_size = 8

    prueba_short = str(papeleta.get('prueba', ''))
    if ' - ' in prueba_short:
        prueba_short = prueba_short.split(' - ')[0]

    papeleta_data = [
        [_papeleta_paragraph('Evento:', bold=True, font_size=label_size),
         _papeleta_paragraph(prueba_short, font_size=value_size)],
        [_papeleta_paragraph('SERIE:', bold=True, font_size=label_size),
         _papeleta_paragraph(str(papeleta['serie']), bold=True, font_size=serie_size)],
        [_papeleta_paragraph('CARRIL:', bold=True, font_size=label_size),
         _papeleta_paragraph(str(papeleta['carril']), bold=True, font_size=carril_size)],
        [_papeleta_paragraph('NADADOR:', bold=True, font_size=label_size),
         _papeleta_paragraph(papeleta['nombre'], font_size=value_size + 1)],
        [_papeleta_paragraph('EQUIPO:', bold=True, font_size=label_size),
         _papeleta_paragraph(papeleta['equipo'], font_size=value_size)],
        [_papeleta_paragraph('CAT.:', bold=True, font_size=label_size),
         _papeleta_paragraph(papeleta['categoria'], font_size=value_size)],
        [_papeleta_paragraph('T. INSCR.:', bold=True, font_size=label_size),
         _papeleta_paragraph(str(papeleta.get('tiempo_inscripcion', '')), font_size=value_size)],
        [_papeleta_paragraph('T. FINAL:', bold=True, font_size=label_size),
         _papeleta_paragraph(' ', font_size=final_size)],
    ]

    label_col = width_per_papeleta * 0.36
    value_col = width_per_papeleta * 0.64
    row_heights = None
    if max_height:
        weights = [1.0, 1.05, 1.05, 1.15, 1.0, 0.95, 0.95, 1.35]
        total_w = sum(weights)
        row_heights = [max_height * w / total_w for w in weights]

    papeleta_table = Table(
        papeleta_data,
        colWidths=[label_col, value_col],
        rowHeights=row_heights,
    )

    papeleta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), value_size),
        ('GRID', (0, 0), (-1, -1), 1.2 if large else 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), pad),
        ('BOTTOMPADDING', (0, 0), (-1, -1), pad),
        ('LEFTPADDING', (0, 0), (-1, -1), pad),
        ('RIGHTPADDING', (0, 0), (-1, -1), pad),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E6F3FF')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFE6E6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#FAFAFA')]),
    ]))

    return papeleta_table


def _build_papeletas_page_table(chunk, width_per_papeleta, row_height, large=True):
    """Tabla fija 3 filas × 2 columnas = 6 papeletas por página."""
    grid = []
    for row_idx in range(3):
        row_cells = []
        for col_idx in range(2):
            idx = row_idx * 2 + col_idx
            if idx < len(chunk):
                row_cells.append(
                    crear_papeleta_individual_excel(
                        chunk[idx],
                        width_per_papeleta,
                        large=large,
                        max_height=row_height - 4,
                    )
                )
            else:
                row_cells.append(_empty_papeleta_cell(width_per_papeleta, row_height))
        grid.append(row_cells)

    page_table = Table(
        grid,
        colWidths=[width_per_papeleta, width_per_papeleta],
        rowHeights=[row_height, row_height, row_height],
    )
    page_table.splitByRow = 0
    page_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return page_table


def generar_papeletas_pdf_3x2(session_state=None):
    """PDF compacto: 2 columnas × 3 filas = 6 papeletas por página, tipografía ampliada."""
    papeletas_sembrado = leer_datos_sembrado(session_state=session_state)

    if not papeletas_sembrado:
        return False, "No se pudieron leer los datos del sembrado", None

    PAPELETAS_POR_PAGINA = 6
    COLS = 2
    ROWS = 3

    try:
        buffer = BytesIO()
        page_w, page_h = landscape(A4)
        margin_lr = 8 * mm
        margin_tb = 8 * mm

        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=margin_lr,
            leftMargin=margin_lr,
            topMargin=margin_tb,
            bottomMargin=margin_tb,
        )

        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle(
            'DocumentTitle3x2',
            parent=styles['Heading1'],
            fontSize=13,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=4,
            spaceBefore=0,
            fontName='Helvetica-Bold',
        )
        title_block_h = 24
        usable_h = page_h - 2 * margin_tb
        row_h_first = (usable_h - title_block_h) / ROWS * 0.97
        row_h_next = usable_h / ROWS * 0.97
        page_width = page_w - 2 * margin_lr
        width_per_papeleta = page_width / COLS

        pages = [
            papeletas_sembrado[i:i + PAPELETAS_POR_PAGINA]
            for i in range(0, len(papeletas_sembrado), PAPELETAS_POR_PAGINA)
        ]

        for page_idx, chunk in enumerate(pages):
            if page_idx > 0:
                elements.append(PageBreak())
            if page_idx == 0:
                elements.append(Paragraph("PAPELETAS DE JUECES - COMPETENCIA DE NATACIÓN", title_style))
                row_h = row_h_first
            else:
                row_h = row_h_next

            elements.append(_build_papeletas_page_table(chunk, width_per_papeleta, row_h, large=True))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        Path(ARCHIVO_PAPELETAS_3X2).write_bytes(pdf_bytes)
        total_pages = len(pages)
        msg = (
            f"Papeletas PDF 3x2 generadas: {len(papeletas_sembrado)} papeletas "
            f"(6 por página: 2×3) en {total_pages} páginas"
        )
        return True, msg, pdf_bytes

    except Exception as e:
        return False, f"Error al generar papeletas PDF 3x2: {e}", None


def generar_papeletas_pdf_excel_style(session_state=None):
    """Genera papeletas en formato de tabla Excel para ahorrar papel"""
    papeletas_sembrado = leer_datos_sembrado(session_state=session_state)

    if not papeletas_sembrado:
        return False, "No se pudieron leer los datos del sembrado", None

    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
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
            elements.append(Paragraph(event_name, event_title))

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

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        Path(ARCHIVO_PAPELETAS_EXCEL_STYLE).write_bytes(pdf_bytes)
        total_pages = math.ceil(len(papeletas_sembrado) / 15)
        msg = (
            f"Papeletas Excel-style generadas: {len(papeletas_sembrado)} registros "
            f"en ~{total_pages} páginas"
        )
        return True, msg, pdf_bytes

    except Exception as e:
        return False, f"Error al generar papeletas Excel-style: {e}", None

def generar_papeletas_pdf(session_state=None):
    """Genera el archivo PDF con 3 papeletas por página, optimizado para impresión"""
    papeletas_sembrado = leer_datos_sembrado(session_state=session_state)

    if not papeletas_sembrado:
        return False, "No se pudieron leer los datos del sembrado", None

    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
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

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        Path(ARCHIVO_PAPELETAS).write_bytes(pdf_bytes)
        msg = (
            f"Papeletas PDF generadas: {len(papeletas_sembrado)} papeletas "
            f"en {math.ceil(len(papeletas_sembrado) / 3)} páginas"
        )
        return True, msg, pdf_bytes

    except Exception as e:
        return False, f"Error al generar papeletas: {e}", None

def main():
    """Función principal para ejecutar desde línea de comandos"""
    print("Generando papeletas para jueces...")
    
    # Verificar que existe el archivo de inscripción
    if not os.path.exists('planilla_inscripcion.xlsx'):
        print("ERROR: No se encontro el archivo 'planilla_inscripcion.xlsx'")
        print("Este archivo es necesario para generar las papeletas.")
        print("Primero genera el sembrado usando la aplicacion Streamlit.")
        return
    
    success, message, _pdf_bytes = generar_papeletas_pdf()
    print(message)
    
    if success:
        total_papeletas = len(leer_datos_sembrado())
        print(f"Total de papeletas generadas: {total_papeletas}")
        print(f"Archivo guardado como: {ARCHIVO_PAPELETAS}")
        print(f"Formato: Una papeleta individual por página con serie y carril asignados")

if __name__ == "__main__":
    main()
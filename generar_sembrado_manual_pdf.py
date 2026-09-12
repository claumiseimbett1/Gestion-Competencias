"""PDF continuo del sembrado manual acumulado (2 columnas, plano sin cuadros)."""
from io import BytesIO

from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from planilla_utils import (
    build_manual_seeding_title,
    sort_manual_seedings,
)

_SERIE_HEADERS = ['#', 'Nombre', 'Equipo', 'Ed', 'Cat', 'T.I.', 'T.C.']

# Tipografía ampliada para lectura en impresión
_FONT_BODY = 8
_FONT_HEADER = 8
_FONT_SERIE = 9
_FONT_PRUEBA = 10
_FONT_DOC = 13
_ROW_PAD = 1.5

_PLAIN_TABLE = TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), _FONT_BODY),
    ('LEADING', (0, 0), (-1, -1), _FONT_BODY + 2),
    ('TEXTCOLOR', (0, 0), (-1, -1), 'black'),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), _ROW_PAD),
    ('BOTTOMPADDING', (0, 0), (-1, -1), _ROW_PAD),
    ('LEFTPADDING', (0, 0), (-1, -1), 1),
    ('RIGHTPADDING', (0, 0), (-1, -1), 1),
])


def _sort_seedings(seedings, event_order=None):
    return sort_manual_seedings(seedings, event_order)


def _plain_text(value):
    return str(value or '').strip()


def _format_time(value):
    """Muestra el tiempo de inscripción/competencia completo, sin recortar."""
    if value is None:
        return ''
    if isinstance(value, str):
        s = value.strip()
        if not s or s.lower() in ('nan', 'none', 'nat'):
            return ''
        return s.replace(',', '.')

    try:
        import pandas as pd
        if pd.isna(value):
            return ''
    except (TypeError, ValueError, ImportError):
        pass

    if hasattr(value, 'total_seconds'):
        total = max(0.0, float(value.total_seconds()))
        minutes = int(total // 60)
        seconds = total % 60
        return f"{minutes}:{seconds:05.2f}"

    if hasattr(value, 'hour') and hasattr(value, 'minute'):
        total = (
            value.hour * 3600
            + value.minute * 60
            + value.second
            + getattr(value, 'microsecond', 0) / 1_000_000.0
        )
        minutes = int(total // 60)
        seconds = total % 60
        return f"{minutes}:{seconds:05.2f}"

    s = str(value).strip()
    return '' if s.lower() in ('nan', 'none', 'nat') else s.replace(',', '.')


def _truncate(text, max_len=24):
    s = str(text or '').strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + '…'


def _occupied_lanes(carriles):
    """Solo carriles con nadador, conservando el número real de carril (1-based)."""
    occupied = []
    for lane_num, swimmer in enumerate(carriles or [], 1):
        if swimmer:
            occupied.append((lane_num, swimmer))
    return occupied


def _build_serie_block_table(serie, col_width):
    """Bloque de serie en texto plano; omite carriles vacíos."""
    occupied = _occupied_lanes(serie.get('carriles', []))
    if not occupied:
        return Spacer(col_width, 1)

    col_widths = [
        col_width * 0.06,
        col_width * 0.30,
        col_width * 0.16,
        col_width * 0.05,
        col_width * 0.11,
        col_width * 0.16,
        col_width * 0.16,
    ]

    data = [[f"SERIE {serie['serie']}", '', '', '', '', '', '']]
    data.append(_SERIE_HEADERS)

    for lane_num, swimmer in occupied:
        data.append([
            str(lane_num),
            _truncate(swimmer.get('nombre', ''), 26),
            _truncate(swimmer.get('equipo', ''), 14),
            str(swimmer.get('edad', '')),
            _truncate(swimmer.get('categoria', ''), 11),
            _format_time(swimmer.get('tiempo', '')),
            _format_time(swimmer.get('tiempo_competencia', '')),
        ])

    table = Table(data, colWidths=col_widths)
    style = list(_PLAIN_TABLE.getCommands())
    style.extend([
        ('SPAN', (0, 0), (-1, 0)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), _FONT_SERIE),
        ('LEADING', (0, 0), (-1, 0), _FONT_SERIE + 2),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), _FONT_HEADER),
        ('FONTNAME', (0, 2), (0, -1), 'Helvetica-Bold'),
    ])
    table.setStyle(TableStyle(style))
    return table


def generate_all_manual_seedings_pdf(seedings, event_order=None, event_name='Sembrado Manual'):
    """
    PDF único y continuo en hoja vertical (A4): PRUEBA 1, 2, 3… en orden de cronograma.
    Series en dos columnas; sin carriles vacíos; tipografía ampliada.
    """
    if not seedings:
        return None

    buffer = BytesIO()
    page_size = A4
    doc = SimpleDocTemplate(
        buffer,
        pagesize=page_size,
        leftMargin=0.28 * inch,
        rightMargin=0.28 * inch,
        topMargin=0.30 * inch,
        bottomMargin=0.30 * inch,
        title=event_name,
    )

    styles = getSampleStyleSheet()
    doc_title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=_FONT_DOC,
        leading=_FONT_DOC + 2,
        textColor='black',
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    )
    prueba_title_style = ParagraphStyle(
        'PruebaTitle',
        parent=styles['Heading2'],
        fontSize=_FONT_PRUEBA,
        leading=_FONT_PRUEBA + 2,
        textColor='black',
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=2,
        fontName='Helvetica-Bold',
    )

    usable_width = page_size[0] - doc.leftMargin - doc.rightMargin
    col_gap = 0.10 * inch
    col_width = (usable_width - col_gap) / 2

    elements = [Paragraph(event_name, doc_title_style), Spacer(1, 4)]

    ordered = _sort_seedings(seedings, event_order)
    for item in ordered:
        titulo = build_manual_seeding_title(
            item['evento'], item['genero'], event_order or []
        )

        elements.append(Paragraph(titulo, prueba_title_style))

        # Solo series con al menos un nadador
        series_list = [
            s for s in item['data'].get('series', [])
            if _occupied_lanes(s.get('carriles', []))
        ]
        s_idx = 0
        while s_idx < len(series_list):
            left = _build_serie_block_table(series_list[s_idx], col_width)
            if s_idx + 1 < len(series_list):
                right = _build_serie_block_table(series_list[s_idx + 1], col_width)
            else:
                right = Spacer(col_width, 1)
            pair = Table([[left, right]], colWidths=[col_width, col_width])
            pair.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (0, 0), 0),
                ('LEFTPADDING', (1, 0), (1, 0), col_gap),
                ('RIGHTPADDING', (1, 0), (1, 0), 0),
            ]))
            elements.append(pair)
            elements.append(Spacer(1, 5))
            s_idx += 2

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

"""Utilidades compartidas para leer planilla_inscripcion.xlsx."""
import re
import pandas as pd


def safe_excel_sheet_title(name, used_titles):
    """Nombre de hoja válido en Excel (máx. 31 caracteres, sin \\ / * ? : [ ])."""
    s = re.sub(r'[\[\]*?:/\\]', '-', str(name)).strip() or 'Prueba'
    base = s[:31]
    candidate = base
    n = 1
    while candidate in used_titles:
        suffix = f' ({n})'
        max_base = max(0, 31 - len(suffix))
        candidate = (base[:max_base] + suffix).strip()
        n += 1
    used_titles.add(candidate)
    return candidate


def inscrito_en_prueba(cell_val):
    """
    True si el nadador está inscrito en la prueba (celda con dato).
    False si la celda está vacía o solo espacios: no nada esa prueba.

    Incluye marcas sin tiempo **s/t** o **S/T** (con espacios): el nadador **sí nada**
    la prueba; el sembrado lo trata como peor tiempo (ver parse_time en scripts de sembrado).
    """
    if pd.isna(cell_val):
        return False
    if isinstance(cell_val, str) and cell_val.strip() == "":
        return False
    return True


def ordered_prueba_hoja_keys(eventos_dict, event_cols):
    """
    Orden: columnas de la planilla; en cada prueba, Mujeres antes que Hombres.
    Claves esperadas: "{columna prueba} - Mujeres|Hombres".
    """
    ordered = []
    seen = set()
    for prueba in event_cols:
        for genero_suffix in ('Mujeres', 'Hombres'):
            key = f"{prueba} - {genero_suffix}"
            if key in eventos_dict:
                ordered.append(key)
                seen.add(key)
    remaining = [k for k in eventos_dict if k not in seen]

    def _fallback_sort_key(key):
        base = key.rsplit(' - ', 1)[0] if ' - ' in key else key
        tail = key.rsplit(' - ', 1)[-1] if ' - ' in key else ''
        gen = 0 if tail == 'Mujeres' else (1 if tail == 'Hombres' else 2)
        return (base, gen, key)

    ordered.extend(sorted(remaining, key=_fallback_sort_key))
    return ordered


def titulo_prueba_numerada(indice, nombre_prueba):
    """Ej.: PRUEBA 1 50M CROLL - Mujeres"""
    return f"PRUEBA {indice} {nombre_prueba}"

"""Utilidades compartidas para leer planilla_inscripcion.xlsx."""
import pandas as pd


def inscrito_en_prueba(cell_val):
    """
    True si el nadador está inscrito en la prueba (celda con dato).
    False si la celda está vacía o solo espacios: no nada esa prueba.
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

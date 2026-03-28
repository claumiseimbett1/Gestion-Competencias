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

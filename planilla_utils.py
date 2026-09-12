"""Utilidades compartidas para leer planilla_inscripcion.xlsx."""
import re
from pathlib import Path

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


def normalize_prueba_name(name):
    """Unificar nombre de prueba (p. ej. CROLL → LIBRE, 'hasta' → '-')."""
    text = str(name or '').strip()
    text = re.sub(r'CROLL', 'LIBRE', text, flags=re.IGNORECASE)
    # Solo "hasta" (título de categoría), no tocar rangos tipo Menores 2-3
    text = re.sub(r'\s+\bhasta\b\s+', ' - ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def prueba_match_key(name):
    """Clave comparable para emparejar columnas Excel ↔ event_order."""
    text = normalize_prueba_name(name).upper()
    text = (text.replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
                .replace('Ó', 'O').replace('Ú', 'U'))
    text = text.replace('METROS', 'M').replace('MTS', 'M').replace('MT ', 'M ')
    # Compactar guiones para que '2 - 3' == '2-3' y 'A - Master' == 'A-MASTER'
    text = re.sub(r'\s*[-–—]\s*', '-', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def match_column_to_event(column_name, event_names):
    """
    Devuelve el nombre canónico de event_names que corresponde a column_name,
    o None si no hay match.
    """
    if not column_name or not event_names:
        return None
    col_key = prueba_match_key(column_name)
    # Exacto por clave
    for event in event_names:
        if prueba_match_key(event) == col_key:
            return event
    # Contención (por si el Excel trae título más corto/largo)
    for event in event_names:
        ev_key = prueba_match_key(event)
        if col_key in ev_key or ev_key in col_key:
            return event
    return None


def align_planilla_columns_to_events(df, event_names):
    """
    Renombra columnas de la planilla para que coincidan con event_order.
    Ej: '… Infantil A hasta Master' → '… Infantil A - Master'
    """
    if df is None or df.empty:
        return df
    info_cols = {'NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO', 'FECHA DE NA', 'Nø', 'No'}
    rename_map = {}
    used_targets = set()
    for col in df.columns:
        if str(col).strip() in info_cols or str(col).upper().startswith('NØ'):
            continue
        if 'FECHA' in str(col).upper():
            continue
        matched = match_column_to_event(col, event_names)
        if matched and matched not in used_targets and matched != col:
            rename_map[col] = matched
            used_targets.add(matched)
        elif matched == col:
            used_targets.add(matched)
    if rename_map:
        df = df.rename(columns=rename_map)
    # También CROLL → LIBRE en lo que quede
    return normalize_planilla_columns(df)


def normalize_planilla_columns(df):
    """Renombra columnas de pruebas (CROLL→LIBRE, hasta→-)."""
    rename_map = {}
    for col in df.columns:
        new_name = normalize_prueba_name(col)
        if new_name != col:
            rename_map[col] = new_name
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


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
    """Ej.: PRUEBA 1 50M LIBRE - Mujeres (o conserva nombre si ya es PRUEBA N)."""
    nombre = str(nombre_prueba).strip()
    if nombre.upper().startswith(f"PRUEBA {indice}"):
        return nombre
    return f"PRUEBA {indice} {nombre}"


def gender_filter_to_sheet_suffix(gender_filter):
    """Convierte filtro de sembrado manual a sufijo de hoja (Mujeres/Hombres)."""
    return {
        'Femenino': 'Mujeres',
        'Masculino': 'Hombres',
        'Todos': None,
    }.get(gender_filter)


def get_manual_prueba_number(event_col, gender_filter, event_cols):
    """
    Número de prueba según orden de columnas en planilla / cronograma.
    Por columna: Femenino → par impar-1, Masculino → par; Todos → índice de columna.
    """
    if not event_col or not event_cols:
        return None
    try:
        col_idx = event_cols.index(event_col)
    except ValueError:
        return None
    if gender_filter == 'Todos':
        return col_idx + 1
    gender_order = {'Femenino': 0, 'Masculino': 1}
    g = gender_order.get(gender_filter, 0)
    return col_idx * 2 + g + 1


def event_from_prueba_number(prueba_num, gender_filter, event_cols):
    """Inverso de get_manual_prueba_number: PRUEBA N + género → columna de evento."""
    if not event_cols or prueba_num is None:
        return None, gender_filter
    try:
        n = int(prueba_num)
    except (TypeError, ValueError):
        return None, gender_filter
    if gender_filter == 'Todos':
        if 1 <= n <= len(event_cols):
            return event_cols[n - 1], gender_filter
        return None, gender_filter
    col_idx = (n - 1) // 2
    if 0 <= col_idx < len(event_cols):
        return event_cols[col_idx], gender_filter
    return None, gender_filter


def build_manual_seeding_title(event_col, gender_filter, event_cols):
    """Título PRUEBA N + nombre, alineado con hojas del sembrado automático."""
    n = get_manual_prueba_number(event_col, gender_filter, event_cols)
    if n is None:
        return f"{event_col} - {gender_filter}"
    if gender_filter == 'Todos':
        return titulo_prueba_numerada(n, event_col)
    suffix = gender_filter_to_sheet_suffix(gender_filter)
    return titulo_prueba_numerada(n, f"{event_col} - {suffix}")


def sort_manual_seedings(seedings, event_order=None):
    """Ordena sembrados manuales por número de prueba del cronograma."""
    def sort_key(item):
        evento = item['evento']
        genero = item['genero']
        n = get_manual_prueba_number(evento, genero, event_order or [])
        if n is not None:
            return (n, evento, genero)
        gen_order = {'Masculino': 0, 'Femenino': 1, 'Todos': 2}.get(genero, 3)
        if event_order and evento in event_order:
            return (event_order.index(evento), gen_order, evento)
        return (999, gen_order, evento)

    return sorted(seedings, key=sort_key)


def dedupe_manual_seedings(seedings):
    """
    Elimina sembrados redundantes acumulados en sesión.

    Si el evento ya tiene sembrado con filtro **Todos** (p. ej. editado a mano),
    se conserva ese y se omiten copias automáticas M/F del mismo evento.
    Si no hay Todos, se conservan Femenino y Masculino por separado.
    """
    by_event = {}
    for item in seedings:
        by_event.setdefault(item['evento'], []).append(item)

    deduped = []
    dropped = 0
    for items in by_event.values():
        todos_items = [i for i in items if i['genero'] == 'Todos']
        if todos_items:
            filtered = [todos_items[-1]]
            dropped += len(items) - 1
        else:
            filtered = [i for i in items if i['genero'] in ('Masculino', 'Femenino', 'Todos')]

        latest_by_key = {}
        for item in filtered:
            key = (item['evento'], item['genero'])
            if key in latest_by_key:
                dropped += 1
            latest_by_key[key] = item
        deduped.extend(latest_by_key.values())

    return sort_manual_seedings(deduped), dropped


def _event_has_gender_inscriptions(df, event_col, gender_filter):
    for _, row in df.iterrows():
        if not inscrito_en_prueba(row.get(event_col)) or pd.isna(row.get('NOMBRE Y AP')):
            continue
        swimmer_gender = 'Masculino' if str(row.get('SEXO', '')).upper() == 'M' else 'Femenino'
        if swimmer_gender == gender_filter:
            return True
    return False


def _is_edited_todos_seeding(todos_item):
    if not todos_item:
        return False
    data = todos_item.get('data') or todos_item
    return bool(
        data.get('editado_manual')
        or str(data.get('titulo', '')).strip().upper() == 'EDITADO MANUAL'
    )


def _pick_best_seeding_item(existing, candidate):
    """Prefiere sembrado editado a mano sobre copia automática."""
    if not existing:
        return candidate
    if candidate['data'].get('editado_manual') and not existing['data'].get('editado_manual'):
        return candidate
    if existing['data'].get('editado_manual') and not candidate['data'].get('editado_manual'):
        return existing
    return candidate


def split_seeding_by_gender(todos_item, gender_filter, event_col, event_cols):
    """
    Convierte un sembrado **Todos** (M+H mezclados) en una vista M o F
    conservando carril y serie de cada nadador.
    """
    data = todos_item['data']
    new_series = []
    for serie in data.get('series', []):
        new_carriles = [None] * 8
        for lane_idx, swimmer in enumerate(serie.get('carriles', [])):
            if not swimmer:
                continue
            if swimmer.get('sexo') != gender_filter:
                continue
            clean = {k: v for k, v in swimmer.items() if not str(k).startswith('_')}
            if lane_idx < len(new_carriles):
                new_carriles[lane_idx] = clean
        if any(new_carriles):
            new_series.append({'serie': serie.get('serie', len(new_series) + 1), 'carriles': new_carriles})

    total = sum(1 for serie in new_series for swimmer in serie['carriles'] if swimmer)
    if total == 0:
        return None

    return {
        'key': f"manual_seeding_{event_col}_{gender_filter}",
        'evento': event_col,
        'genero': gender_filter,
        'data': {
            'evento': event_col,
            'genero': gender_filter,
            'prueba_num': get_manual_prueba_number(event_col, gender_filter, event_cols),
            'titulo': build_manual_seeding_title(event_col, gender_filter, event_cols),
            'series': new_series,
            'nadadores_disponibles': [],
            'total_nadadores': total,
            'editado_manual': True,
            'desde_todos': True,
        },
    }


def prepare_seedings_for_export(seedings, event_order, df):
    """
    Arma el PDF/Excel con **exactamente** lo mismo que muestra la UI por prueba M/F.

    Usa las claves Femenino/Masculino del sembrado cargado. Solo divide **Todos**
    si no existe sembrado M o F para ese género.
    """
    by_key = {}
    for item in seedings:
        key = (item['evento'], item['genero'])
        by_key[key] = _pick_best_seeding_item(by_key.get(key), item)

    result = []
    skipped = 0
    for event_col in event_order or []:
        todos_item = by_key.get((event_col, 'Todos'))

        for gender_filter in ('Femenino', 'Masculino'):
            if not _event_has_gender_inscriptions(df, event_col, gender_filter):
                continue

            item = by_key.get((event_col, gender_filter))
            if item:
                result.append(item)
                continue

            if todos_item:
                split_item = split_seeding_by_gender(
                    todos_item, gender_filter, event_col, event_order
                )
                if split_item:
                    result.append(split_item)
                    continue

            skipped += 1

    return sort_manual_seedings(result, event_order), skipped


def _normalize_swimmer_name(name):
    return str(name or '').strip().upper()


def swimmer_inscrito_en_evento(df, nombre, event_col, equipo=None):
    """True si el nadador está inscrito en la prueba según planilla_inscripcion."""
    name_key = _normalize_swimmer_name(nombre)
    team_key = str(equipo or '').strip().upper()
    for _, row in df.iterrows():
        if _normalize_swimmer_name(row.get('NOMBRE Y AP')) != name_key:
            continue
        if team_key and str(row.get('EQUIPO', '')).strip().upper() != team_key:
            continue
        return inscrito_en_prueba(row.get(event_col))
    return False


def load_manual_seedings_dict(session_state=None, cache_path=None):
    """Carga sembrados manuales desde JSON + sesión (solo lectura)."""
    import json
    from pathlib import Path

    path = Path(cache_path or 'manual_seedings_cache.json')
    data = {}
    if path.exists():
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = {}

    if session_state is not None:
        for key, value in session_state.items():
            if not str(key).startswith('manual_seeding_'):
                continue
            if isinstance(value, dict) and 'series' in value:
                data[str(key)] = value
    return data


def manual_seedings_dict_to_list(data):
    seedings = []
    for key, val in data.items():
        if not str(key).startswith('manual_seeding_'):
            continue
        if not isinstance(val, dict) or 'series' not in val:
            continue
        seedings.append({
            'key': str(key),
            'evento': val.get('evento', str(key).replace('manual_seeding_', '')),
            'genero': val.get('genero', ''),
            'data': val,
        })
    return seedings


def build_papeletas_from_manual_seedings(seedings, df, event_cols):
    """
    Convierte sembrado manual (series/carriles) en papeletas individuales.
    Solo incluye nadadores inscritos en la planilla para esa prueba.
    """
    papeletas = []
    skipped_not_inscribed = 0
    for item in seedings:
        event_col = item['evento']
        gender = item['genero']
        if gender not in ('Femenino', 'Masculino'):
            continue
        titulo = item['data'].get('titulo') or build_manual_seeding_title(
            event_col, gender, event_cols
        )
        sexo = 'F' if gender == 'Femenino' else 'M'
        for serie in item['data'].get('series', []):
            serie_num = serie.get('serie', 1)
            for lane_idx, swimmer in enumerate(serie.get('carriles', [])):
                if not swimmer:
                    continue
                nombre = str(swimmer.get('nombre', '')).strip()
                equipo = swimmer.get('equipo', '')
                if not swimmer_inscrito_en_evento(df, nombre, event_col, equipo):
                    skipped_not_inscribed += 1
                    continue
                papeletas.append({
                    'nombre': nombre,
                    'equipo': equipo,
                    'categoria': swimmer.get('categoria', ''),
                    'sexo': sexo,
                    'prueba': titulo,
                    'serie': serie_num,
                    'carril': lane_idx + 1,
                    'tiempo_inscripcion': swimmer.get('tiempo', ''),
                })
    return papeletas, skipped_not_inscribed


def get_papeletas_from_manual_sembrado(session_state=None, cache_path=None):
    """
    Genera lista de papeletas leyendo el sembrado manual guardado.
    No modifica el sembrado. Retorna (papeletas, skipped, error_msg).
    """
    if not Path('planilla_inscripcion.xlsx').exists():
        return [], 0, 'Falta planilla_inscripcion.xlsx'

    df = pd.read_excel('planilla_inscripcion.xlsx')
    info_cols = ['NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO']
    event_cols = [
        c for c in df.columns
        if c not in info_cols and 'Nø' not in c and 'FECHA DE NA' not in c
    ]

    merged = load_manual_seedings_dict(session_state, cache_path)
    if not merged:
        return [], 0, 'No hay sembrado manual guardado (manual_seedings_cache.json)'

    raw = manual_seedings_dict_to_list(merged)
    seedings, export_skipped = prepare_seedings_for_export(raw, event_cols, df)
    if not seedings:
        return [], 0, 'El sembrado manual no tiene pruebas listas para exportar'

    papeletas, skipped = build_papeletas_from_manual_seedings(seedings, df, event_cols)
    if not papeletas:
        return [], skipped, 'No se encontraron nadadores inscritos en el sembrado manual'

    return papeletas, skipped, None


def prueba_column_name(orden):
    """Nombre de columna en planilla para la prueba N del cronograma."""
    return f"PRUEBA {int(orden)}"

# 🏊‍♀️ Sistema TEN — Uso local (CLI y scripts)

Guía para quien prefiere terminal, scripts sueltos o el menú `menu_local.py` en lugar de solo la interfaz web.

## 🚀 Inicio rápido

### Opción 1: Menú interactivo

```bash
python menu_local.py
```

Opciones típicas: inscripción, sembrado (categorías o tiempo), procesar resultados, revisar archivos, iniciar la app web.

### Opción 2: Aplicación web (funciones completas)

La **creación del evento**, las **papeletas** (PDF/Excel) y la **gestión de archivos** están en la app Streamlit:

```bash
streamlit run app.py
```

Abre `http://localhost:8501`.

### Opción 3: Scripts por separado

```bash
python 1-inscripcion_nadadores.py
python 2-generar_sembrado.py
python 3-generar_sembrado_por_tiempo.py
python 4-procesar_resultados.py
python 5-procesar_sembrado_tiempos.py
```

En Linux/mac, si no existe el comando `python`, usa `python3`.

## 📋 Qué hace cada parte

### Inscripción (`1-inscripcion_nadadores.py`)

- Registro manual, búsqueda en `BASE-DE-DATOS.xlsx`, importación masiva.
- Reportes PDF con estadísticas (requiere `reportlab` y dependencias del proyecto).

### Sembrado (`2` y `3`)

- **Por categorías** (`2-generar_sembrado.py`): agrupa por edad/categoría y ordena por tiempo dentro de cada grupo.
- **Por tiempo** (`3-generar_sembrado_por_tiempo.py`): orden global por marca dentro de cada prueba (sin bloques por categoría). Ambos Excel llevan **una hoja por prueba** con título `PRUEBA N …`.

Salidas habituales: `sembrado_competencia.xlsx`, `sembrado_competencia_POR_TIEMPO.xlsx`.

### Papeletas

Se generan desde la sección **“Generar Papeletas”** en `app.py`, usando `generar_papeletas.py` (PDF) y `generar_papeletas_excel.py` (Excel).

### Resultados (`4-procesar_resultados.py`)

- Entrada típica: `resultados_con_tiempos.xlsx`.
- Salida: `reporte_premiacion_final_CORREGIDO.xlsx` (puntos 1.º=9, 2.º=7, …).

### Sembrado con tiempos ya cargados (`5-procesar_sembrado_tiempos.py`)

Útil si tienes un Excel de sembrado donde ya anotaste tiempos de competencia y quieres llevarlos a un formato procesable como resultados. Detalles en `CLAUDE.md`.

## 📁 Archivos que verás con frecuencia

### Entrada

| Archivo | Uso |
|---------|-----|
| `event_config.json` | Pruebas y reglas del evento (créalo desde la app web: “Creación del Evento”) |
| `planilla_inscripcion.xlsx` | Nadadores inscritos |
| `BASE-DE-DATOS.xlsx` | Histórico para búsqueda en inscripción |
| `resultados_con_tiempos.xlsx` | Tiempos finales para premiación |

### Salida

| Archivo | Uso |
|---------|-----|
| `sembrado_competencia.xlsx` | Sembrado por categorías |
| `sembrado_competencia_POR_TIEMPO.xlsx` | Sembrado por tiempo (una hoja por prueba) |
| `reporte_premiacion_final_CORREGIDO.xlsx` | Premiación procesada |
| `papeletas_jueces.pdf` (u otro nombre según la app) | Papeletas PDF |

El menú local incluye **“Gestión de archivos”** para comprobar si existen varios de estos archivos en la carpeta de trabajo.

## ⚙️ Dependencias

```bash
pip install -r requirements.txt
```

Imprescindibles para PDF y la web: entre otras, `streamlit`, `pandas`, `openpyxl`, `reportlab`.

## 🔧 Problemas frecuentes

### `No module named 'reportlab'`

```bash
python -m pip install reportlab
```

Usa el **mismo** intérprete con el que ejecutas Streamlit (misma carpeta `venv` si usas entorno virtual).

### Falta `event_config.json`

Créalo desde la app web (**Creación del Evento**) antes de depender de filtros por prueba/edad en inscripción o sembrado.

### Scripts fallan por archivo no encontrado

Ejecuta el menú → opción de estado de archivos, o revisa mensajes de error: suelen indicar el nombre exacto esperado.

## 🌐 Web frente a solo CLI

| Aspecto | Streamlit (`app.py`) | Menú / scripts |
|--------|----------------------|----------------|
| Creación de evento | Sí | No (usa la web o edita `event_config.json` manualmente si conoces el formato) |
| Papeletas PDF/Excel | Sí | Integradas vía módulos; flujo habitual desde la web |
| Inscripción completa con UI | Sí | `menu_local` delega en el módulo; la experiencia más completa es la web |
| Sembrado y resultados | Sí | Sí, vía menú o `python 2-…`, `3-…`, `4-…` |

## 📞 Más ayuda

- Detalle de columnas Excel y flujos: `CLAUDE.md`
- Visión general del proyecto: `README.md`

---
🏊‍♀️ **Sistema TEN — Tecnología En Natación**

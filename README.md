# Sistema TEN - Gestión de Competencias de Natación

![TEN Logo](img/TEN.png)

Sistema para competencias de natación: evento, inscripción, sembrado (manual o automático), papeletas para jueces (PDF/Excel) y resultados con puntuación.

## Inicio rápido

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre `http://localhost:8501`. En Windows usa `python`; en Linux/mac a veces `python3`.

### Menú local (CLI)

```bash
python menu_local.py
```

### Scripts individuales

```bash
python 1-inscripcion_nadadores.py
python 2-generar_sembrado.py
python 3-generar_sembrado_por_tiempo.py
python 4-procesar_resultados.py
python 5-procesar_sembrado_tiempos.py
```

Las papeletas (`generar_papeletas.py` / `generar_papeletas_excel.py`) se usan desde la app web.

## Características

- **Evento**: pruebas, categorías y edades → `event_config.json`
- **Inscripción**: manual, base de datos o importación Excel → `planilla_inscripcion.xlsx`
- **Sembrado**: por categorías, por tiempo, o **manual** (series/carriles editables) → `manual_seedings_cache.json` / `sembrado_manual_completo.*`
- **Papeletas**: PDF (por página o compacto 3×2) y Excel, desde el sembrado manual
- **Resultados**: puntos y reportes de premiación
- **Backups**: carpeta `backups/` con copias de competencias (no se versiona)

## Flujo sugerido

1. Crear/ajustar el evento en la app → `event_config.json`
2. Inscribir nadadores → `planilla_inscripcion.xlsx`
3. Sembrar (manual recomendado, o automático por categoría/tiempo)
4. Generar papeletas PDF/Excel para jueces
5. Registrar tiempos y procesar resultados → `reporte_premiacion_final_CORREGIDO.xlsx`

## Archivos habituales

### Entrada

| Archivo | Uso |
|---------|-----|
| `event_config.json` | Configuración del evento |
| `planilla_inscripcion.xlsx` | Nadadores inscritos |
| `BASE-DE-DATOS.xlsx` | Histórico para búsqueda en inscripción |
| `categorias_festitorneo_2026.xlsx` | Categorías (carga/edición de evento) |
| `resultados_con_tiempos.xlsx` | Tiempos finales para premiación |

### Salida

| Archivo | Uso |
|---------|-----|
| `manual_seedings_cache.json` | Sembrado manual persistente |
| `sembrado_manual_completo.pdf` / `.xlsx` | Exportación del sembrado manual |
| `sembrado_competencia.xlsx` | Sembrado automático por categorías |
| `sembrado_competencia_POR_TIEMPO.xlsx` | Sembrado automático por tiempo |
| `papeletas_jueces.pdf` | Papeletas PDF |
| `papeletas_jueces_3x2.pdf` | Papeletas compactas (6 por hoja) |
| `reporte_premiacion_final_CORREGIDO.xlsx` | Premiación |

## Qué hace cada módulo

| Módulo | Función |
|--------|---------|
| `app.py` | App Streamlit (flujo completo) |
| `event_manager.py` | Crear/editar evento |
| `1-inscripcion_nadadores.py` | Inscripción y reportes |
| `2-generar_sembrado.py` | Sembrado por categorías |
| `3-generar_sembrado_por_tiempo.py` | Sembrado por tiempo (una hoja por prueba) |
| `4-procesar_resultados.py` | Premiación (1.º=9 … 8.º=1 pts) |
| `5-procesar_sembrado_tiempos.py` | Sembrado con tiempos → formato resultados |
| `generar_papeletas.py` | Papeletas PDF |
| `generar_papeletas_excel.py` | Papeletas Excel |
| `menu_local.py` | Menú por consola |

### Web vs CLI

| Aspecto | Streamlit (`app.py`) | Menú / scripts |
|---------|----------------------|----------------|
| Creación de evento | Sí | No (usa la web o edita `event_config.json`) |
| Sembrado manual y papeletas | Sí | Flujo habitual desde la web |
| Sembrado automático y resultados | Sí | Sí |

## Estructura

```
Gestion-Competencias/
├── app.py
├── menu_local.py
├── event_manager.py
├── planilla_utils.py
├── 1-inscripcion_nadadores.py … 5-procesar_sembrado_tiempos.py
├── generar_papeletas.py / generar_papeletas_excel.py
├── generar_sembrado_manual_pdf.py
├── img/TEN.png
├── event_logos/
├── backups/                    # Copias de competencias (gitignore)
├── requirements.txt
├── README.md
├── CLAUDE.md                   # Notas técnicas de desarrollo
├── BASE-DE-DATOS.xlsx
└── categorias_festitorneo_2026.xlsx
```

## Dependencias

```bash
pip install -r requirements.txt
```

| Paquete | Uso |
|---------|-----|
| streamlit | Interfaz web |
| pandas / openpyxl | Excel |
| reportlab | PDF |
| numpy / Pillow | Inscripción y logos en reportes |

### `No module named 'reportlab'`

```bash
python -m pip install reportlab
```

Usa el mismo Python/venv con el que ejecutas Streamlit.

### Falta `event_config.json`

Créalo en la app (**Creación del Evento**) antes de filtrar por pruebas/edades.

## Streamlit Cloud

1. Conecta el repo a [Streamlit Community Cloud](https://streamlit.io/cloud).
2. Entrada: `app.py`.
3. Sube o enlaza datos (`BASE-DE-DATOS.xlsx`, etc.); en la nube no están tus archivos locales salvo que los subas.

## Soporte

- Detalle técnico y columnas Excel: `CLAUDE.md`
- Issues en el repositorio (si está habilitado)

## Licencia

Si existe `LICENSE`, prevalece su texto. Si no, consulta a los mantenedores.

---

**Sistema TEN — Tecnología En Natación**

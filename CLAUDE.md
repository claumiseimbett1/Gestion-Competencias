# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About This Project

This is a swimming competition management system called "TEN - Gestión de Competencias". It's a Streamlit web application that processes swimming competition data, generates seeding arrangements, and produces results reports with scoring systems.

## How to Run the Application

```bash
streamlit run app.py
```

The application will start a web interface accessible at `http://localhost:8501`.

## Core Architecture

### Main Application (`app.py`)
- Streamlit web interface with multiple functional modules
- Imports and integrates three core processing scripts as modules
- Uses custom CSS styling with blue gradient theme matching TEN logo
- File upload/download functionality for Excel files
- Multi-page interface with sidebar navigation

### Core Processing Modules

1. **`generar_sembrado.py`** - Category-based seeding
   - Groups swimmers by age category, then sorts by time within each category
   - Places fastest swimmers in final heats (swimming competition standard)
   - Outputs: `sembrado_competencia.xlsx`

2. **`generar_sembrado_por_tiempo.py`** - Time-based seeding  
   - Sorts all swimmers purely by registration time, ignoring categories
   - Used for open competitions or qualifying events
   - Outputs: `sembrado_competencia_POR_TIEMPO.xlsx`

3. **`procesar_resultados.py`** - Results processing and scoring
   - Reads final race times and calculates rankings
   - Applies point system: 1st=9pts, 2nd=7pts, 3rd=6pts, 4th=5pts, 5th=4pts, 6th=3pts, 7th=2pts, 8th=1pt
   - Generates three reports: by event/category, individual rankings, team rankings
   - Outputs: `reporte_premiacion_final_CORREGIDO.xlsx`

## Required Input Files

- **`planilla_inscripcion.xlsx`** - Registration data with swimmer info and event entries
  - Expected columns: 'NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO', plus event columns with times
- **`resultados_con_tiempos.xlsx`** - Final race results (needed for results processing only)
  - Structured format with race times by event and category

## Key Data Processing Logic

### Time Parsing (`parse_time` function)
- Handles multiple time formats: MM:SS.ff, pandas datetime objects, plain seconds
- Returns time in seconds as float for sorting
- Invalid times return `float('inf')` to sort last

### Lane Assignment (`seed_series` function)  
- Uses standard swimming lane order: [4, 5, 3, 6, 2, 7, 1, 8] for 8-lane pools
- Fastest swimmers get center lanes in final heats
- Configurable pool lanes (default: 8)

### Results Processing
- Groups results by event and category for fair competition
- Handles both men's and women's events separately
- Automatic ranking calculation with proper tie handling

## File Structure

```
/
├── app.py                    # Main Streamlit application
├── generar_sembrado.py       # Category-based seeding
├── generar_sembrado_por_tiempo.py  # Time-based seeding  
├── procesar_resultados.py    # Results processing
├── img/TEN.png              # Organization logo
├── *.xlsx                   # Input/output Excel files
└── CLAUDE.md                # This file
```

## Dependencies

- `streamlit` - Web interface
- `pandas` - Excel file processing and data manipulation
- `openpyxl` - Excel file creation with formatting
- `pathlib` - File path handling

## Development Notes

- All processing functions can run independently as scripts or be imported as modules
- Excel files use openpyxl for advanced formatting (fonts, borders, column widths)
- The application includes comprehensive error handling and user feedback
- File operations include safety checks for required input files
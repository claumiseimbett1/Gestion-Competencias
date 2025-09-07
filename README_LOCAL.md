# 🏊‍♀️ Sistema TEN - Uso Local

## 🚀 Inicio Rápido

### Opción 1: Menú Interactivo (Recomendado)
```bash
python3 menu_local.py
```

### Opción 2: Aplicación Web
```bash
streamlit run app.py
```

### Opción 3: Scripts Individuales
```bash
# Inscripción de nadadores
python3 1-inscripcion_nadadores.py

# Sembrado por categorías 
python3 2-generar_sembrado.py

# Sembrado por tiempo
python3 3-generar_sembrado_por_tiempo.py

# Procesar resultados
python3 4-procesar_resultados.py
```

## 📋 Funcionalidades Disponibles

### ✍️ Inscripción de Nadadores
- **Manual**: Formulario completo de registro
- **Base de Datos**: Búsqueda en atletas existentes  
- **Importación Masiva**: Desde archivos Excel
- **Reportes PDF**: Con estadísticas completas

### 📊 Sembrado de Competencia
- **Por Categorías**: Agrupa por edad, ordena por tiempo
- **Por Tiempo**: Ignora categorías, solo ordenamiento temporal
- **Manual**: Organización personalizada (próximamente)

### 🏆 Procesamiento de Resultados  
- **Sistema de Puntos**: 1°=9pts, 2°=7pts, etc.
- **Reportes Múltiples**: Por evento, individual y equipos
- **Clasificaciones**: Automáticas por categoría

## 📁 Archivos del Sistema

### Archivos de Entrada
- `planilla_inscripcion.xlsx` - Datos de nadadores registrados
- `BASE-DE-DATOS.xlsx` - Base histórica de atletas
- `resultados_con_tiempos.xlsx` - Tiempos finales de competencia

### Archivos de Salida
- `sembrado_competencia.xlsx` - Sembrado por categorías
- `sembrado_competencia_POR_TIEMPO.xlsx` - Sembrado por tiempo
- `reporte_premiacion_final_CORREGIDO.xlsx` - Resultados procesados

## ⚙️ Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Dependencias Principales
- `streamlit` - Aplicación web
- `pandas` - Procesamiento de datos
- `openpyxl` - Manejo de Excel
- `reportlab` - Generación de PDFs

## 🔧 Resolución de Problemas

### Error de ReportLab
```bash
# Instalación manual
pip install reportlab
# o
pip3 install reportlab
```

### Archivos Faltantes
- El sistema verificará automáticamente archivos necesarios
- Mensajes claros sobre qué archivos faltan
- Sugerencias de dónde obtenerlos

## 💡 Consejos de Uso

### Para Competencias Pequeñas
1. Usar inscripción manual
2. Sembrado por categorías
3. Procesamiento directo

### Para Competencias Grandes
1. Importación masiva desde Excel
2. Base de datos de atletas
3. Sembrado por tiempo para qualifiers

### Flujo Completo
```bash
python3 menu_local.py
# 1. Inscripción → 2. Sembrado → 3. Resultados
```

## 🌐 Aplicación Web vs Local

| Característica | Web (Streamlit) | Local (Scripts) |
|----------------|-----------------|-----------------|
| **Interfaz** | Moderna, intuitiva | Línea de comandos |
| **Funcionalidad** | Completa | Completa |
| **Facilidad** | Muy fácil | Técnica |
| **Velocidad** | Media | Rápida |
| **Archivos** | Upload/Download | Directo |

## 📞 Soporte

Si encuentras problemas:
1. Revisa `CLAUDE.md` para documentación técnica
2. Verifica que todos los archivos estén en el directorio correcto
3. Usa el menú local para estado de archivos
4. Instala dependencias faltantes con `pip install -r requirements.txt`

---
🏊‍♀️ **Sistema TEN - Tecnología En Natación**
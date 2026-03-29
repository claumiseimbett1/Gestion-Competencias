# 🏊‍♀️ Sistema TEN - Gestión de Competencias de Natación

![TEN Logo](img/TEN.png)

## 🌟 Descripción

Sistema completo para la gestión de competencias de natación: configuración del evento, inscripción de nadadores, generación de sembrados (series y carriles), papeletas para jueces (PDF y Excel) y procesamiento de resultados con sistema de puntuación. Pensado para optimizar la organización de eventos deportivos acuáticos.

## ✨ Características principales

- 🎯 **Gestión del evento**: Pruebas disponibles, rangos de edad y configuración persistente (`event_config.json`)
- 🏊 **Inscripción de nadadores**: Manual, búsqueda en base de datos e importación masiva desde Excel
- 📊 **Sembrado**: Por categorías o solo por tiempo, con asignación estándar de carriles
- 📋 **Papeletas para jueces**: Generación en PDF y en Excel tras el sembrado
- 🏆 **Procesamiento de resultados**: Puntos, rankings y reportes por evento, individual y equipos
- 🌐 **Interfaz web**: Aplicación Streamlit con todas las funciones integradas
- 💻 **Uso local**: Menú por consola (`menu_local.py`) y scripts ejecutables por separado

## 🚀 Inicio rápido

### Aplicación web (recomendado)

En Windows suele usarse `python`; en Linux/mac a veces `python3`.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre `http://localhost:8501` en el navegador.

### Menú local interactivo

```bash
python menu_local.py
```

### Scripts individuales

```bash
python 1-inscripcion_nadadores.py
python 2-generar_sembrado.py
python 3-generar_sembrado_por_tiempo.py
python 4-procesar_resultados.py
python 5-procesar_sembrado_tiempos.py   # Sembrado con tiempos → formato de resultados
```

Los módulos `generar_papeletas.py` y `generar_papeletas_excel.py` se usan desde la app web o pueden importarse según necesidad; no suelen ejecutarse como `python generar_papeletas.py` en el flujo típico.

## 📁 Estructura del proyecto

```
📦 Gestion-Competencias/
├── app.py                          # Aplicación web Streamlit (punto de entrada principal)
├── menu_local.py                   # Menú CLI interactivo
├── event_manager.py                # Lógica de creación/edición de eventos
├── 1-inscripcion_nadadores.py      # Inscripciones
├── 2-generar_sembrado.py           # Sembrado por categorías
├── 3-generar_sembrado_por_tiempo.py # Sembrado por tiempo
├── 4-procesar_resultados.py        # Resultados y premiación
├── 5-procesar_sembrado_tiempos.py  # Convierte sembrado con tiempos a formato de resultados
├── generar_papeletas.py            # Papeletas PDF (ReportLab)
├── generar_papeletas_excel.py      # Papeletas Excel
├── img/TEN.png                     # Logo
├── requirements.txt
├── README.md                       # Este archivo
├── README_LOCAL.md                 # Uso sin depender solo de la web
├── CLAUDE.md                       # Notas técnicas para desarrollo
├── event_config.json               # Generado al configurar el evento (no suele versionarse vacío)
├── BASE-DE-DATOS.xlsx              # Base histórica de atletas (inscripción con búsqueda)
├── planilla_inscripcion.xlsx       # Planilla de inscripción (flujo principal)
└── …                               # Otros Excel de entrada/salida según la etapa
```

## 🔧 Instalación y configuración

### Prerrequisitos

- Python 3.8 o superior
- `pip`

### Dependencias destacadas

| Paquete    | Uso principal        |
|-----------|----------------------|
| streamlit | Interfaz web         |
| pandas    | Datos y Excel        |
| openpyxl  | Lectura/escritura .xlsx |
| reportlab | PDF (papeletas)      |
| matplotlib| Gráficos en reportes de inscripción |

Instalación:

```bash
pip install -r requirements.txt
```

## 🏊 Flujo de trabajo sugerido

1. **Crear o ajustar el evento** (en la app web): define pruebas y edades → se guarda `event_config.json`.
2. **Inscripción**: genera o completa `planilla_inscripcion.xlsx` (manual, BD o importación).
3. **Sembrado**: por categorías o por tiempo → `sembrado_competencia.xlsx` o `sembrado_competencia_POR_TIEMPO.xlsx` (ambos con **una hoja por prueba** numerada `PRUEBA N …`; en por-tiempo el orden dentro de la prueba es global por marca, sin series por categoría).
4. **Papeletas** (opcional): PDF / Excel para jueces.
5. **Resultados**: introduce tiempos en `resultados_con_tiempos.xlsx` (o usa `5-procesar_sembrado_tiempos.py` si partes de un sembrado ya anotado) y ejecuta el procesamiento → `reporte_premiacion_final_CORREGIDO.xlsx`.

## 📊 Formatos de archivo

### Entrada habitual

- **`event_config.json`**: Configuración del evento (lo crea la sección “Creación del Evento” en la web).
- **`planilla_inscripcion.xlsx`**: Nadadores y tiempos de inscripción.
- **`BASE-DE-DATOS.xlsx`**: Búsqueda de atletas (hojas esperadas según `CLAUDE.md`).
- **`resultados_con_tiempos.xlsx`**: Tiempos de carrera para premiación.

### Salida habitual

- Excel de sembrado y de premiación.
- **`papeletas_jueces.pdf`** (u otros nombres según la app) y exportaciones Excel de papeletas.

## 🌐 Despliegue en Streamlit Cloud

1. Conecta el repositorio a [Streamlit Community Cloud](https://streamlit.io/cloud).
2. Punto de entrada: `app.py`, rama principal.
3. Sube los archivos de datos necesarios o configura secretos/almacenamiento: en la nube no están tus `BASE-DE-DATOS.xlsx` locales salvo que los subas o enlaces una fuente externa.

## 🔧 Resolución de problemas

### `ModuleNotFoundError: No module named 'reportlab'`

Instala en **el mismo Python** que usa Streamlit:

```bash
python -m pip install reportlab
```

Si usas un entorno virtual, actívalo antes de instalar y de ejecutar `streamlit run app.py`.

### Comprobar paquetes

```bash
python -m pip show streamlit pandas openpyxl reportlab
```

### Archivos faltantes

La aplicación valida entradas y muestra mensajes indicando qué archivo falta o qué configuración crear primero.

## 🤝 Contribuciones

1. Fork del repositorio.
2. Rama de funcionalidad (`git checkout -b feature/nombre-descriptivo`).
3. Commits con mensajes claros.
4. Pull request con descripción del cambio.

## 📝 Changelog (resumen)

### Actual

- Interfaz web con creación de evento, inscripción, sembrado, papeletas (PDF/Excel), resultados y gestión de archivos.
- Scripts numerados `1`–`5` y módulos de papeletas alineados con la app.

### Versiones anteriores

- Scripts por consola, sembrado por categorías/tiempo, sistema de puntos y reportes Excel.

## 📞 Soporte

- Documentación técnica: `CLAUDE.md`
- Uso local y archivos: `README_LOCAL.md`
- Incidencias: abre un issue en el repositorio si está habilitado.

## ⚖️ Licencia

Si el repositorio incluye un archivo `LICENSE`, prevalece su texto. Si no existe, consulta con los mantenedores del proyecto.

## 🏆 Agradecimientos

- **TEN (Tecnología En Natación)** — identidad visual
- Comunidad y pruebas en competencias reales

---

<div align="center">

**Sistema TEN — Gestión de Competencias de Natación**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://python.org/)

</div>

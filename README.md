# 🏊‍♀️ Sistema TEN - Gestión de Competencias de Natación

![TEN Logo](img/TEN.png)

## 🌟 Descripción

Sistema completo para la gestión de competencias de natación que incluye inscripción de nadadores, generación de sembrados y procesamiento de resultados con sistema de puntuación. Desarrollado para optimizar la organización de eventos deportivos acuáticos.

## ✨ Características Principales

- 🏊 **Inscripción de Nadadores**: Manual, búsqueda en BD e importación masiva
- 📊 **Sembrado Inteligente**: Por categorías o tiempo con organización automática de series
- 🏆 **Procesamiento de Resultados**: Sistema de puntos y reportes por equipos
- 📋 **Reportes PDF**: Documentos profesionales con branding corporativo  
- 🌐 **Interfaz Web Moderna**: Aplicación Streamlit intuitiva
- 💻 **Uso Local**: Scripts independientes para uso técnico

## 🚀 Inicio Rápido

### 🌐 Aplicación Web (Recomendado)
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```
Accede a `http://localhost:8501` en tu navegador.

### 💻 Menú Local Interactivo
```bash
python3 menu_local.py
```

### ⚡ Scripts Individuales
```bash
python3 1-inscripcion_nadadores.py    # Inscripciones
python3 2-generar_sembrado.py         # Sembrado por categorías
python3 3-generar_sembrado_por_tiempo.py  # Sembrado por tiempo
python3 4-procesar_resultados.py      # Procesar resultados
```

## 📁 Estructura del Proyecto

```
📦 gestion-competencias/
├── 🌐 app.py                          # Aplicación web principal
├── 💻 menu_local.py                   # Menú CLI interactivo
├── 🏊 1-inscripcion_nadadores.py      # Sistema de inscripciones
├── 📊 2-generar_sembrado.py           # Sembrado por categorías
├── ⏱️ 3-generar_sembrado_por_tiempo.py # Sembrado por tiempo
├── 🏆 4-procesar_resultados.py        # Procesamiento de resultados
├── 🗄️ BASE-DE-DATOS.xlsx             # Base de datos de atletas
├── 📋 planilla_inscripcion.xlsx      # Template de inscripción
├── 🖼️ img/TEN.png                    # Logo corporativo
├── 📦 requirements.txt               # Dependencias Python
├── 📚 README.md                      # Este archivo
├── 📝 README_LOCAL.md                # Guía uso local
├── 🔧 CLAUDE.md                      # Documentación técnica
└── 🚫 .gitignore                     # Archivos excluidos
```

## 🔧 Instalación y Configuración

### 📋 Prerrequisitos
- Python 3.8+
- pip (gestor de paquetes)

### 📦 Dependencias Principales
```txt
streamlit>=1.28.0    # Aplicación web
pandas>=2.0.0        # Manipulación de datos  
openpyxl>=3.1.0      # Archivos Excel
reportlab>=4.0.0     # Generación PDF
pillow>=10.0.0       # Procesamiento imágenes
```

### ⚙️ Instalación Completa
```bash
# Clonar repositorio
git clone <repository-url>
cd gestion-competencias

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python3 menu_local.py
```

## 🏊 Flujo de Trabajo

### 1️⃣ **Inscripción de Nadadores**
- **Manual**: Formulario completo con validación
- **Base de Datos**: Búsqueda en histórico de atletas  
- **Importación Masiva**: Desde archivos Excel existentes

### 2️⃣ **Generación de Sembrado**
- **Por Categorías**: Grupos por edad + ordenamiento por tiempo
- **Por Tiempo**: Ordenamiento global ignorando categorías
- **Distribución Inteligente**: Asignación automática de carriles

### 3️⃣ **Procesamiento de Resultados**
- **Sistema de Puntos**: 1°=9pts, 2°=7pts, 3°=6pts, etc.
- **Reportes Múltiples**: Por evento, individual y equipos
- **Rankings Automáticos**: Por categoría y género

## 📊 Formatos de Archivo Soportados

### Entrada
- **`.xlsx`** - Planillas de inscripción y resultados
- **Base de Datos** - Hojas `FPROYECCION 2025T` y `M. PROYECCION 2025`

### Salida  
- **`.xlsx`** - Sembrados y reportes de resultados
- **`.pdf`** - Reportes con branding corporativo

## 🌐 Deploy en Streamlit Cloud

1. **Fork** este repositorio
2. **Conectar** con Streamlit Cloud  
3. **Configurar** rama `main` y archivo `app.py`
4. **Deploy automático** - ¡Listo!

La aplicación incluye gestión automática de dependencias y archivos base.

## 🔧 Resolución de Problemas

### ❌ Error de ReportLab
```bash
pip install reportlab --upgrade
```

### 📁 Archivos Faltantes
El sistema verifica automáticamente archivos necesarios y proporciona mensajes claros sobre dependencias faltantes.

### 🐛 Problemas de Importación
```bash
# Verificar entorno Python
python3 --version
pip list | grep -E "(streamlit|pandas|openpyxl|reportlab)"
```

## 🤝 Contribuciones

1. **Fork** el proyecto
2. **Crear** rama feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** cambios (`git commit -m 'Add AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abrir** Pull Request

## 📝 Changelog

### v2.0 (Actual)
- ✅ Interfaz web Streamlit completa
- ✅ Menú CLI interactivo  
- ✅ Importación masiva desde Excel
- ✅ Base de datos dual (femenino/masculino)
- ✅ PDFs con colores corporativos TEN
- ✅ Gestión de archivos integrada
- ✅ Sembrado unificado con pestañas

### v1.0 (Inicial)
- ✅ Scripts individuales básicos
- ✅ Procesamiento por categorías
- ✅ Sistema de puntuación 
- ✅ Generación de reportes

## 📞 Soporte

- 📚 **Documentación Técnica**: Ver `CLAUDE.md`
- 💻 **Uso Local**: Ver `README_LOCAL.md`  
- 🐛 **Issues**: Crear issue en GitHub
- 📧 **Contacto**: [Información de contacto]

## ⚖️ Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🏆 Agradecimientos

- **TEN (Tecnología En Natación)** - Logo y branding
- **Comunidad de Natación** - Feedback y testing
- **Desarrolladores** - Contribuciones técnicas

---

<div align="center">

**🏊‍♀️ Sistema TEN - Gestión de Competencias de Natación 🏊‍♂️**

*Optimizando la organización de eventos deportivos acuáticos*

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF-green)](https://www.reportlab.com/)

</div>
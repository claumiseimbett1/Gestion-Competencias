import streamlit as st
import pandas as pd
import io
import os
from pathlib import Path
from datetime import datetime
#import subprocess  # No longer needed
import sys

# Importar las funciones de los scripts existentes
#import importlib.util # No longer needed

# Importar los scripts directly  
import importlib.util

# Importar el módulo de inscripción con el nuevo nombre
spec = importlib.util.spec_from_file_location("inscripcion_nadadores", "1-inscripcion_nadadores.py")
inscripcion_nadadores = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inscripcion_nadadores)

# Importar los otros módulos con sus nuevos nombres
spec1 = importlib.util.spec_from_file_location("generar_sembrado", "2-generar_sembrado.py")
script1 = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(script1)

spec2 = importlib.util.spec_from_file_location("generar_sembrado_por_tiempo", "3-generar_sembrado_por_tiempo.py")
script2 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(script2)

spec3 = importlib.util.spec_from_file_location("procesar_resultados", "4-procesar_resultados.py")
script3 = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(script3)

# Importar ambos módulos de papeletas
spec4 = importlib.util.spec_from_file_location("generar_papeletas", "generar_papeletas.py")
papeletas_pdf_module = importlib.util.module_from_spec(spec4)
spec4.loader.exec_module(papeletas_pdf_module)

spec5 = importlib.util.spec_from_file_location("generar_papeletas_excel", "generar_papeletas_excel.py")
papeletas_excel_module = importlib.util.module_from_spec(spec5)
spec5.loader.exec_module(papeletas_excel_module)

#Configuración de la página
st.set_page_config(
    page_title="TEN - Gestión de Competencias",
    page_icon="🏊‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

#CSS personalizado con colores del logo
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1E88E5 0%, #64B5F6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #1E88E5 0%, #64B5F6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #1565C0 0%, #42A5F5 100%);
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.3);
        transform: translateY(-2px);
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .feature-card h3 {
        color: #1E88E5;
        margin-top: 0;
    }
    
    .sidebar .stSelectbox label {
        color: #1E88E5;
        font-weight: bold;
    }
    
    .success-message {
        background: #E8F5E8;
        color: #2E7D2E;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .info-message {
        background: #E3F2FD;
        color: #1565C0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: #FFF3E0;
        color: #E65100;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF9800;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

#def load_script_functions(): # No longer needed
#    """Cargar funciones de los scripts existentes"""
#    functions = {}
#    
#    # Cargar funciones del script 1
#    spec1 = importlib.util.spec_from_file_location("script1", "1-generar_sembrado.py")
#    script1 = importlib.util.module_from_spec(spec1)
#    spec1.loader.exec_module(script1)
#    functions['generar_sembrado_categoria'] = script1.main
#    
#    # Cargar funciones del script 2
#    spec2 = importlib.util.spec_from_file_location("script2", "2-generar_sembrado_por_tiempo.py")
#    script2 = importlib.util.module_from_spec(spec2)
#    spec2.loader.exec_module(script2)
#    functions['generar_sembrado_tiempo'] = script2.main
#    
#    # Cargar funciones del script 3
#    spec3 = importlib.util.spec_from_file_location("script3", "3-procesar_resultados.py")
#    script3 = importlib.util.module_from_spec(spec3)
#    spec3.loader.exec_module(script3)
#    functions['procesar_resultados'] = script3.main_full
#    
#    return functions

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🏊‍♀️ TEN - Gestión de Competencias</h1>
        <p>Sistema completo para administrar competencias de natación</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.image("img/TEN.png", width=150)
    st.sidebar.markdown("## 📋 Panel de Control")
    
    # Selector de funciones
    opcion = st.sidebar.selectbox(
        "Selecciona una operación:",
        [
            "🏠 Inicio",
            "✍️ Inscripción de Nadadores",
            "📊 Sembrado de Competencia",
            "📋 Generar Papeletas",
            "🏆 Procesar Resultados",
            "📁 Gestión de Archivos"
        ]
    )
    
    if opcion == "🏠 Inicio":
        mostrar_inicio()
    elif opcion == "✍️ Inscripción de Nadadores":
        inscripcion_nadadores_interface()
    elif opcion == "📊 Sembrado de Competencia":
        sembrado_competencia_interface()
    elif opcion == "📋 Generar Papeletas":
        generar_papeletas_interface()
    elif opcion == "🏆 Procesar Resultados":
        procesar_resultados()
    elif opcion == "📁 Gestión de Archivos":
        gestion_archivos()

def mostrar_inicio():
    st.markdown("## 🏊‍♀️ Bienvenido al Sistema TEN")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>✍️ Inscripción de Nadadores</h3>
            <p>Registra nuevos nadadores con sus datos personales y tiempos de inscripción por prueba.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Sembrado por Categoría</h3>
            <p>Organiza las series agrupando nadadores por categoría de edad y luego por tiempo dentro de cada categoría.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🏆 Procesamiento de Resultados</h3>
            <p>Genera reportes de premiación con sistema de puntos y clasificaciones por categoría y equipos.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⏱️ Sembrado por Tiempo</h3>
            <p>Crea series basándose únicamente en los tiempos de inscripción, sin importar la categoría.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>📁 Gestión de Archivos</h3>
            <p>Sube y descarga archivos Excel, visualiza datos y administra los archivos del sistema.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-message">
        <h4>📋 Flujo de trabajo recomendado:</h4>
        <ol>
            <li><strong>Inscribe nadadores</strong> usando el formulario de inscripción integrado</li>
            <li>Genera el sembrado (por categoría o tiempo)</li>
            <li>Después de la competencia, procesa los resultados</li>
            <li>Descarga los reportes generados</li>
        </ol>
        <p><em>Alternativamente, puedes subir un archivo <strong>planilla_inscripcion.xlsx</strong> existente en "Gestión de Archivos"</em></p>
    </div>
    """, unsafe_allow_html=True)

def generar_sembrado_categoria():
    st.markdown("## 📊 Generar Sembrado por Categoría")
    
    st.markdown("""
    <div class="info-message">
        Este proceso agrupa los nadadores por categoría de edad y luego los ordena por tiempo dentro de cada categoría.
        Las series se organizan con los nadadores más rápidos en las últimas series.
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar archivo de entrada
    if not os.path.exists("planilla_inscripcion.xlsx"):
        st.markdown("""
        <div class="warning-message">
            ⚠️ No se encontró el archivo <strong>planilla_inscripcion.xlsx</strong>. 
            Por favor, súbelo en la sección "Gestión de Archivos".
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Mostrar información del archivo
    try:
        df = pd.read_excel("planilla_inscripcion.xlsx")
        st.success(f"✅ Archivo cargado: {len(df)} nadadores registrados")
        
        # Mostrar preview
        if st.checkbox("Ver vista previa de datos"):
            st.dataframe(df.head(10))
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🚀 Generar Sembrado por Categoría", type="primary"):
            with st.spinner("Generando sembrado..."):
                try:
                    # Ejecutar el script
                    #result = subprocess.run([sys.executable, "1-generar_sembrado.py"],
                    #                      capture_output=True, text=True)
                    script1.main() # Llamar la función directamente
                    
                    #if result.returncode == 0:
                    st.markdown("""
                        <div class="success-message">
                            ✅ <strong>Sembrado generado exitosamente!</strong><br>
                            Archivo creado: <code>sembrado_competencia.xlsx</code>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Mostrar output
                    #if result.stdout:
                    #    st.text("Output:")
                    #    st.text(result.stdout)
                    
                    #else:
                    #    st.error(f"Error al generar sembrado: {result.stderr}")
                        
                except Exception as e:
                    st.error(f"Error al ejecutar el script: {e}")
    
    with col2:
        if os.path.exists("sembrado_competencia.xlsx"):
            st.info("📄 Archivo generado disponible para descarga")
            
            # Botón de descarga
            with open("sembrado_competencia.xlsx", "rb") as file:
                st.download_button(
                    label="⬇️ Descargar Sembrado por Categoría",
                    data=file.read(),
                    file_name="sembrado_competencia.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # Sección de papeletas para jueces
            st.markdown("### 📋 Generar Papeletas para Jueces")
            st.info("Las papeletas se generan en formato Excel con rectángulos imprimibles")
            
            if st.button("📄 Generar Papeletas Excel", type="secondary", key="papeletas_excel_cat"):
                with st.spinner("Generando papeletas en Excel..."):
                    success, message = papeletas_excel_module.generar_papeletas_excel()
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            
            # Botón de descarga para papeletas Excel si existe
            if os.path.exists("papeletas_jueces.xlsx"):
                st.info("📄 Papeletas Excel disponibles")
                with open("papeletas_jueces.xlsx", "rb") as file:
                    st.download_button(
                        label="⬇️ Descargar Papeletas Excel",
                        data=file.read(),
                        file_name="papeletas_jueces.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

def generar_sembrado_tiempo():
    st.markdown("## ⏱️ Generar Sembrado por Tiempo")
    
    st.markdown("""
    <div class="info-message">
        Este proceso ordena todos los nadadores únicamente por tiempo de inscripción, 
        sin importar la categoría de edad. Ideal para competencias open o clasificatorias.
    </div>
    """, unsafe_allow_html=True)
    
    if not os.path.exists("planilla_inscripcion.xlsx"):
        st.markdown("""
        <div class="warning-message">
            ⚠️ No se encontró el archivo <strong>planilla_inscripcion.xlsx</strong>. 
            Por favor, súbelo en la sección "Gestión de Archivos".
        </div>
        """, unsafe_allow_html=True)
        return
    
    try:
        df = pd.read_excel("planilla_inscripcion.xlsx")
        st.success(f"✅ Archivo cargado: {len(df)} nadadores registrados")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🚀 Generar Sembrado por Tiempo", type="primary"):
            with st.spinner("Generando sembrado..."):
                try:
                    #result = subprocess.run([sys.executable, "2-generar_sembrado_por_tiempo.py"],
                    #                      capture_output=True, text=True)
                    script2.main() # Llamar la función directamente
                    
                    #if result.returncode == 0:
                    st.markdown("""
                        <div class="success-message">
                            ✅ <strong>Sembrado por tiempo generado exitosamente!</strong><br>
                            Archivo creado: <code>sembrado_competencia_POR_TIEMPO.xlsx</code>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    #if result.stdout:
                    #    st.text("Output:")
                    #    st.text(result.stdout)
                    
                    #else:
                    #    st.error(f"Error al generar sembrado: {result.stderr}")
                        
                except Exception as e:
                    st.error(f"Error al ejecutar el script: {e}")
    
    with col2:
        if os.path.exists("sembrado_competencia_POR_TIEMPO.xlsx"):
            st.info("📄 Archivo generado disponible para descarga")
            
            with open("sembrado_competencia_POR_TIEMPO.xlsx", "rb") as file:
                st.download_button(
                    label="⬇️ Descargar Sembrado por Tiempo",
                    data=file.read(),
                    file_name="sembrado_competencia_POR_TIEMPO.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            # Sección de papeletas para jueces
            st.markdown("### 📋 Generar Papeletas para Jueces")
            st.info("Las papeletas se generan en formato Excel con rectángulos imprimibles")
            
            if st.button("📄 Generar Papeletas Excel", type="secondary", key="papeletas_excel_tiempo"):
                with st.spinner("Generando papeletas en Excel..."):
                    success, message = papeletas_excel_module.generar_papeletas_excel()
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            
            # Botón de descarga para papeletas Excel si existe
            if os.path.exists("papeletas_jueces.xlsx"):
                st.info("📄 Papeletas Excel disponibles")
                with open("papeletas_jueces.xlsx", "rb") as file:
                    st.download_button(
                        label="⬇️ Descargar Papeletas Excel",
                        data=file.read(),
                        file_name="papeletas_jueces.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

def generate_seeding_excel(df_evento, evento_nombre, tipo_sembrado):
    """
    Genera un archivo Excel con formato de sembrado actualizado con tiempos de competencia
    """
    from io import BytesIO
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    
    wb = Workbook()
    ws = wb.active
    ws.title = f"Sembrado {tipo_sembrado.title()}"
    
    # Título principal
    ws.cell(row=1, column=1, value=evento_nombre).font = Font(bold=True, size=16)
    
    current_row = 3
    current_serie = None
    
    # Procesar por serie
    for _, row in df_evento.iterrows():
        serie_num = row['Serie']
        
        # Nueva serie
        if serie_num != current_serie:
            if current_serie is not None:
                current_row += 1  # Espacio entre series
            
            ws.cell(row=current_row, column=1, value=f"Serie {serie_num}").font = Font(bold=True, size=14)
            current_row += 1
            
            # Headers
            headers = ["Carril", "Nombre", "Equipo", "Edad", "Categoría", "Tiempo Inscripción", "Tiempo Competencia"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=current_row, column=col, value=header)
                cell.font = Font(bold=True)
                if header == "Tiempo Competencia":
                    cell.font = Font(bold=True, color="FF0000")
            current_row += 1
            current_serie = serie_num
        
        # Datos del nadador
        ws.cell(row=current_row, column=1, value=row['Carril'])
        ws.cell(row=current_row, column=2, value=row['Nombre'])
        ws.cell(row=current_row, column=3, value=row['Equipo'])
        ws.cell(row=current_row, column=4, value=row['Edad'])
        ws.cell(row=current_row, column=5, value=row['Categoría'])
        ws.cell(row=current_row, column=6, value=row['Tiempo Inscripción'])
        
        # Tiempo de competencia (editado por el usuario)
        tiempo_comp = row['Tiempo Competencia']
        comp_cell = ws.cell(row=current_row, column=7, value=tiempo_comp if tiempo_comp else "")
        comp_cell.font = Font(color="0000FF")
        
        current_row += 1
    
    # Ajustar ancho de columnas
    ws.column_dimensions['B'].width = 40  # Nombre
    ws.column_dimensions['C'].width = 25  # Equipo
    ws.column_dimensions['F'].width = 18  # Tiempo Inscripción
    ws.column_dimensions['G'].width = 18  # Tiempo Competencia
    
    # Guardar en buffer
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return buffer.getvalue()

def generate_seeding_excel_from_manual(seeding_data, event_name, gender):
    """
    Genera un archivo Excel desde datos de sembrado manual
    """
    from io import BytesIO
    from openpyxl import Workbook
    from openpyxl.styles import Font
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Sembrado Manual"
    
    # Título
    ws.cell(row=1, column=1, value=f"{event_name} - {gender}").font = Font(bold=True, size=16)
    
    current_row = 3
    for serie in seeding_data['series']:
        # Título de serie
        ws.cell(row=current_row, column=1, value=f"Serie {serie['serie']}").font = Font(bold=True, size=14)
        current_row += 1
        
        # Headers
        headers = ["Carril", "Nombre", "Equipo", "Edad", "Categoría", "Tiempo Inscripción", "Tiempo Competencia"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=current_row, column=col, value=header)
            cell.font = Font(bold=True)
            if header == "Tiempo Competencia":
                cell.font = Font(bold=True, color="FF0000")
        current_row += 1
        
        # Datos de carriles
        for lane_idx, swimmer in enumerate(serie['carriles']):
            ws.cell(row=current_row, column=1, value=lane_idx + 1)
            if swimmer:
                ws.cell(row=current_row, column=2, value=swimmer['nombre'])
                ws.cell(row=current_row, column=3, value=swimmer['equipo'])
                ws.cell(row=current_row, column=4, value=swimmer['edad'])
                ws.cell(row=current_row, column=5, value=swimmer['categoria'])
                ws.cell(row=current_row, column=6, value=swimmer['tiempo'])
                # Tiempo competencia vacío para llenar después
                comp_cell = ws.cell(row=current_row, column=7, value="")
                comp_cell.font = Font(color="0000FF")
            current_row += 1
        
        current_row += 1  # Espacio entre series
    
    # Ajustar columnas
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 25
    ws.column_dimensions['F'].width = 18
    ws.column_dimensions['G'].width = 18
    
    # Guardar en buffer
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return buffer.getvalue()

def sembrado_competencia_interface():
    st.markdown("## 📊 Sembrado de Competencia")
    
    st.markdown("""
    <div class="info-message">
        Genera los listados de participantes organizados por series y carriles para la competencia.
        Elige el método de sembrado que mejor se adapte a tu competencia.
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar archivo de inscripciones
    if not os.path.exists("planilla_inscripcion.xlsx"):
        st.markdown("""
        <div class="warning-message">
            ⚠️ No se encontró el archivo <strong>planilla_inscripcion.xlsx</strong>. 
            Por favor, ve a la sección "Inscripción de Nadadores" para registrar participantes.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Verificar si hay sembrados cacheados y mostrar advertencia si puede haber cambios
    cached_seedings = []
    if 'seeding_preview_cat' in st.session_state:
        cached_seedings.append("Por Categorías")
    if 'seeding_preview_time' in st.session_state:
        cached_seedings.append("Por Tiempo")
    if any(key.startswith('manual_seeding_') for key in st.session_state.keys()):
        cached_seedings.append("Manual")
    
    if cached_seedings:
        st.markdown(f"""
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 12px; margin-bottom: 20px;">
            <strong>💡 Recordatorio:</strong> Tienes sembrados cargados ({', '.join(cached_seedings)}). 
            Si agregaste nuevas inscripciones, usa el botón <strong>🔄</strong> para actualizar.
        </div>
        """, unsafe_allow_html=True)
    
    # Pestañas para diferentes métodos de sembrado
    tab1, tab2, tab3 = st.tabs(["📊 Por Categorías", "⏱️ Por Tiempo", "✍️ Manual"])
    
    with tab1:
        st.markdown("### 📊 Sembrado por Categorías")
        st.markdown("""
        **¿Cuándo usar este método?**
        - Competencias federadas o oficiales
        - Eventos con múltiples categorías de edad
        - Cuando se busca competencia equitativa por grupos etarios
        
        **Cómo funciona:**
        - Agrupa nadadores por categoría de edad
        - Ordena por tiempo dentro de cada categoría
        - Coloca los mejores tiempos en las series finales
        """)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🚀 Generar Sembrado por Categorías", type="primary"):
                with st.spinner("Generando sembrado por categorías..."):
                    try:
                        script1.main_full()
                        st.markdown("""
                            <div class="success-message">
                                ✅ <strong>Sembrado generado exitosamente!</strong><br>
                                Archivo creado: <code>sembrado_competencia.xlsx</code>
                            </div>
                            """, unsafe_allow_html=True)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al generar sembrado: {e}")
        
        with col2:
            col_view, col_refresh = st.columns([2, 1])
            with col_view:
                if st.button("👁️ Visualizar Sembrado", help="Ver preview del sembrado antes de descargar"):
                    with st.spinner("Cargando visualización..."):
                        try:
                            seeding_data, message = script1.get_seeding_data()
                            if seeding_data:
                                st.session_state['seeding_preview_cat'] = seeding_data
                                st.success("✅ Visualización cargada")
                            else:
                                st.error(message)
                        except Exception as e:
                            st.error(f"Error al cargar visualización: {e}")
            
            with col_refresh:
                if st.button("🔄", help="Actualizar con nuevas inscripciones"):
                    # Limpiar cache y recargar
                    if 'seeding_preview_cat' in st.session_state:
                        del st.session_state['seeding_preview_cat']
                    with st.spinner("Actualizando sembrado..."):
                        try:
                            seeding_data, message = script1.get_seeding_data()
                            if seeding_data:
                                st.session_state['seeding_preview_cat'] = seeding_data
                                st.success("✅ Sembrado actualizado")
                            else:
                                st.error(message)
                        except Exception as e:
                            st.error(f"Error al actualizar: {e}")
        
        with col3:
            if os.path.exists("sembrado_competencia.xlsx"):
                st.info("📄 Archivo generado disponible para descarga")
                with open("sembrado_competencia.xlsx", "rb") as file:
                    st.download_button(
                        label="⬇️ Descargar Sembrado por Categorías",
                        data=file.read(),
                        file_name="sembrado_competencia.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        # Mostrar visualización del sembrado si está disponible
        if 'seeding_preview_cat' in st.session_state:
            st.markdown("---")
            st.markdown("### 👁️ Vista Previa Editable - Sembrado por Categorías")
            
            seeding_data = st.session_state['seeding_preview_cat']
            
            # Selector de evento para visualizar
            eventos_disponibles = list(seeding_data.keys())
            if eventos_disponibles:
                evento_seleccionado = st.selectbox(
                    "Selecciona un evento para editar:",
                    eventos_disponibles,
                    key="evento_cat_preview"
                )
                
                if evento_seleccionado:
                    st.markdown(f"**{evento_seleccionado}**")
                    
                    # Crear una sola tabla consolidada para todas las series del evento
                    all_carriles_data = []
                    series = seeding_data[evento_seleccionado]['series']
                    
                    for serie in series:
                        for i, nadador in enumerate(serie['carriles'], 1):
                            if nadador:
                                all_carriles_data.append({
                                    "Serie": serie['serie'],
                                    "Carril": i,
                                    "Nombre": nadador['nombre'],
                                    "Equipo": nadador['equipo'],
                                    "Edad": nadador['edad'],
                                    "Categoría": nadador['categoria'],
                                    "Tiempo Inscripción": str(nadador['tiempo_inscripcion']),
                                    "Tiempo Competencia": ""
                                })
                    
                    if all_carriles_data:
                        df_evento = pd.DataFrame(all_carriles_data)
                        
                        # Tabla editable con solo la columna Tiempo Competencia editable
                        edited_df = st.data_editor(
                            df_evento,
                            disabled=["Serie", "Carril", "Nombre", "Equipo", "Edad", "Categoría", "Tiempo Inscripción"],
                            use_container_width=True,
                            hide_index=True,
                            key=f"editor_cat_{evento_seleccionado}"
                        )
                        
                        # Botones de acción
                        col_save, col_download, col_process, col_info = st.columns([1, 1, 1, 1])
                        
                        with col_save:
                            if st.button("💾 Guardar Cambios", type="primary", help="Guardar los tiempos editados"):
                                # Actualizar session_state con los cambios
                                updated_key = f"updated_seeding_cat_{evento_seleccionado}"
                                st.session_state[updated_key] = edited_df
                                st.success("✅ Cambios guardados en memoria")
                        
                        with col_download:
                            if st.button("⬇️ Descargar Excel", help="Descargar archivo Excel con los tiempos actualizados"):
                                # Generar archivo Excel con los datos editados
                                excel_buffer = generate_seeding_excel(edited_df, evento_seleccionado, "categoria")
                                st.download_button(
                                    label="📥 Descargar Sembrado Actualizado",
                                    data=excel_buffer,
                                    file_name=f"sembrado_{evento_seleccionado.replace(' ', '_').replace('-', '_')}_editado.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        
                        with col_process:
                            if st.button("🏆 Procesar a Resultados", help="Convertir a formato de resultados para procesamiento"):
                                # Verificar si hay tiempos de competencia
                                tiempos_comp = [t for t in edited_df["Tiempo Competencia"] if t and t.strip()]
                                if len(tiempos_comp) > 0:
                                    # Guardar archivo temporalmente y procesarlo
                                    temp_file = f"temp_seeding_cat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                                    excel_data = generate_seeding_excel(edited_df, evento_seleccionado, "categoria")
                                    
                                    with open(temp_file, "wb") as f:
                                        f.write(excel_data)
                                    
                                    try:
                                        # Procesar con el script de resultados
                                        import importlib.util
                                        spec = importlib.util.spec_from_file_location("processor", "5-procesar_sembrado_tiempos.py")
                                        processor = importlib.util.module_from_spec(spec)
                                        spec.loader.exec_module(processor)
                                        
                                        success, message = processor.process_seeding_with_times(temp_file)
                                        
                                        if success:
                                            st.success(f"✅ {message}")
                                            st.info("📄 Archivo de resultados disponible en gestión de archivos")
                                        else:
                                            st.error(f"❌ {message}")
                                    
                                    except Exception as e:
                                        st.error(f"❌ Error al procesar: {e}")
                                    
                                    finally:
                                        # Limpiar archivo temporal
                                        if os.path.exists(temp_file):
                                            os.remove(temp_file)
                                else:
                                    st.warning("⚠️ Debes agregar al menos un tiempo de competencia")
                        
                        with col_info:
                            tiempos_completados = len([t for t in edited_df["Tiempo Competencia"] if t and t.strip()])
                            total_nadadores = len([n for n in edited_df["Nombre"] if n != "---"])
                            st.info(f"⏱️ Tiempos: {tiempos_completados}/{total_nadadores}")
    
    with tab2:
        st.markdown("### ⏱️ Sembrado por Tiempo")
        st.markdown("""
        **¿Cuándo usar este método?**
        - Competencias de clasificación o qualifiers
        - Eventos abiertos sin restricción de edad
        - Búsqueda de récords o marcas específicas
        
        **Cómo funciona:**
        - Ignora las categorías de edad
        - Ordena todos los nadadores por tiempo de inscripción
        - Series más rápidas al final del evento
        """)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🚀 Generar Sembrado por Tiempo", type="primary", key="gen_tiempo"):
                with st.spinner("Generando sembrado por tiempo..."):
                    try:
                        script2.main()
                        st.markdown("""
                            <div class="success-message">
                                ✅ <strong>Sembrado generado exitosamente!</strong><br>
                                Archivo creado: <code>sembrado_competencia_POR_TIEMPO.xlsx</code>
                            </div>
                            """, unsafe_allow_html=True)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al generar sembrado: {e}")
        
        with col2:
            col_view, col_refresh = st.columns([2, 1])
            with col_view:
                if st.button("👁️ Visualizar Sembrado", help="Ver preview del sembrado antes de descargar", key="view_tiempo"):
                    with st.spinner("Cargando visualización..."):
                        try:
                            seeding_data, message = script2.get_seeding_data()
                            if seeding_data:
                                st.session_state['seeding_preview_time'] = seeding_data
                                st.success("✅ Visualización cargada")
                            else:
                                st.error(message)
                        except Exception as e:
                            st.error(f"Error al cargar visualización: {e}")
            
            with col_refresh:
                if st.button("🔄", key="refresh_time", help="Actualizar con nuevas inscripciones"):
                    # Limpiar cache y recargar
                    if 'seeding_preview_time' in st.session_state:
                        del st.session_state['seeding_preview_time']
                    with st.spinner("Actualizando sembrado..."):
                        try:
                            seeding_data, message = script2.get_seeding_data()
                            if seeding_data:
                                st.session_state['seeding_preview_time'] = seeding_data
                                st.success("✅ Sembrado actualizado")
                            else:
                                st.error(message)
                        except Exception as e:
                            st.error(f"Error al actualizar: {e}")
        
        with col3:
            if os.path.exists("sembrado_competencia_POR_TIEMPO.xlsx"):
                st.info("📄 Archivo generado disponible para descarga")
                with open("sembrado_competencia_POR_TIEMPO.xlsx", "rb") as file:
                    st.download_button(
                        label="⬇️ Descargar Sembrado por Tiempo",
                        data=file.read(),
                        file_name="sembrado_competencia_POR_TIEMPO.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        # Mostrar visualización del sembrado si está disponible
        if 'seeding_preview_time' in st.session_state:
            st.markdown("---")
            st.markdown("### 👁️ Vista Previa Editable - Sembrado por Tiempo")
            
            seeding_data = st.session_state['seeding_preview_time']
            
            # Selector de evento para visualizar
            eventos_disponibles = list(seeding_data.keys())
            if eventos_disponibles:
                evento_seleccionado = st.selectbox(
                    "Selecciona un evento para editar:",
                    eventos_disponibles,
                    key="evento_time_preview"
                )
                
                if evento_seleccionado:
                    st.markdown(f"**{evento_seleccionado}**")
                    
                    # Crear una sola tabla consolidada para todas las series del evento
                    all_carriles_data = []
                    series = seeding_data[evento_seleccionado]['series']
                    
                    for serie in series:
                        for i, nadador in enumerate(serie['carriles'], 1):
                            if nadador:
                                all_carriles_data.append({
                                    "Serie": serie['serie'],
                                    "Carril": i,
                                    "Nombre": nadador['nombre'],
                                    "Equipo": nadador['equipo'],
                                    "Edad": nadador['edad'],
                                    "Categoría": nadador['categoria'],
                                    "Tiempo Inscripción": str(nadador['tiempo_inscripcion']),
                                    "Tiempo Competencia": ""
                                })
                    
                    if all_carriles_data:
                        df_evento = pd.DataFrame(all_carriles_data)
                        
                        # Tabla editable con solo la columna Tiempo Competencia editable
                        edited_df = st.data_editor(
                            df_evento,
                            disabled=["Serie", "Carril", "Nombre", "Equipo", "Edad", "Categoría", "Tiempo Inscripción"],
                            use_container_width=True,
                            hide_index=True,
                            key=f"editor_time_{evento_seleccionado}"
                        )
                        
                        # Botones de acción
                        col_save, col_download, col_process, col_info = st.columns([1, 1, 1, 1])
                        
                        with col_save:
                            if st.button("💾 Guardar Cambios", type="primary", help="Guardar los tiempos editados", key="save_time"):
                                # Actualizar session_state con los cambios
                                updated_key = f"updated_seeding_time_{evento_seleccionado}"
                                st.session_state[updated_key] = edited_df
                                st.success("✅ Cambios guardados en memoria")
                        
                        with col_download:
                            if st.button("⬇️ Descargar Excel", help="Descargar archivo Excel con los tiempos actualizados", key="download_time"):
                                # Generar archivo Excel con los datos editados
                                excel_buffer = generate_seeding_excel(edited_df, evento_seleccionado, "tiempo")
                                st.download_button(
                                    label="📥 Descargar Sembrado Actualizado",
                                    data=excel_buffer,
                                    file_name=f"sembrado_{evento_seleccionado.replace(' ', '_').replace('-', '_')}_editado.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="dl_time"
                                )
                        
                        with col_process:
                            if st.button("🏆 Procesar a Resultados", help="Convertir a formato de resultados para procesamiento", key="process_time"):
                                # Verificar si hay tiempos de competencia
                                tiempos_comp = [t for t in edited_df["Tiempo Competencia"] if t and t.strip()]
                                if len(tiempos_comp) > 0:
                                    # Guardar archivo temporalmente y procesarlo
                                    temp_file = f"temp_seeding_time_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                                    excel_data = generate_seeding_excel(edited_df, evento_seleccionado, "tiempo")
                                    
                                    with open(temp_file, "wb") as f:
                                        f.write(excel_data)
                                    
                                    try:
                                        # Procesar con el script de resultados
                                        import importlib.util
                                        spec = importlib.util.spec_from_file_location("processor", "5-procesar_sembrado_tiempos.py")
                                        processor = importlib.util.module_from_spec(spec)
                                        spec.loader.exec_module(processor)
                                        
                                        success, message = processor.process_seeding_with_times(temp_file)
                                        
                                        if success:
                                            st.success(f"✅ {message}")
                                            st.info("📄 Archivo de resultados disponible en gestión de archivos")
                                        else:
                                            st.error(f"❌ {message}")
                                    
                                    except Exception as e:
                                        st.error(f"❌ Error al procesar: {e}")
                                    
                                    finally:
                                        # Limpiar archivo temporal
                                        if os.path.exists(temp_file):
                                            os.remove(temp_file)
                                else:
                                    st.warning("⚠️ Debes agregar al menos un tiempo de competencia")
                        
                        with col_info:
                            tiempos_completados = len([t for t in edited_df["Tiempo Competencia"] if t and t.strip()])
                            total_nadadores = len([n for n in edited_df["Nombre"] if n != "---"])
                            st.info(f"⏱️ Tiempos: {tiempos_completados}/{total_nadadores}")
        
    
    with tab3:
        st.markdown("### ✍️ Sembrado Manual")
        st.markdown("""
        **Crea sembrados personalizados con total control:**
        - 🎯 Arrastra nadadores entre carriles y series
        - 🔄 Combina diferentes categorías  
        - 📊 Vista en tiempo real del sembrado
        - 💾 Guarda tu organización personalizada
        """)
        
        # Verificar si hay inscripciones
        if not os.path.exists("planilla_inscripcion.xlsx"):
            st.warning("⚠️ Necesitas tener nadadores inscritos para crear un sembrado manual.")
            st.info("👉 Ve a la sección **Inscripción de Nadadores** para registrar participantes primero.")
            return
        
        try:
            # Cargar datos de inscripción
            df = pd.read_excel("planilla_inscripcion.xlsx")
            info_cols = ['NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO']
            event_cols = [col for col in df.columns if col not in info_cols and 'Nø' not in col and 'FECHA DE NA' not in col]
            
            if len(event_cols) == 0:
                st.error("❌ No se encontraron eventos en la planilla de inscripción")
                return
                
        except Exception as e:
            st.error(f"❌ Error al leer inscripciones: {e}")
            return
        
        # Selector de evento
        st.markdown("#### 📋 Seleccionar Evento")
        col_event, col_gender = st.columns([2, 1])
        
        with col_event:
            selected_event = st.selectbox(
                "Selecciona el evento para crear sembrado manual:",
                event_cols,
                key="manual_event_select"
            )
        
        with col_gender:
            gender_filter = st.selectbox(
                "Género:",
                ["Todos", "Masculino", "Femenino"],
                key="manual_gender_filter"
            )
        
        if selected_event:
            # Filtrar nadadores para el evento seleccionado
            swimmers_for_event = []
            for index, row in df.iterrows():
                if pd.notna(row[selected_event]) and pd.notna(row['NOMBRE Y AP']):
                    swimmer_gender = "Masculino" if row['SEXO'].upper() == 'M' else "Femenino"
                    if gender_filter == "Todos" or gender_filter == swimmer_gender:
                        swimmers_for_event.append({
                            'id': index,
                            'nombre': row['NOMBRE Y AP'],
                            'equipo': row['EQUIPO'],
                            'edad': row['EDAD'],
                            'categoria': row['CAT.'],
                            'sexo': swimmer_gender,
                            'tiempo': str(row[selected_event])
                        })
            
            if len(swimmers_for_event) == 0:
                st.warning(f"⚠️ No hay nadadores inscritos en {selected_event} con el filtro seleccionado")
                return
            
            st.success(f"✅ {len(swimmers_for_event)} nadadores encontrados en **{selected_event}**")
            
            # Botón para actualizar sembrado con nuevas inscripciones
            col_refresh, col_info = st.columns([1, 3])
            with col_refresh:
                if st.button("🔄 Actualizar Sembrado", help="Cargar nuevas inscripciones"):
                    seeding_key = f"manual_seeding_{selected_event}_{gender_filter}"
                    if seeding_key in st.session_state:
                        del st.session_state[seeding_key]
                    st.rerun()
            
            with col_info:
                st.info("💡 Usa 'Actualizar Sembrado' si agregaste nuevas inscripciones")

            # Inicializar sembrado en session state
            seeding_key = f"manual_seeding_{selected_event}_{gender_filter}"
            
            def create_initial_seeding(swimmers_list):
                """Crear sembrado inicial automático"""
                sorted_swimmers = sorted(swimmers_list, key=lambda x: float('inf') if x['tiempo'] == 'nan' else float(x['tiempo'].replace(':', '').replace('.', '')) if ':' in x['tiempo'] else float(x['tiempo']) if x['tiempo'].replace('.', '').isdigit() else float('inf'))
                
                # Distribución en series de 8 carriles
                series = []
                swimmers_per_series = 8
                num_series = (len(sorted_swimmers) + swimmers_per_series - 1) // swimmers_per_series
                
                for serie_num in range(num_series):
                    serie_swimmers = sorted_swimmers[serie_num * swimmers_per_series:(serie_num + 1) * swimmers_per_series]
                    lane_assignment = [4, 5, 3, 6, 2, 7, 1, 8]  # Orden standard de carriles
                    
                    serie = {"serie": serie_num + 1, "carriles": [None] * 8}
                    for i, swimmer in enumerate(serie_swimmers):
                        if i < len(lane_assignment):
                            lane_idx = lane_assignment[i] - 1
                            serie["carriles"][lane_idx] = swimmer
                    
                    series.append(serie)
                
                return {
                    'evento': selected_event,
                    'genero': gender_filter, 
                    'series': series,
                    'nadadores_disponibles': [],
                    'total_nadadores': len(swimmers_list)  # Para detectar cambios
                }
            
            # Verificar si necesita actualización automática
            if seeding_key not in st.session_state:
                st.session_state[seeding_key] = create_initial_seeding(swimmers_for_event)
            else:
                # Verificar si el número de nadadores cambió
                current_total = st.session_state[seeding_key].get('total_nadadores', 0)
                if current_total != len(swimmers_for_event):
                    st.warning(f"⚠️ Se detectaron {len(swimmers_for_event) - current_total} nuevas inscripciones. Usa 'Actualizar Sembrado' para cargarlas.")
            
            seeding_data = st.session_state[seeding_key]
            
            # Interfaz de edición manual
            st.markdown("#### 🎯 Editor de Sembrado Manual")
            
            # Mostrar nadadores disponibles (no asignados)
            if seeding_data['nadadores_disponibles']:
                st.markdown("##### 👥 Nadadores Disponibles")
                cols_available = st.columns(min(len(seeding_data['nadadores_disponibles']), 4))
                category_colors = {
                    'MENORES': '#FFB6C1',  'JUVENIL A': '#87CEEB',  'JUVENIL B': '#98FB98',
                    'JUNIOR': '#DDA0DD',    'SENIOR': '#F0E68C',    'MASTER': '#FFA07A'
                }
                for i, swimmer in enumerate(seeding_data['nadadores_disponibles']):
                    with cols_available[i % 4]:
                        bg_color = category_colors.get(swimmer['categoria'], '#E6E6FA')
                        st.markdown(f"""
                        <div style="background-color: {bg_color}; padding: 6px; border-radius: 4px; border: 1px solid #ccc; margin: 2px 0;">
                            <strong>{swimmer['nombre']}</strong><br>
                            <small>{swimmer['equipo']} - {swimmer['categoria']}</small>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Leyenda de colores
            st.markdown("##### 🎨 Leyenda de Categorías")
            category_colors = {
                'MENORES': '#FFB6C1',  'JUVENIL A': '#87CEEB',  'JUVENIL B': '#98FB98',
                'JUNIOR': '#DDA0DD',    'SENIOR': '#F0E68C',    'MASTER': '#FFA07A'
            }
            
            legend_cols = st.columns(len(category_colors))
            for i, (cat, color) in enumerate(category_colors.items()):
                with legend_cols[i]:
                    st.markdown(f"""
                    <div style="background-color: {color}; padding: 4px; border-radius: 3px; text-align: center; border: 1px solid #ccc;">
                        <small><strong>{cat}</strong></small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Editor por series
            st.markdown("##### 🏊 Series y Carriles")
            
            for serie_idx, serie in enumerate(seeding_data['series']):
                st.markdown(f"**Serie {serie['serie']}**")
                
                # Crear columnas para los 8 carriles
                lane_cols = st.columns(8)
                
                for lane_idx in range(8):
                    with lane_cols[lane_idx]:
                        st.markdown(f"**Carril {lane_idx + 1}**")
                        
                        current_swimmer = serie['carriles'][lane_idx]
                        
                        if current_swimmer:
                            # Mostrar nadador actual con color por categoría
                            category_colors = {
                                'MENORES': '#FFB6C1',  # Rosa claro
                                'JUVENIL A': '#87CEEB',  # Azul cielo
                                'JUVENIL B': '#98FB98',  # Verde claro
                                'JUNIOR': '#DDA0DD',    # Violeta claro
                                'SENIOR': '#F0E68C',    # Amarillo claro
                                'MASTER': '#FFA07A'     # Salmón
                            }
                            bg_color = category_colors.get(current_swimmer['categoria'], '#E6E6FA')
                            
                            st.markdown(f"""
                            <div style="background-color: {bg_color}; padding: 8px; border-radius: 5px; border: 1px solid #ccc; margin: 2px 0;">
                                <strong>{current_swimmer['nombre']}</strong><br>
                                <small>{current_swimmer['equipo']} | {current_swimmer['categoria']}<br>
                                Tiempo: {current_swimmer['tiempo']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Botón para remover nadador
                            if st.button("❌", key=f"remove_{serie_idx}_{lane_idx}", help="Remover nadador"):
                                # Mover a disponibles
                                seeding_data['nadadores_disponibles'].append(current_swimmer)
                                seeding_data['series'][serie_idx]['carriles'][lane_idx] = None
                                st.rerun()
                        else:
                            # Carril vacío - mostrar opciones para asignar
                            st.info("🔘 Carril vacío")
                            
                            # Crear lista de nadadores para asignar
                            available_swimmers = seeding_data['nadadores_disponibles'].copy()
                            
                            # Agregar nadadores de otros carriles para intercambio
                            for s_idx, s in enumerate(seeding_data['series']):
                                for l_idx, swimmer in enumerate(s['carriles']):
                                    if swimmer and not (s_idx == serie_idx and l_idx == lane_idx):
                                        available_swimmers.append({**swimmer, '_from_serie': s_idx, '_from_lane': l_idx})
                            
                            if available_swimmers:
                                swimmer_options = ["Seleccionar nadador..."] + [
                                    f"{swimmer['nombre']} ({swimmer['equipo']} - {swimmer['categoria']})" 
                                    for swimmer in available_swimmers
                                ]
                                
                                selected_swimmer_idx = st.selectbox(
                                    "Asignar:",
                                    range(len(swimmer_options)),
                                    format_func=lambda x: swimmer_options[x],
                                    key=f"assign_{serie_idx}_{lane_idx}"
                                )
                                
                                if selected_swimmer_idx > 0:
                                    selected_swimmer = available_swimmers[selected_swimmer_idx - 1]
                                    
                                    if st.button("✅ Asignar", key=f"confirm_{serie_idx}_{lane_idx}"):
                                        # Asignar nadador al carril
                                        if '_from_serie' in selected_swimmer:
                                            # Mover de otro carril (intercambio)
                                            from_serie = selected_swimmer['_from_serie']
                                            from_lane = selected_swimmer['_from_lane']
                                            clean_swimmer = {k: v for k, v in selected_swimmer.items() if not k.startswith('_')}
                                            
                                            seeding_data['series'][serie_idx]['carriles'][lane_idx] = clean_swimmer
                                            seeding_data['series'][from_serie]['carriles'][from_lane] = None
                                        else:
                                            # Mover de disponibles
                                            seeding_data['series'][serie_idx]['carriles'][lane_idx] = selected_swimmer
                                            seeding_data['nadadores_disponibles'].remove(selected_swimmer)
                                        
                                        st.rerun()
                
                st.markdown("---")
            
            # Controles adicionales
            st.markdown("#### ⚙️ Controles Avanzados")
            col_add_series, col_category_info = st.columns([1, 2])
            
            with col_add_series:
                col_add, col_remove = st.columns([1, 1])
                with col_add:
                    if st.button("➕ Nueva Serie"):
                        new_serie_num = len(seeding_data['series']) + 1
                        new_serie = {"serie": new_serie_num, "carriles": [None] * 8}
                        seeding_data['series'].append(new_serie)
                        st.rerun()
                
                with col_remove:
                    if len(seeding_data['series']) > 1:
                        if st.button("🗑️ Eliminar Serie", help="Eliminar última serie vacía"):
                            # Verificar si la última serie está vacía
                            last_serie = seeding_data['series'][-1]
                            if all(swimmer is None for swimmer in last_serie['carriles']):
                                seeding_data['series'].pop()
                                st.rerun()
                            else:
                                st.error("❌ Solo se pueden eliminar series vacías")
            
            with col_category_info:
                # Mostrar distribución de categorías
                categories_in_seeding = {}
                total_swimmers = 0
                for serie in seeding_data['series']:
                    for swimmer in serie['carriles']:
                        if swimmer:
                            cat = swimmer['categoria']
                            categories_in_seeding[cat] = categories_in_seeding.get(cat, 0) + 1
                            total_swimmers += 1
                
                if categories_in_seeding:
                    st.info(f"📊 **Nadadores por categoría:** " + 
                           ", ".join([f"{cat}: {count}" for cat, count in sorted(categories_in_seeding.items())]) +
                           f" | **Total: {total_swimmers}**")
            
            # Botones de acción
            st.markdown("#### 💾 Acciones")
            col_save, col_download, col_reset = st.columns([1, 1, 1])
            
            with col_save:
                if st.button("💾 Guardar Sembrado", type="primary"):
                    # Generar archivo Excel con sembrado manual
                    manual_filename = f"sembrado_manual_{selected_event}_{gender_filter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    
                    wb = Workbook()
                    ws = wb.active
                    ws.title = "Sembrado Manual"
                    
                    # Título
                    ws.cell(row=1, column=1, value=f"{selected_event} - {gender_filter}").font = Font(bold=True, size=16)
                    
                    current_row = 3
                    for serie in seeding_data['series']:
                        # Título de serie
                        ws.cell(row=current_row, column=1, value=f"Serie {serie['serie']}").font = Font(bold=True, size=14)
                        current_row += 1
                        
                        # Headers
                        headers = ["Carril", "Nombre", "Equipo", "Edad", "Categoría", "Tiempo Inscripción", "Tiempo Competencia"]
                        for col, header in enumerate(headers, 1):
                            cell = ws.cell(row=current_row, column=col, value=header)
                            cell.font = Font(bold=True)
                            if header == "Tiempo Competencia":
                                cell.font = Font(bold=True, color="FF0000")
                        current_row += 1
                        
                        # Datos de carriles
                        for lane_idx, swimmer in enumerate(serie['carriles']):
                            ws.cell(row=current_row, column=1, value=lane_idx + 1)
                            if swimmer:
                                ws.cell(row=current_row, column=2, value=swimmer['nombre'])
                                ws.cell(row=current_row, column=3, value=swimmer['equipo'])
                                ws.cell(row=current_row, column=4, value=swimmer['edad'])
                                ws.cell(row=current_row, column=5, value=swimmer['categoria'])
                                ws.cell(row=current_row, column=6, value=swimmer['tiempo'])
                                comp_cell = ws.cell(row=current_row, column=7, value="")
                                comp_cell.font = Font(color="0000FF")
                            current_row += 1
                        
                        current_row += 1  # Espacio entre series
                    
                    # Ajustar columnas
                    ws.column_dimensions['B'].width = 30
                    ws.column_dimensions['C'].width = 25
                    ws.column_dimensions['F'].width = 18
                    ws.column_dimensions['G'].width = 18
                    
                    wb.save(manual_filename)
                    st.success(f"✅ Sembrado manual guardado: {manual_filename}")
            
            with col_download:
                if st.button("⬇️ Descargar Excel"):
                    # Crear archivo temporal para descarga
                    manual_buffer = generate_seeding_excel_from_manual(seeding_data, selected_event, gender_filter)
                    st.download_button(
                        label="📥 Descargar Sembrado Manual",
                        data=manual_buffer,
                        file_name=f"sembrado_manual_{selected_event}_{gender_filter}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col_reset:
                if st.button("🔄 Resetear", help="Volver al sembrado automático inicial"):
                    if seeding_key in st.session_state:
                        del st.session_state[seeding_key]
                    st.rerun()
    
    # Sección de limpieza de sembrados
    st.markdown("---")
    st.markdown("### 🧹 Limpiar Sembrados")
    
    col_clean_sem1, col_clean_sem2, col_clean_sem3 = st.columns([2, 1, 1])
    
    with col_clean_sem1:
        st.info("🗑️ Eliminar archivos de sembrado para generar nuevos")
    
    with col_clean_sem2:
        if st.button("📊 Limpiar Por Categoría", help="Eliminar sembrado por categoría"):
            if os.path.exists("sembrado_competencia.xlsx"):
                try:
                    os.remove("sembrado_competencia.xlsx")
                    # Limpiar session state relacionado
                    if 'seeding_preview_cat' in st.session_state:
                        del st.session_state['seeding_preview_cat']
                    st.success("✅ Sembrado por categoría eliminado")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.info("ℹ️ No hay sembrado por categoría")
    
    with col_clean_sem3:
        if st.button("⏱️ Limpiar Por Tiempo", help="Eliminar sembrado por tiempo"):
            if os.path.exists("sembrado_competencia_POR_TIEMPO.xlsx"):
                try:
                    os.remove("sembrado_competencia_POR_TIEMPO.xlsx")
                    # Limpiar session state relacionado
                    if 'seeding_preview_time' in st.session_state:
                        del st.session_state['seeding_preview_time']
                    st.success("✅ Sembrado por tiempo eliminado")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.info("ℹ️ No hay sembrado por tiempo")

def procesar_resultados():
    st.markdown("## 🏆 Procesar Resultados")
    
    st.markdown("""
    <div class="info-message">
        Procesa los resultados finales de la competencia y genera reportes de premiación 
        con sistema de puntos y clasificaciones por categoría y equipos.
    </div>
    """, unsafe_allow_html=True)
    
    if not os.path.exists("resultados_con_tiempos.xlsx"):
        st.markdown("""
        <div class="warning-message">
            ⚠️ No se encontró el archivo <strong>resultados_con_tiempos.xlsx</strong>. 
            Por favor, súbelo en la sección "Gestión de Archivos".
        </div>
        """, unsafe_allow_html=True)
        return
    
    try:
        df = pd.read_excel("resultados_con_tiempos.xlsx", header=None)
        st.success("✅ Archivo de resultados cargado correctamente")
    except Exception as e:
        st.error(f"Error al leer el archivo de resultados: {e}")
        return
    
    # Mostrar sistema de puntos
    st.markdown("### 🎯 Sistema de Puntos")
    puntos_df = pd.DataFrame({
        'Posición': [1, 2, 3, 4, 5, 6, 7, 8],
        'Puntos': [9, 7, 6, 5, 4, 3, 2, 1]
    })
    st.dataframe(puntos_df, use_container_width=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🚀 Procesar Resultados", type="primary"):
            with st.spinner("Procesando resultados..."):
                try:
                    #result = subprocess.run([sys.executable, "3-procesar_resultados.py"],
                    #                      capture_output=True, text=True)
                    script3.main_full() # Llamar la función directamente
                    
                    #if result.returncode == 0:
                    st.markdown("""
                        <div class="success-message">
                            ✅ <strong>Resultados procesados exitosamente!</strong><br>
                            Archivo creado: <code>reporte_premiacion_final_CORREGIDO.xlsx</code>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    #if result.stdout:
                    #    st.text("Output:")
                    #    st.text(result.stdout)
                    
                    #else:
                    #    st.error(f"Error al procesar resultados: {result.stderr}")
                        
                except Exception as e:
                    st.error(f"Error al ejecutar el script: {e}")
    
    with col2:
        if os.path.exists("reporte_premiacion_final_CORREGIDO.xlsx"):
            st.info("📄 Reporte de premiación disponible para descarga")
            
            with open("reporte_premiacion_final_CORREGIDO.xlsx", "rb") as file:
                st.download_button(
                    label="⬇️ Descargar Reporte de Premiación",
                    data=file.read(),
                    file_name="reporte_premiacion_final_CORREGIDO.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    # Sección de limpieza de resultados
    st.markdown("---")
    st.markdown("### 🧹 Limpiar Resultados")
    
    col_clean_res1, col_clean_res2, col_clean_res3 = st.columns([2, 1, 1])
    
    with col_clean_res1:
        st.info("🗑️ Eliminar archivos de resultados y reportes")
    
    with col_clean_res2:
        if st.button("🏆 Limpiar Resultados", help="Eliminar archivo de resultados de competencia"):
            files_to_clean = ["resultados_con_tiempos.xlsx"]
            import glob
            dynamic_results = glob.glob("resultados_desde_sembrado_*.xlsx")
            files_to_clean.extend(dynamic_results)
            
            deleted = []
            for file in files_to_clean:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                        deleted.append(file)
                    except Exception as e:
                        st.error(f"❌ Error eliminando {file}: {e}")
            
            if deleted:
                st.success(f"✅ Eliminados: {', '.join(deleted)}")
                st.rerun()
            else:
                st.info("ℹ️ No hay resultados que eliminar")
    
    with col_clean_res3:
        if st.button("🏅 Limpiar Reportes", help="Eliminar reporte de premiación"):
            if os.path.exists("reporte_premiacion_final_CORREGIDO.xlsx"):
                try:
                    os.remove("reporte_premiacion_final_CORREGIDO.xlsx")
                    st.success("✅ Reporte de premiación eliminado")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.info("ℹ️ No hay reporte que eliminar")

def generar_papeletas_interface():
    """Interfaz independiente para generar papeletas PDF y Excel con vista previa"""
    st.markdown("## 📋 Generar Papeletas para Jueces")
    
    st.markdown("""
    <div class="info-message">
        <p>Genera papeletas <strong>individuales por nadador</strong> para que los jueces registren los tiempos durante la competencia.</p>
        <p><strong>Requisito:</strong> Debes tener el archivo de inscripción cargado.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar archivo de entrada
    if not os.path.exists("planilla_inscripcion.xlsx"):
        st.markdown("""
        <div class="warning-message">
            ⚠️ No se encontró el archivo <strong>planilla_inscripcion.xlsx</strong>. 
            Por favor, súbelo en la sección "Gestión de Archivos" o registra nadadores primero.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Leer y mostrar vista previa de papeletas
    try:
        papeletas_data = papeletas_excel_module.leer_datos_sembrado()
        if not papeletas_data:
            st.error("No se encontraron datos del sembrado")
            return
        
        st.success(f"✅ Se generarán {len(papeletas_data)} papeletas individuales")
        
        # Vista previa de papeletas
        st.markdown("### 👁️ Vista Previa de Papeletas")
        
        # Navegador de papeletas
        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
        
        with col_nav2:
            # Selector de papeleta
            papeleta_index = st.selectbox(
                f"Selecciona papeleta (1-{len(papeletas_data)}):",
                range(len(papeletas_data)),
                format_func=lambda x: f"Papeleta {x+1}: {papeletas_data[x]['nombre']} - {papeletas_data[x]['prueba'].split(' - ')[0]}",
                key="papeleta_selector"
            )
        
        with col_nav1:
            if st.button("⬅️ Anterior", disabled=(papeleta_index == 0)):
                if papeleta_index > 0:
                    st.session_state.papeleta_selector = papeleta_index - 1
                    st.rerun()
        
        with col_nav3:
            if st.button("Siguiente ➡️", disabled=(papeleta_index == len(papeletas_data)-1)):
                if papeleta_index < len(papeletas_data)-1:
                    st.session_state.papeleta_selector = papeleta_index + 1
                    st.rerun()
        
        # Mostrar papeleta seleccionada
        nadador_actual = papeletas_data[papeleta_index]
        
        st.markdown(f"""
        <div style="border: 3px solid #1E88E5; padding: 25px; margin: 20px 0; border-radius: 12px; background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%); box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="text-align: center; font-weight: bold; font-size: 18px; color: #1E88E5; margin-bottom: 15px; border-bottom: 2px solid #1E88E5; padding-bottom: 10px;">
                PRUEBA: {nadador_actual['prueba']}
            </div>
            
            <div style="text-align: center; font-size: 14px; margin-bottom: 20px; background-color: rgba(255,255,255,0.7); padding: 10px; border-radius: 8px;">
                <strong>{nadador_actual['nombre']}</strong> - {nadador_actual['equipo']} - {nadador_actual['categoria']}
            </div>
            
            <div style="display: flex; justify-content: space-around; margin-bottom: 25px; background-color: rgba(255,255,255,0.5); padding: 15px; border-radius: 8px;">
                <div style="text-align: center;">
                    <div style="font-weight: bold; font-size: 12px; margin-bottom: 5px;">SERIE:</div>
                    <div style="border: 2px solid #333; padding: 8px 15px; background-color: #e8f5e8; font-size: 14px; font-weight: bold;">{nadador_actual['serie']}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-weight: bold; font-size: 12px; margin-bottom: 5px;">CARRIL:</div>
                    <div style="border: 2px solid #333; padding: 8px 15px; background-color: #e8f5e8; font-size: 14px; font-weight: bold;">{nadador_actual['carril']}</div>
                </div>
            </div>
            
            <div style="text-align: center; font-weight: bold; font-size: 20px; color: #FF0000; margin-bottom: 20px; text-transform: uppercase;">
                TIEMPO DE COMPETENCIA:
            </div>
            
            <div style="text-align: center; font-weight: bold; font-size: 28px; border: 4px solid #000; padding: 20px; background-color: #fff; border-radius: 8px; letter-spacing: 3px; font-family: 'Courier New', monospace;">
                _____ : _____ . _____
            </div>
            
            <div style="margin-top: 20px; font-size: 10px; color: #666; border-top: 1px solid #ccc; padding-top: 10px;">
                <div style="margin-bottom: 5px;">Juez: ________________________________</div>
                <div>Fecha: ______________    Hora: ______________</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Información adicional de la papeleta actual
        col_info1, col_info2, col_info3, col_info4 = st.columns(4)
        with col_info1:
            st.metric("Papeleta", f"{papeleta_index + 1} de {len(papeletas_data)}")
        with col_info2:
            st.metric("Serie Asignada", f"{nadador_actual['serie']}")
        with col_info3:
            st.metric("Carril Asignado", f"{nadador_actual['carril']}")
        with col_info4:
            st.metric("Tiempo Inscripción", f"{nadador_actual['tiempo_inscripcion']}")
        
        # Botón para vista rápida de impresión
        if st.button("🖨️ Vista de Impresión", key="print_preview"):
            st.markdown("### Vista de Impresión - Tamaño Real")
            st.markdown(f"""
            <div style="width: 21cm; border: 1px solid #000; padding: 1cm; margin: 0 auto; background: white; font-family: Arial, sans-serif;">
                <div style="text-align: center; font-size: 20px; font-weight: bold; color: #1E88E5; margin-bottom: 1cm; border-bottom: 2px solid #1E88E5; padding-bottom: 0.5cm;">
                    PRUEBA: {nadador_actual['prueba']}
                </div>
                
                <div style="text-align: center; font-size: 16px; margin-bottom: 1.5cm;">
                    <strong>{nadador_actual['nombre']}</strong> - {nadador_actual['equipo']} - {nadador_actual['categoria']}
                </div>
                
                <div style="display: flex; justify-content: space-around; margin-bottom: 2cm;">
                    <div style="text-align: center;">
                        <div style="font-size: 14px; margin-bottom: 0.5cm;">SERIE:</div>
                        <div style="border: 3px solid #000; padding: 1cm 2cm; font-size: 18px;">______</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 14px; margin-bottom: 0.5cm;">CARRIL:</div>
                        <div style="border: 3px solid #000; padding: 1cm 2cm; font-size: 18px;">______</div>
                    </div>
                </div>
                
                <div style="text-align: center; font-size: 24px; font-weight: bold; color: #FF0000; margin-bottom: 1.5cm;">
                    TIEMPO DE COMPETENCIA:
                </div>
                
                <div style="text-align: center; font-size: 36px; font-weight: bold; border: 4px solid #000; padding: 1.5cm; background: #f9f9f9; letter-spacing: 5px;">
                    _____ : _____ . _____
                </div>
                
                <div style="margin-top: 2cm; font-size: 12px; color: #666;">
                    <div style="margin-bottom: 1cm;">Juez: ________________________________</div>
                    <div>Fecha: ______________    Hora: ______________</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("*Esta vista simula el tamaño real de impresión*")
        
        # Lista compacta de todas las papeletas
        with st.expander(f"📊 Ver lista completa ({len(papeletas_data)} papeletas)"):
            df_preview = pd.DataFrame(papeletas_data)
            st.dataframe(
                df_preview[['nombre', 'prueba', 'equipo', 'categoria', 'tiempo_inscripcion']], 
                use_container_width=True,
                hide_index=True
            )
        
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return
    
    st.markdown("---")
    
    # Dos columnas para las dos opciones de generación
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Papeletas PDF")
        st.info("Formato: Una papeleta por página en orientación horizontal")
        
        if st.button("🚀 Generar Papeletas PDF", type="primary", key="gen_pdf"):
            with st.spinner("Generando papeletas PDF..."):
                try:
                    success, message = papeletas_pdf_module.generar_papeletas_pdf()
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                except Exception as e:
                    st.error(f"Error al generar papeletas PDF: {e}")
        
        # Descarga PDF
        if os.path.exists("papeletas_jueces.pdf"):
            with open("papeletas_jueces.pdf", "rb") as file:
                st.download_button(
                    label="⬇️ Descargar Papeletas PDF",
                    data=file.read(),
                    file_name="papeletas_jueces.pdf",
                    mime="application/pdf",
                    key="download_pdf"
                )
    
    with col2:
        st.markdown("### 📊 Papeletas Excel") 
        st.info("Formato: Rectángulos individuales por nadador, ideal para recortar")
        
        if st.button("🚀 Generar Papeletas Excel", type="primary", key="gen_excel"):
            with st.spinner("Generando papeletas Excel..."):
                try:
                    success, message = papeletas_excel_module.generar_papeletas_excel()
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                except Exception as e:
                    st.error(f"Error al generar papeletas Excel: {e}")
        
        # Descarga Excel
        if os.path.exists("papeletas_jueces.xlsx"):
            with open("papeletas_jueces.xlsx", "rb") as file:
                st.download_button(
                    label="⬇️ Descargar Papeletas Excel",
                    data=file.read(),
                    file_name="papeletas_jueces.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel"
                )

def gestion_archivos():
    st.markdown("## 📁 Gestión de Archivos")
    
    # Upload de archivos
    st.markdown("### ⬆️ Subir Archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Planilla de Inscripción")
        uploaded_inscripcion = st.file_uploader(
            "Sube tu archivo de inscripciones",
            type=['xlsx'],
            key="inscripcion",
            help="Archivo Excel con datos de nadadores registrados"
        )
        
        if uploaded_inscripcion:
            with open("planilla_inscripcion.xlsx", "wb") as f:
                f.write(uploaded_inscripcion.getbuffer())
            st.success("✅ Archivo de inscripción subido correctamente")
    
    with col2:
        st.markdown("#### 🏆 Resultados de Competencia")
        uploaded_resultados = st.file_uploader(
            "Sube el archivo de resultados",
            type=['xlsx'],
            key="resultados",
            help="Archivo Excel con tiempos finales de la competencia"
        )
        
        if uploaded_resultados:
            with open("resultados_con_tiempos.xlsx", "wb") as f:
                f.write(uploaded_resultados.getbuffer())
            st.success("✅ Archivo de resultados subido correctamente")
    
    # Nueva sección para base de datos
    st.markdown("### 💾 Base de Datos de Atletas")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### 📊 Base de Datos Local")
        if os.path.exists("BASE-DE-DATOS.xlsx"):
            st.success("✅ Base de datos local disponible")
            # Mostrar información de la base de datos local
            try:
                xl_file = pd.ExcelFile("BASE-DE-DATOS.xlsx")
                target_sheets = ['FPROYECCION 2025T', 'M. PROYECCION 2025']
                available_sheets = [s for s in target_sheets if s in xl_file.sheet_names]
                st.info(f"🔍 Hojas disponibles: {', '.join(available_sheets)}")
                
                # Contar registros totales
                total_records = 0
                for sheet in available_sheets:
                    try:
                        df = pd.read_excel("BASE-DE-DATOS.xlsx", sheet_name=sheet)
                        total_records += len(df)
                    except:
                        pass
                st.info(f"📈 Total de registros: {total_records:,}")
                
            except Exception as e:
                st.warning("⚠️ Error al leer información de la base de datos local")
        else:
            st.warning("⚠️ No se encuentra base de datos local")
    
    with col4:
        st.markdown("#### 🔄 Cargar Base de Datos Externa")
        uploaded_database = st.file_uploader(
            "Sube tu propia base de datos",
            type=['xlsx'],
            key="database",
            help="Archivo Excel con base de datos de atletas (debe contener hojas FPROYECCION 2025T y M. PROYECCION 2025)"
        )
        
        if uploaded_database:
            try:
                # Guardar como archivo temporal y verificar estructura
                with open("BASE-DE-DATOS-TEMP.xlsx", "wb") as f:
                    f.write(uploaded_database.getbuffer())
                
                # Verificar estructura
                xl_file = pd.ExcelFile("BASE-DE-DATOS-TEMP.xlsx")
                target_sheets = ['FPROYECCION 2025T', 'M. PROYECCION 2025']
                available_sheets = [s for s in target_sheets if s in xl_file.sheet_names]
                
                if available_sheets:
                    # Reemplazar base de datos actual
                    if os.path.exists("BASE-DE-DATOS.xlsx"):
                        os.rename("BASE-DE-DATOS.xlsx", "BASE-DE-DATOS-BACKUP.xlsx")
                    os.rename("BASE-DE-DATOS-TEMP.xlsx", "BASE-DE-DATOS.xlsx")
                    
                    st.success("✅ Base de datos externa cargada correctamente")
                    st.info(f"🔍 Hojas encontradas: {', '.join(available_sheets)}")
                    
                    # Contar registros
                    total_records = 0
                    for sheet in available_sheets:
                        try:
                            df = pd.read_excel("BASE-DE-DATOS.xlsx", sheet_name=sheet)
                            total_records += len(df)
                        except:
                            pass
                    st.info(f"📈 Total de registros cargados: {total_records:,}")
                    st.rerun()
                else:
                    os.remove("BASE-DE-DATOS-TEMP.xlsx")
                    st.error("❌ El archivo no contiene las hojas requeridas (FPROYECCION 2025T o M. PROYECCION 2025)")
                    
            except Exception as e:
                st.error(f"❌ Error al procesar la base de datos: {e}")
                if os.path.exists("BASE-DE-DATOS-TEMP.xlsx"):
                    os.remove("BASE-DE-DATOS-TEMP.xlsx")
    
    # Opción para restaurar base de datos original
    if os.path.exists("BASE-DE-DATOS-BACKUP.xlsx"):
        st.markdown("#### 🔄 Restaurar Base de Datos Original")
        col5, col6 = st.columns([2, 1])
        
        with col5:
            st.info("📁 Se encontró un respaldo de la base de datos original")
        
        with col6:
            if st.button("♻️ Restaurar Original", help="Restaurar la base de datos original del repositorio"):
                try:
                    if os.path.exists("BASE-DE-DATOS.xlsx"):
                        os.remove("BASE-DE-DATOS.xlsx")
                    os.rename("BASE-DE-DATOS-BACKUP.xlsx", "BASE-DE-DATOS.xlsx")
                    st.success("✅ Base de datos original restaurada")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al restaurar: {e}")
    
    # Mostrar archivos existentes
    st.markdown("### 📄 Archivos Disponibles")
    
    archivos = {
        "planilla_inscripcion.xlsx": "📋 Planilla de Inscripción",
        "BASE-DE-DATOS.xlsx": "🗄️ Base de Datos de Atletas",
        "sembrado_competencia.xlsx": "📊 Sembrado por Categoría",
        "sembrado_competencia_POR_TIEMPO.xlsx": "⏱️ Sembrado por Tiempo",
        "resultados_con_tiempos.xlsx": "🏆 Resultados de Competencia",
        "reporte_premiacion_final_CORREGIDO.xlsx": "🏅 Reporte de Premiación"
    }
    
    # Detectar archivos dinámicos generados por el procesador de sembrado
    import glob
    dynamic_result_files = glob.glob("resultados_desde_sembrado_*.xlsx")
    for file in dynamic_result_files:
        archivos[file] = "🏁 Resultados desde Sembrado"
    
    for archivo, descripcion in archivos.items():
        if os.path.exists(archivo):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"{descripcion}")
            
            with col2:
                try:
                    df = pd.read_excel(archivo, nrows=10)
                    if st.button("👁️", key=f"view_{archivo}", help="Ver vista previa"):
                        st.dataframe(df)
                except:
                    st.write("📄")
            
            with col3:
                with open(archivo, "rb") as file:
                    st.download_button(
                        label="⬇️",
                        data=file.read(),
                        file_name=archivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_{archivo}",
                        help="Descargar archivo"
                    )

def inscripcion_nadadores_interface():
    st.markdown("## ✍️ Inscripción de Nadadores")
    
    # Inicializar el sistema de inscripción
    registration_system = inscripcion_nadadores.SwimmerRegistration()
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3 = st.tabs(["➕ Nuevo Nadador", "📝 Nadadores Inscritos", "⚙️ Gestión"])
    
    with tab1:
        st.markdown("### Registrar Nuevo Nadador")
        
        # Método de inscripción
        inscripcion_method = st.radio(
            "Método de inscripción:",
            ["✍️ Manual", "🔍 Buscar en Base de Datos", "📤 Importar desde Excel"],
            horizontal=True
        )
        
        if inscripcion_method == "✍️ Manual":
            # INSCRIPCIÓN MANUAL (código existente)
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nombre y Apellidos", placeholder="Ej: Juan Pérez García")
                team = st.text_input("Equipo", placeholder="Ej: Club Natación TEN")
                age = st.number_input("Edad", min_value=6, max_value=99, value=12)
                
            with col2:
                gender = st.selectbox("Sexo", ["M", "F"], format_func=lambda x: "Masculino" if x == "M" else "Femenino")
                category = registration_system.get_category_by_age(age, gender)
                st.info(f"Categoría automática: **{category}**")
                
            st.markdown("### Pruebas de Inscripción")
            st.markdown("*Ingresa los tiempos de inscripción en formato MM:SS.dd o SS.dd. Deja en blanco las pruebas en las que no participa.*")
            
            events_data = {}
            col1, col2, col3 = st.columns(3)
            
            for i, event in enumerate(registration_system.swimming_events):
                with [col1, col2, col3][i % 3]:
                    time_input = st.text_input(
                        event,
                        key=f"manual_event_{i}",
                        placeholder="MM:SS.dd",
                        help="Ejemplo: 1:25.30 o 85.30"
                    )
                    
                    if time_input:
                        is_valid, error_msg = registration_system.validate_time_format(time_input)
                        if not is_valid:
                            st.error(error_msg)
                        else:
                            events_data[event] = time_input
            
            if st.button("🏊‍♂️ Registrar Nadador (Manual)", type="primary"):
                if not name.strip():
                    st.error("El nombre es obligatorio")
                elif not team.strip():
                    st.error("El equipo es obligatorio")
                elif not events_data:
                    st.warning("Debe inscribirse en al menos una prueba")
                else:
                    swimmer_data = {
                        'name': name.strip(),
                        'team': team.strip(),
                        'age': age,
                        'category': category,
                        'gender': gender,
                        'events': events_data
                    }
                    
                    success, message, duplicate_info = registration_system.add_swimmer(swimmer_data)
                    if success:
                        st.success(message)
                        st.balloons()
                        st.rerun()
                    else:
                        if duplicate_info:  # Es un duplicado
                            st.error(message)
                            st.markdown("### ⚠️ Información del Nadador Existente:")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Nombre:** {duplicate_info['name']}")
                                st.write(f"**Equipo:** {duplicate_info['team']}")
                                st.write(f"**Edad:** {duplicate_info['age']}")
                            with col2:
                                st.write(f"**Categoría:** {duplicate_info['category']}")
                                st.write(f"**Sexo:** {'Masculino' if duplicate_info['gender'] == 'M' else 'Femenino'}")
                            
                            if st.button("🚫 Inscribir De Todas Formas", key="force_add_manual"):
                                success_force, message_force, _ = registration_system.add_swimmer(swimmer_data, force_add=True)
                                if success_force:
                                    st.success(f"✅ {swimmer_data['name']} inscrito como registro adicional")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error(message_force)
                        else:
                            st.error(message)
        
        elif inscripcion_method == "🔍 Buscar en Base de Datos":
            # BÚSQUEDA EN BASE DE DATOS
            st.markdown("### Buscar Nadador en Base de Datos")
            
            # Estado de la base de datos
            with st.container():
                col_db1, col_db2 = st.columns([2, 1])
                
                with col_db1:
                    if os.path.exists("BASE-DE-DATOS.xlsx"):
                        try:
                            xl_file = pd.ExcelFile("BASE-DE-DATOS.xlsx")
                            target_sheets = ['FPROYECCION 2025T', 'M. PROYECCION 2025']
                            available_sheets = [s for s in target_sheets if s in xl_file.sheet_names]
                            
                            if available_sheets:
                                # Contar registros
                                total_records = 0
                                for sheet in available_sheets:
                                    try:
                                        df = pd.read_excel("BASE-DE-DATOS.xlsx", sheet_name=sheet)
                                        total_records += len(df)
                                    except:
                                        pass
                                
                                st.success(f"✅ Base de datos activa: {total_records:,} atletas ({len(available_sheets)} hojas)")
                            else:
                                st.warning("⚠️ Base de datos sin hojas válidas")
                        except Exception as e:
                            st.error("❌ Error al leer base de datos")
                    else:
                        st.error("❌ No se encuentra base de datos")
                
                with col_db2:
                    with st.popover("🔄 Cambiar BD", help="Cargar una base de datos diferente"):
                        st.markdown("**Cargar nueva base de datos:**")
                        uploaded_db = st.file_uploader(
                            "Archivo de base de datos",
                            type=['xlsx'],
                            key="db_for_search",
                            help="Debe contener hojas FPROYECCION 2025T y/o M. PROYECCION 2025"
                        )
                        
                        if uploaded_db:
                            try:
                                # Guardar como archivo temporal
                                with open("BASE-DE-DATOS-TEMP.xlsx", "wb") as f:
                                    f.write(uploaded_db.getbuffer())
                                
                                # Verificar estructura
                                xl_file = pd.ExcelFile("BASE-DE-DATOS-TEMP.xlsx")
                                target_sheets = ['FPROYECCION 2025T', 'M. PROYECCION 2025']
                                available_sheets = [s for s in target_sheets if s in xl_file.sheet_names]
                                
                                if available_sheets:
                                    # Crear backup si existe BD actual
                                    if os.path.exists("BASE-DE-DATOS.xlsx"):
                                        os.rename("BASE-DE-DATOS.xlsx", "BASE-DE-DATOS-BACKUP.xlsx")
                                    os.rename("BASE-DE-DATOS-TEMP.xlsx", "BASE-DE-DATOS.xlsx")
                                    
                                    st.success("✅ Base de datos cargada")
                                    st.rerun()
                                else:
                                    os.remove("BASE-DE-DATOS-TEMP.xlsx")
                                    st.error("❌ Archivo sin hojas válidas")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                                if os.path.exists("BASE-DE-DATOS-TEMP.xlsx"):
                                    os.remove("BASE-DE-DATOS-TEMP.xlsx")
            
            st.markdown("---")
            
            search_term = st.text_input(
                "Buscar nadador por nombre:",
                placeholder="Escribe el nombre del nadador...",
                help="Se buscará en la base de datos activa"
            )
            
            if search_term and len(search_term.strip()) >= 3:
                with st.spinner("Buscando en la base de datos..."):
                    matches, search_message = registration_system.search_swimmer_in_database(search_term)
                
                if matches:
                    st.success(search_message)
                    
                    # Mostrar resultados de búsqueda
                    st.markdown("### Resultados de Búsqueda")
                    
                    for i, match in enumerate(matches):
                        with st.expander(f"🏊‍♂️ {match['name']}"):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                # Obtener información del nadador
                                swimmer_info = registration_system.get_swimmer_info_from_database(match)
                                st.write(f"**Equipo:** {swimmer_info['team'] or 'No especificado'}")
                                st.write(f"**Edad:** {swimmer_info['age'] or 'No especificada'}")
                                st.write(f"**Categoría:** {swimmer_info['category'] or 'No especificada'}")
                                st.write(f"**Sexo:** {'Masculino' if swimmer_info['gender'] == 'M' else 'Femenino' if swimmer_info['gender'] == 'F' else 'No especificado'}")
                                
                                # Mostrar tiempos disponibles
                                latest_times, times_message = registration_system.get_swimmer_latest_times(swimmer_info)
                                if latest_times:
                                    st.write("**Últimos tiempos registrados:**")
                                    for event, time in latest_times.items():
                                        st.write(f"• {event}: {time}")
                                else:
                                    st.write("*No hay tiempos registrados*")
                            
                            with col2:
                                if st.button(f"📋 Inscribir", key=f"db_register_{i}"):
                                    # Crear nadador desde base de datos
                                    swimmer_data, create_message = registration_system.create_swimmer_from_database(match)
                                    
                                    # Registrar el nadador
                                    success, register_message, duplicate_info = registration_system.add_swimmer(swimmer_data)
                                    if success:
                                        st.success(register_message)
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        if duplicate_info:  # Es un duplicado
                                            st.error(register_message)
                                            if st.button("🚫 Inscribir De Todas Formas", key=f"force_add_db_{i}"):
                                                success_force, message_force, _ = registration_system.add_swimmer(swimmer_data, force_add=True)
                                                if success_force:
                                                    st.success(f"✅ {swimmer_data['name']} inscrito como registro adicional")
                                                    st.balloons()
                                                    st.rerun()
                                                else:
                                                    st.error(message_force)
                                        else:
                                            st.error(register_message)
                else:
                    st.warning(search_message)
            
            elif search_term and len(search_term.strip()) < 3:
                st.info("Escribe al menos 3 caracteres para buscar")
            
            # Información sobre la base de datos
            if os.path.exists(registration_system.archivo_base_datos):
                st.markdown("### 📊 Estado de la Base de Datos")
                st.success(f"✅ Base de datos encontrada: `{registration_system.archivo_base_datos}`")
            else:
                st.warning(f"⚠️ No se encontró la base de datos: `{registration_system.archivo_base_datos}`")
        
        elif inscripcion_method == "📤 Importar desde Excel":
            # IMPORTACIÓN MASIVA DESDE EXCEL
            st.markdown("### Importar Nadadores desde Excel")
            
            st.markdown("""
            <div class="info-message">
                <h4>📋 Instrucciones para la importación masiva:</h4>
                <ol>
                    <li>Utiliza un archivo Excel con la misma estructura que el archivo <code>planilla_inscripcion.xlsx</code></li>
                    <li>Las columnas requeridas son: <strong>NOMBRE Y AP</strong>, <strong>EQUIPO</strong>, <strong>EDAD</strong>, <strong>CAT.</strong>, <strong>SEXO</strong></li>
                    <li>Las columnas de pruebas deben tener los tiempos en formato MM:SS.dd (ejemplo: 1:25.30)</li>
                    <li>Los nadadores duplicados serán omitidos automáticamente</li>
                    <li>La categoría se calculará automáticamente si no se proporciona</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
            
            # Descarga del template
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("#### 📥 Subir Archivo de Inscripciones")
            
            with col2:
                if os.path.exists("planilla_inscripcion.xlsx"):
                    with open("planilla_inscripcion.xlsx", "rb") as file:
                        st.download_button(
                            label="📄 Descargar Template",
                            data=file.read(),
                            file_name="template_inscripciones.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            help="Descarga el archivo actual como plantilla"
                        )
            
            # Upload del archivo
            uploaded_file = st.file_uploader(
                "Selecciona el archivo Excel con los nadadores:",
                type=['xlsx', 'xls'],
                help="El archivo debe contener las columnas requeridas y los datos de los nadadores",
                key="bulk_import_uploader"
            )
            
            # Limpiar estado cuando se cambia de archivo
            if uploaded_file is not None:
                # Detectar si es un archivo nuevo
                current_file_info = f"{uploaded_file.name}_{uploaded_file.size}"
                if 'last_uploaded_file' not in st.session_state:
                    st.session_state.last_uploaded_file = current_file_info
                elif st.session_state.last_uploaded_file != current_file_info:
                    # Archivo nuevo detectado, limpiar estados previos
                    st.session_state.last_uploaded_file = current_file_info
                    # Limpiar cualquier resultado anterior
                    for key in list(st.session_state.keys()):
                        if key.startswith('bulk_import_'):
                            del st.session_state[key]
                    st.rerun()
                
                st.success(f"✅ Archivo cargado: {uploaded_file.name}")
                
                # Vista previa del archivo
                if st.checkbox("👁️ Ver vista previa del archivo", key="preview_checkbox"):
                    try:
                        # Usar caché para evitar re-lecturas
                        @st.cache_data
                        def load_preview_data(file_content, file_name):
                            return pd.read_excel(io.BytesIO(file_content))
                        
                        preview_df = load_preview_data(uploaded_file.getvalue(), uploaded_file.name)
                        st.markdown("**Vista previa (primeras 10 filas):**")
                        st.dataframe(preview_df.head(10))
                        st.info(f"Total de filas en el archivo: {len(preview_df)}")
                    except Exception as e:
                        st.error(f"Error al leer el archivo: {str(e)}")
                
                # Botón de importación
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col2:
                    if st.button("🚀 Importar Nadadores", type="primary", use_container_width=True):
                        with st.spinner("Importando nadadores..."):
                            success, message = registration_system.bulk_import_from_excel(uploaded_file)
                            
                            # Guardar resultado en session_state
                            st.session_state.bulk_import_result = (success, message)
                            st.session_state.bulk_import_completed = True
                            
                            if success:
                                st.success("✅ **Importación completada exitosamente!**")
                                st.markdown(message)
                                st.balloons()
                                
                                # Mostrar estadísticas actualizadas
                                updated_swimmers = registration_system.get_swimmers_list()
                                if updated_swimmers:
                                    st.markdown("---")
                                    st.markdown("### 📊 Estado Actualizado de Inscripciones")
                                    
                                    total_swimmers = len(updated_swimmers)
                                    male_count = len([s for s in updated_swimmers if s['gender'] == 'M'])
                                    female_count = len([s for s in updated_swimmers if s['gender'] == 'F'])
                                    
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Total Nadadores", total_swimmers)
                                    with col2:
                                        st.metric("Masculinos", male_count)
                                    with col3:
                                        st.metric("Femeninos", female_count)
                            else:
                                st.error("❌ **Error en la importación**")
                                st.markdown(message)
                
                # Mostrar resultados previos si existen
                if 'bulk_import_completed' in st.session_state and st.session_state.bulk_import_completed:
                    st.markdown("---")
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if st.session_state.bulk_import_result[0]:
                            st.info("📋 **Importación anterior completada**")
                        else:
                            st.warning("⚠️ **Última importación tuvo errores**")
                    
                    with col2:
                        if st.button("🧹 Limpiar Resultados", help="Limpia los resultados de la importación anterior"):
                            # Limpiar resultados
                            for key in list(st.session_state.keys()):
                                if key.startswith('bulk_import_'):
                                    del st.session_state[key]
                            st.rerun()
            
            else:
                st.info("📤 Selecciona un archivo Excel para importar nadadores masivamente")
    
    with tab2:
        st.markdown("### Nadadores Inscritos")
        
        swimmers = registration_system.get_swimmers_list()
        
        if not swimmers:
            st.info("No hay nadadores inscritos aún. Usa la pestaña 'Nuevo Nadador' para registrar.")
        else:
            st.success(f"Total de nadadores inscritos: **{len(swimmers)}**")
            
            for i, swimmer in enumerate(swimmers):
                with st.expander(f"🏊‍♂️ {swimmer['name']} - {swimmer['team']} ({swimmer['age']} años)"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Categoría:** {swimmer['category']}")
                        st.write(f"**Sexo:** {'Masculino' if swimmer['gender'] == 'M' else 'Femenino'}")
                        
                        if swimmer['events']:
                            st.write("**Pruebas inscritas:**")
                            for event in swimmer['events']:
                                st.write(f"• {event}")
                        else:
                            st.write("*Sin pruebas registradas*")
                    
                    with col2:
                        col_edit, col_delete = st.columns(2)
                        
                        with col_edit:
                            if st.button("✏️ Editar", key=f"edit_{i}"):
                                st.session_state[f'editing_swimmer_{i}'] = True
                                st.rerun()
                        
                        with col_delete:
                            if st.button("🗑️ Eliminar", key=f"delete_{i}"):
                                success, message = registration_system.delete_swimmer(swimmer['index'])
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
            
            # Formulario de edición (aparece cuando se hace clic en editar)
            for i, swimmer in enumerate(swimmers):
                if f'editing_swimmer_{i}' in st.session_state and st.session_state[f'editing_swimmer_{i}']:
                    st.markdown("---")
                    st.markdown(f"### ✏️ Editando: {swimmer['name']}")
                    
                    # Obtener datos actuales del nadador
                    swimmer_data, message = registration_system.get_swimmer_for_editing(swimmer['index'])
                    
                    if swimmer_data:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("Nombre y Apellidos", value=swimmer_data['name'], key=f"edit_name_{i}")
                            edit_team = st.text_input("Equipo", value=swimmer_data['team'], key=f"edit_team_{i}")
                            edit_age = st.number_input("Edad", min_value=6, max_value=99, value=swimmer_data['age'], key=f"edit_age_{i}")
                            
                        with col2:
                            edit_gender = st.selectbox("Sexo", ["M", "F"], 
                                                     index=0 if swimmer_data['gender'] == 'M' else 1,
                                                     format_func=lambda x: "Masculino" if x == "M" else "Femenino",
                                                     key=f"edit_gender_{i}")
                            edit_category = registration_system.get_category_by_age(edit_age, edit_gender)
                            st.info(f"Categoría automática: **{edit_category}**")
                        
                        st.markdown("### Pruebas de Inscripción")
                        st.markdown("*Edita los tiempos de inscripción. Deja en blanco para eliminar la prueba.*")
                        
                        edit_events_data = {}
                        col1, col2, col3 = st.columns(3)
                        
                        for j, event in enumerate(registration_system.swimming_events):
                            with [col1, col2, col3][j % 3]:
                                current_time = swimmer_data['events'].get(event, "")
                                edit_time_input = st.text_input(
                                    event,
                                    value=current_time,
                                    key=f"edit_event_{i}_{j}",
                                    placeholder="MM:SS.dd",
                                    help="Ejemplo: 1:25.30 o 85.30"
                                )
                                
                                if edit_time_input:
                                    is_valid, error_msg = registration_system.validate_time_format(edit_time_input)
                                    if not is_valid:
                                        st.error(error_msg)
                                    else:
                                        edit_events_data[event] = edit_time_input
                        
                        col_save, col_cancel = st.columns(2)
                        
                        with col_save:
                            if st.button("💾 Guardar Cambios", key=f"save_{i}", type="primary"):
                                updated_swimmer_data = {
                                    'name': edit_name.strip(),
                                    'team': edit_team.strip(),
                                    'age': edit_age,
                                    'category': edit_category,
                                    'gender': edit_gender,
                                    'events': edit_events_data
                                }
                                
                                success, message = registration_system.update_swimmer(swimmer['index'], updated_swimmer_data)
                                if success:
                                    st.success(message)
                                    del st.session_state[f'editing_swimmer_{i}']
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error(message)
                        
                        with col_cancel:
                            if st.button("❌ Cancelar", key=f"cancel_{i}"):
                                del st.session_state[f'editing_swimmer_{i}']
                                st.rerun()
                    else:
                        st.error(message)
    
    with tab3:
        st.markdown("### Gestión del Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Estadísticas")
            swimmers = registration_system.get_swimmers_list()
            
            if swimmers:
                teams = {}
                categories = {}
                genders = {"Masculino": 0, "Femenino": 0}
                events_stats = {}
                
                # Procesar estadísticas
                for swimmer in swimmers:
                    # Equipos
                    teams[swimmer['team']] = teams.get(swimmer['team'], 0) + 1
                    
                    # Categorías
                    categories[swimmer['category']] = categories.get(swimmer['category'], 0) + 1
                    
                    # Géneros
                    gender_label = "Masculino" if swimmer['gender'] == 'M' else "Femenino"
                    genders[gender_label] += 1
                    
                    # Eventos (contar inscripciones por prueba)
                    for event_info in swimmer['events']:
                        if ':' in event_info:  # Formato "EVENTO: tiempo"
                            event_name = event_info.split(':')[0].strip()
                            events_stats[event_name] = events_stats.get(event_name, 0) + 1
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Nadadores", len(swimmers))
                with col2:
                    st.metric("Equipos Diferentes", len(teams))
                with col3:
                    st.metric("Categorías", len(categories))
                
                # Distribución por género
                st.markdown("#### 👥 Distribución por Sexo")
                if genders:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("👨 Masculino", genders["Masculino"])
                    with col2:
                        st.metric("👩 Femenino", genders["Femenino"])
                    
                    # Gráfico de género
                    st.bar_chart(genders)
                
                # Distribución por pruebas
                if events_stats:
                    st.markdown("#### 🏊‍♂️ Distribución por Pruebas")
                    st.bar_chart(events_stats)
                    
                    # Top 5 pruebas más populares
                    top_events = sorted(events_stats.items(), key=lambda x: x[1], reverse=True)[:5]
                    st.markdown("**Top 5 Pruebas Más Populares:**")
                    for i, (event, count) in enumerate(top_events, 1):
                        st.write(f"{i}. **{event}**: {count} nadadores")
                
                # Otras estadísticas expandibles
                if st.checkbox("📊 Ver distribución por categorías"):
                    st.bar_chart(categories)
                
                if st.checkbox("🏢 Ver distribución por equipos"):
                    st.bar_chart(teams)
                
                if st.checkbox("📈 Estadísticas detalladas"):
                    st.markdown("#### Estadísticas Detalladas")
                    
                    # Promedio de edad
                    ages = [swimmer['age'] for swimmer in swimmers if swimmer['age']]
                    if ages:
                        avg_age = sum(ages) / len(ages)
                        st.metric("Edad Promedio", f"{avg_age:.1f} años")
                    
                    # Nadadores por categoría
                    st.markdown("**Nadadores por Categoría:**")
                    for category, count in sorted(categories.items()):
                        percentage = (count / len(swimmers)) * 100
                        st.write(f"• **{category}**: {count} nadadores ({percentage:.1f}%)")
                    
                    # Total de inscripciones en pruebas
                    total_event_entries = sum(len(swimmer['events']) for swimmer in swimmers)
                    if total_event_entries > 0:
                        avg_events_per_swimmer = total_event_entries / len(swimmers)
                        st.metric("Promedio pruebas/nadador", f"{avg_events_per_swimmer:.1f}")
            else:
                st.info("No hay datos para mostrar estadísticas")
        
        with col2:
            st.markdown("#### 🔧 Acciones del Sistema")
            
            if st.button("📋 Crear Archivo Vacío"):
                success, message = registration_system.create_empty_registration_file()
                if success:
                    st.success(message)
                else:
                    st.error(message)
            
            if os.path.exists(registration_system.archivo_inscripcion):
                with open(registration_system.archivo_inscripcion, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Planilla de Inscripción",
                        data=file.read(),
                        file_name="planilla_inscripcion.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            # Generar reporte PDF
            if swimmers:
                if st.button("📄 Generar Reporte PDF", type="primary"):
                    try:
                        pdf_data = registration_system.generate_pdf_report(swimmers, teams, categories, genders, events_stats)
                        if pdf_data:
                            st.download_button(
                                label="📄 Descargar Reporte PDF",
                                data=pdf_data,
                                file_name="reporte_inscripciones.pdf",
                                mime="application/pdf"
                            )
                            st.success("¡Reporte PDF generado exitosamente!")
                        else:
                            st.error("**ReportLab no está instalado en este entorno Python**")
                            st.markdown("""
                            **Para generar reportes PDF, pruebe uno de estos comandos:**
                            ```bash
                            pip install reportlab
                            # o
                            pip3 install reportlab
                            # o
                            python -m pip install reportlab
                            # o  
                            python3 -m pip install reportlab
                            ```
                            
                            **Si está usando un entorno virtual, asegúrese de activarlo primero:**
                            ```bash
                            source venv/bin/activate  # Linux/Mac
                            # o
                            venv\\Scripts\\activate     # Windows
                            ```
                            
                            Luego reinicie la aplicación Streamlit.
                            """)
                    except Exception as e:
                        if "reportlab" in str(e).lower() or "not available" in str(e).lower():
                            st.error("Para generar reportes PDF, instale la librería ReportLab ejecutando: pip install reportlab")
                        else:
                            st.error(f"Error al generar el reporte PDF: {str(e)}")
            else:
                st.info("No hay nadadores inscritos para generar reporte")
            
            st.markdown("#### 🧹 Limpiar Inscripciones")
            col_clean1, col_clean2 = st.columns([2, 1])
            
            with col_clean1:
                st.info("🗑️ Eliminar todas las inscripciones para empezar con nuevos nadadores")
            
            with col_clean2:
                if st.button("👥 Limpiar Inscripciones", type="secondary", help="Eliminar planilla de inscripción"):
                    if os.path.exists("planilla_inscripcion.xlsx"):
                        try:
                            os.remove("planilla_inscripcion.xlsx")
                            st.success("✅ Inscripciones eliminadas")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                    else:
                        st.info("ℹ️ No hay inscripciones que eliminar")
            
            st.markdown("#### ℹ️ Información")
            st.info("""
            **Categorías por edad:**
            - PRE-INFANTIL A: ≤8 años
            - PRE-INFANTIL B: ≤9 años  
            - INFANTIL A: ≤10 años
            - INFANTIL B: ≤11 años
            - JUVENIL A: ≤12 años
            - JUVENIL B: ≤13 años
            - JUNIOR A: ≤14 años
            - JUNIOR B: ≤15 años
            - SENIOR: ≤17 años
            - MASTER: >17 años
            """)
    
    # Copyright footer para todas las páginas
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 12px; margin-top: 20px;'>"
        "Sistema de Gestión de Competencias de Natación - Todos los derechos reservados"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
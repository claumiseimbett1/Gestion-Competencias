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
            st.markdown("### 👁️ Vista Previa del Sembrado por Categorías")
            
            seeding_data = st.session_state['seeding_preview_cat']
            
            # Selector de evento para visualizar
            eventos_disponibles = list(seeding_data.keys())
            if eventos_disponibles:
                evento_seleccionado = st.selectbox(
                    "Selecciona un evento para visualizar:",
                    eventos_disponibles,
                    key="evento_cat_preview"
                )
                
                if evento_seleccionado:
                    series = seeding_data[evento_seleccionado]['series']
                    st.markdown(f"**{evento_seleccionado}**")
                    
                    # Mostrar cada serie
                    for serie in series:
                        st.markdown(f"#### Serie {serie['serie']}")
                        
                        # Crear tabla de la serie
                        carriles_data = []
                        for i, nadador in enumerate(serie['carriles'], 1):
                            if nadador:
                                carriles_data.append({
                                    "Carril": i,
                                    "Nombre": nadador['nombre'],
                                    "Equipo": nadador['equipo'],
                                    "Edad": nadador['edad'],
                                    "Categoría": nadador['categoria'],
                                    "Tiempo Inscripción": str(nadador['tiempo_inscripcion']),
                                    "Tiempo Competencia": ""
                                })
                            else:
                                carriles_data.append({
                                    "Carril": i,
                                    "Nombre": "---",
                                    "Equipo": "---",
                                    "Edad": "---",
                                    "Categoría": "---",
                                    "Tiempo Inscripción": "---",
                                    "Tiempo Competencia": "---"
                                })
                        
                        df_serie = pd.DataFrame(carriles_data)
                        st.dataframe(df_serie, use_container_width=True, hide_index=True)
    
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
            st.markdown("### 👁️ Vista Previa del Sembrado por Tiempo")
            
            seeding_data = st.session_state['seeding_preview_time']
            
            # Selector de evento para visualizar
            eventos_disponibles = list(seeding_data.keys())
            if eventos_disponibles:
                evento_seleccionado = st.selectbox(
                    "Selecciona un evento para visualizar:",
                    eventos_disponibles,
                    key="evento_time_preview"
                )
                
                if evento_seleccionado:
                    series = seeding_data[evento_seleccionado]['series']
                    st.markdown(f"**{evento_seleccionado}**")
                    
                    # Mostrar cada serie
                    for serie in series:
                        st.markdown(f"#### Serie {serie['serie']}")
                        
                        # Crear tabla de la serie
                        carriles_data = []
                        for i, nadador in enumerate(serie['carriles'], 1):
                            if nadador:
                                carriles_data.append({
                                    "Carril": i,
                                    "Nombre": nadador['nombre'],
                                    "Equipo": nadador['equipo'],
                                    "Edad": nadador['edad'],
                                    "Categoría": nadador['categoria'],
                                    "Tiempo Inscripción": str(nadador['tiempo_inscripcion']),
                                    "Tiempo Competencia": ""
                                })
                            else:
                                carriles_data.append({
                                    "Carril": i,
                                    "Nombre": "---",
                                    "Equipo": "---",
                                    "Edad": "---",
                                    "Categoría": "---",
                                    "Tiempo Inscripción": "---",
                                    "Tiempo Competencia": "---"
                                })
                        
                        df_serie = pd.DataFrame(carriles_data)
                        st.dataframe(df_serie, use_container_width=True, hide_index=True)
        
        # Sección para procesar sembrado con tiempos
        st.markdown("---")
        st.markdown("### 🔄 Procesar Sembrado con Tiempos de Competencia")
        st.markdown("""
        Si ya tienes un archivo de sembrado con los tiempos de competencia agregados,
        puedes convertirlo a formato de resultados aquí.
        """)
        
        col_upload, col_process = st.columns([2, 1])
        
        with col_upload:
            uploaded_seeding = st.file_uploader(
                "Sube tu archivo de sembrado con tiempos agregados:",
                type=['xlsx'],
                key="seeding_with_times_upload",
                help="Archivo Excel de sembrado donde ya agregaste los tiempos en la columna 'Tiempo Competencia'"
            )
        
        with col_process:
            if uploaded_seeding is not None:
                if st.button("🔄 Convertir a Resultados", type="secondary"):
                    with st.spinner("Procesando tiempos..."):
                        try:
                            # Guardar archivo temporalmente
                            temp_file = f"temp_seeding_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                            with open(temp_file, "wb") as f:
                                f.write(uploaded_seeding.getbuffer())
                            
                            # Importar y usar la función de procesamiento
                            import importlib.util
                            spec = importlib.util.spec_from_file_location("processor", "5-procesar_sembrado_tiempos.py")
                            processor = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(processor)
                            
                            success, message = processor.process_seeding_with_times(temp_file)
                            
                            # Limpiar archivo temporal
                            if os.path.exists(temp_file):
                                os.remove(temp_file)
                            
                            if success:
                                st.success(f"✅ {message}")
                                st.info("📄 El archivo de resultados está disponible para descarga en la sección de gestión de archivos")
                            else:
                                st.error(f"❌ {message}")
                                
                        except Exception as e:
                            st.error(f"❌ Error al procesar archivo: {e}")
                            # Limpiar archivo temporal en caso de error
                            if os.path.exists(temp_file):
                                os.remove(temp_file)
    
    with tab3:
        st.markdown("### ✍️ Sembrado Manual")
        st.markdown("""
        **¿Cuándo usar este método?**
        - Competencias con criterios especiales
        - Eventos ceremoniales o de exhibición
        - Cuando necesitas control total sobre la organización
        """)
        
        st.info("🚧 **Próximamente**: Interfaz para crear sembrados manuales con drag & drop y organización personalizada.")
        
        # Placeholder para funcionalidad futura
        st.markdown("""
        **Funcionalidades planeadas:**
        - 📋 Vista de todas las pruebas inscritas
        - 🔄 Organización manual de series y carriles
        - 👥 Agrupación personalizada de nadadores
        - 📊 Vista previa del sembrado antes de generar
        """)

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
import streamlit as st
import pandas as pd
import io
import os
from pathlib import Path
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
            "📊 Generar Sembrado por Categoría",
            "⏱️ Generar Sembrado por Tiempo",
            "🏆 Procesar Resultados",
            "📁 Gestión de Archivos"
        ]
    )
    
    if opcion == "🏠 Inicio":
        mostrar_inicio()
    elif opcion == "✍️ Inscripción de Nadadores":
        inscripcion_nadadores_interface()
    elif opcion == "📊 Generar Sembrado por Categoría":
        generar_sembrado_categoria()
    elif opcion == "⏱️ Generar Sembrado por Tiempo":
        generar_sembrado_tiempo()
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
            st.dataframe(df.head())
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
    
    # Mostrar archivos existentes
    st.markdown("### 📄 Archivos Disponibles")
    
    archivos = {
        "planilla_inscripcion.xlsx": "📋 Planilla de Inscripción",
        "sembrado_competencia.xlsx": "📊 Sembrado por Categoría",
        "sembrado_competencia_POR_TIEMPO.xlsx": "⏱️ Sembrado por Tiempo",
        "resultados_con_tiempos.xlsx": "🏆 Resultados de Competencia",
        "reporte_premiacion_final_CORREGIDO.xlsx": "🏅 Reporte de Premiación",
        "NUEVA BASE DE DATOS.xlsx": "🗄️ Base de Datos"
    }
    
    for archivo, descripcion in archivos.items():
        if os.path.exists(archivo):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"{descripcion}")
            
            with col2:
                try:
                    df = pd.read_excel(archivo, nrows=5)
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
                    key=f"event_{i}",
                    placeholder="MM:SS.dd",
                    help="Ejemplo: 1:25.30 o 85.30"
                )
                
                if time_input:
                    is_valid, error_msg = registration_system.validate_time_format(time_input)
                    if not is_valid:
                        st.error(error_msg)
                    else:
                        events_data[event] = time_input
        
        if st.button("🏊‍♂️ Registrar Nadador", type="primary"):
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
                
                success, message = registration_system.add_swimmer(swimmer_data)
                if success:
                    st.success(message)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(message)
    
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
                        if st.button("🗑️ Eliminar", key=f"delete_{i}"):
                            success, message = registration_system.delete_swimmer(swimmer['index'])
                            if success:
                                st.success(message)
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
                genders = {"M": 0, "F": 0}
                
                for swimmer in swimmers:
                    teams[swimmer['team']] = teams.get(swimmer['team'], 0) + 1
                    categories[swimmer['category']] = categories.get(swimmer['category'], 0) + 1
                    genders[swimmer['gender']] += 1
                
                st.metric("Total Nadadores", len(swimmers))
                st.metric("Equipos", len(teams))
                st.metric("Masculino/Femenino", f"{genders['M']}/{genders['F']}")
                
                if st.checkbox("Ver distribución por categorías"):
                    st.bar_chart(categories)
                
                if st.checkbox("Ver distribución por equipos"):
                    st.bar_chart(teams)
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

if __name__ == "__main__":
    main()
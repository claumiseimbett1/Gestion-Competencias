import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import re
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus.flowables import Image
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
from io import BytesIO

class SwimmerRegistration:
    def __init__(self):
        self.archivo_inscripcion = 'planilla_inscripcion.xlsx'
        self.archivo_base_datos = 'BASE-DE-DATOS.xlsx'
        self.swimming_events = [
            "50M CROLL",
            "100M CROLL", 
            "200M CROLL",
            "400M CROLL",
            "50M ESPALDA",
            "100M ESPALDA",
            "200M ESPALDA", 
            "50M PECHO",
            "100M PECHO",
            "200M PECHO",
            "50M MARIPOSA",
            "100M MARIPOSA",
            "200M MARIPOSA",
            "200M COMBINADO INDIVIDUAL",
            "400M COMBINADO INDIVIDUAL"
        ]
        
        self.categories = [
            "PRE-INFANTIL A",
            "PRE-INFANTIL B", 
            "INFANTIL A",
            "INFANTIL B",
            "JUVENIL A",
            "JUVENIL B", 
            "JUNIOR A",
            "JUNIOR B",
            "SENIOR",
            "MASTER"
        ]
        
    def get_category_by_age(self, age, gender):
        age = int(age)
        if gender.upper() == 'M':  # Masculino
            if age <= 8:
                return "PRE-INFANTIL A"
            elif age <= 9:
                return "PRE-INFANTIL B"
            elif age <= 10:
                return "INFANTIL A"
            elif age <= 11:
                return "INFANTIL B"
            elif age <= 12:
                return "JUVENIL A"
            elif age <= 13:
                return "JUVENIL B"
            elif age <= 14:
                return "JUNIOR A"
            elif age <= 15:
                return "JUNIOR B"
            elif age <= 17:
                return "SENIOR"
            else:
                return "MASTER"
        else:  # Femenino
            if age <= 8:
                return "PRE-INFANTIL A"
            elif age <= 9:
                return "PRE-INFANTIL B"
            elif age <= 10:
                return "INFANTIL A"
            elif age <= 11:
                return "INFANTIL B"
            elif age <= 12:
                return "JUVENIL A"
            elif age <= 13:
                return "JUVENIL B"
            elif age <= 14:
                return "JUNIOR A"
            elif age <= 15:
                return "JUNIOR B"
            elif age <= 17:
                return "SENIOR"
            else:
                return "MASTER"
    
    def validate_time_format(self, time_str):
        if not time_str or time_str.strip() == "":
            return True, None
            
        time_str = time_str.strip().replace(',', '.')
        
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    minutes = int(parts[0])
                    seconds = float(parts[1])
                    if 0 <= minutes <= 59 and 0 <= seconds < 60:
                        return True, time_str
            else:
                seconds = float(time_str)
                if 0 <= seconds <= 3600:
                    return True, time_str
        except ValueError:
            pass
            
        return False, "Formato de tiempo inválido. Use MM:SS.dd o SS.dd"
    
    def load_existing_data(self):
        if os.path.exists(self.archivo_inscripcion):
            try:
                df = pd.read_excel(self.archivo_inscripcion)
                return df
            except Exception as e:
                print(f"Error al cargar datos existentes: {e}")
                return None
        return None
    
    def create_empty_registration_file(self):
        columns = ['NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO'] + self.swimming_events
        df = pd.DataFrame(columns=columns)
        
        try:
            df.to_excel(self.archivo_inscripcion, index=False)
            return True, "Archivo de inscripción creado exitosamente"
        except Exception as e:
            return False, f"Error al crear archivo: {e}"
    
    def check_duplicate_swimmer(self, swimmer_name):
        """Verificar si el nadador ya está inscrito"""
        df = self.load_existing_data()
        if df is None or df.empty:
            return False, None
        
        # Buscar nombres similares (exacto o muy parecido)
        name_lower = swimmer_name.lower().strip()
        for index, row in df.iterrows():
            existing_name = str(row['NOMBRE Y AP']).lower().strip()
            if existing_name == name_lower:
                return True, {
                    'index': index,
                    'name': row['NOMBRE Y AP'],
                    'team': row['EQUIPO'],
                    'age': row['EDAD'],
                    'category': row['CAT.'],
                    'gender': row['SEXO']
                }
        
        return False, None
    
    def add_swimmer(self, swimmer_data, force_add=False):
        try:
            df_existing = self.load_existing_data()
            
            if df_existing is None:
                success, message = self.create_empty_registration_file()
                if not success:
                    return False, message, None
                df_existing = self.load_existing_data()
            
            # Verificar duplicados si no se fuerza la adición
            if not force_add:
                is_duplicate, duplicate_info = self.check_duplicate_swimmer(swimmer_data['name'])
                if is_duplicate:
                    return False, f"⚠️ POSIBLE DUPLICADO: El nadador '{duplicate_info['name']}' ya está inscrito", duplicate_info
            
            new_row = {
                'NOMBRE Y AP': swimmer_data['name'],
                'EQUIPO': swimmer_data['team'],
                'EDAD': swimmer_data['age'],
                'CAT.': swimmer_data['category'],
                'SEXO': swimmer_data['gender']
            }
            
            for event, time in swimmer_data['events'].items():
                if time and time.strip():
                    new_row[event] = time
                    
            new_df = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
            new_df.to_excel(self.archivo_inscripcion, index=False)
            
            events_count = len(swimmer_data['events'])
            success_msg = f"✅ {swimmer_data['name']} inscrito exitosamente con {events_count} prueba(s)"
            
            return True, success_msg, None
            
        except Exception as e:
            return False, f"Error al registrar nadador: {e}", None
    
    def update_swimmer(self, index, swimmer_data):
        try:
            df = self.load_existing_data()
            if df is None or index >= len(df):
                return False, "Nadador no encontrado"
            
            df.loc[index, 'NOMBRE Y AP'] = swimmer_data['name']
            df.loc[index, 'EQUIPO'] = swimmer_data['team']
            df.loc[index, 'EDAD'] = swimmer_data['age']
            df.loc[index, 'CAT.'] = swimmer_data['category']
            df.loc[index, 'SEXO'] = swimmer_data['gender']
            
            for event, time in swimmer_data['events'].items():
                if time and time.strip():
                    df.loc[index, event] = time
                else:
                    df.loc[index, event] = None
                    
            df.to_excel(self.archivo_inscripcion, index=False)
            return True, "Nadador actualizado exitosamente"
            
        except Exception as e:
            return False, f"Error al actualizar nadador: {e}"
    
    def delete_swimmer(self, index):
        try:
            df = self.load_existing_data()
            if df is None or index >= len(df):
                return False, "Nadador no encontrado"
            
            df = df.drop(index=index).reset_index(drop=True)
            df.to_excel(self.archivo_inscripcion, index=False)
            return True, "Nadador eliminado exitosamente"
            
        except Exception as e:
            return False, f"Error al eliminar nadador: {e}"
    
    def get_swimmers_list(self):
        df = self.load_existing_data()
        if df is None or df.empty:
            return []
        
        swimmers = []
        for index, row in df.iterrows():
            events_registered = []
            for event in self.swimming_events:
                if pd.notna(row.get(event)):
                    events_registered.append(f"{event}: {row[event]}")
            
            swimmers.append({
                'index': index,
                'name': row['NOMBRE Y AP'],
                'team': row['EQUIPO'],
                'age': row['EDAD'],
                'category': row['CAT.'],
                'gender': row['SEXO'],
                'events': events_registered
            })
        
        return swimmers
    
    # ===== MÉTODOS PARA BÚSQUEDA EN BASE DE DATOS =====
    
    def load_database(self):
        """Cargar la base de datos desde FPROYECCION 2025T con estructura de múltiples registros por atleta"""
        if not os.path.exists(self.archivo_base_datos):
            return None, f"No se encontró el archivo {self.archivo_base_datos}"
        
        try:
            # Leer con encabezados en la primera fila
            try:
                df = pd.read_excel(self.archivo_base_datos, sheet_name='FPROYECCION 2025T', header=0)
            except:
                # Buscar hoja alternativa
                xl_file = pd.ExcelFile(self.archivo_base_datos)
                target_sheet = None
                for sheet in xl_file.sheet_names:
                    if 'PROYECCION' in sheet.upper() or '2025' in sheet:
                        target_sheet = sheet
                        break
                if target_sheet:
                    df = pd.read_excel(self.archivo_base_datos, sheet_name=target_sheet, header=0)
                else:
                    df = pd.read_excel(self.archivo_base_datos, sheet_name=0, header=0)
            
            return df, f"Base de datos cargada: {len(df)} registros encontrados"
                
        except Exception as e:
            return None, f"Error al cargar base de datos: {e}"
    
    def search_swimmer_in_database(self, search_term):
        """Buscar nadador en la base de datos por nombre"""
        df, message = self.load_database()
        if df is None:
            return [], message
        
        # Buscar en la columna ATLETA
        if 'ATLETA' not in df.columns:
            return [], "No se encontró columna ATLETA en la base de datos"
        
        # Buscar coincidencias
        search_term = search_term.lower().strip()
        mask = df['ATLETA'].astype(str).str.lower().str.contains(search_term, na=False, regex=False)
        matching_rows = df[mask]
        
        # Agrupar por atleta único (pueden tener múltiples registros por diferentes pruebas)
        unique_athletes = matching_rows['ATLETA'].unique()
        
        matches = []
        for athlete_name in unique_athletes:
            # Tomar el primer registro para información básica
            athlete_records = matching_rows[matching_rows['ATLETA'] == athlete_name]
            first_record = athlete_records.iloc[0]
            
            matches.append({
                'index': 0,  # No importante ya que agrupamos
                'name': athlete_name,
                'full_data': first_record,  # Información básica del primer registro
                'all_records': athlete_records  # Todos los registros del atleta
            })
        
        return matches, f"Se encontraron {len(matches)} atletas únicos"
    
    def get_swimmer_latest_times(self, swimmer_data):
        """Obtener los tiempos del nadador agrupando todos sus registros"""
        df, message = self.load_database()
        if df is None:
            return {}, message
        
        # Buscar todos los registros del atleta
        mask = df['ATLETA'].astype(str).str.lower().str.contains(swimmer_data['name'].lower(), na=False, regex=False)
        swimmer_records = df[mask]
        
        if swimmer_records.empty:
            return {}, f"No se encontraron registros para {swimmer_data['name']}"
        
        # Mapear pruebas de la base de datos a eventos del sistema
        prueba_mappings = {
            '50M CROLL': '50m LIBRE',
            '100M CROLL': '100m LIBRE', 
            '200M CROLL': '200m LIBRE',
            '400M CROLL': '400m LIBRE',
            '50M ESPALDA': '50m ESPALDA',
            '100M ESPALDA': '100m ESPALDA',
            '200M ESPALDA': '200m ESPALDA',
            '50M PECHO': '50m PECHO',
            '100M PECHO': '100m PECHO',
            '200M PECHO': '200m PECHO',
            '50M MARIPOSA': '50m MARIPOSA',
            '100M MARIPOSA': '100m MARIPOSA',
            '200M MARIPOSA': '200m MARIPOSA',
            '200M COMBINADO INDIVIDUAL': '200m COMBINADO',
            '400M COMBINADO INDIVIDUAL': '400m COMBINADO'
        }
        
        # Procesar cada registro y extraer tiempos
        times_by_event = {}
        
        for _, record in swimmer_records.iterrows():
            prueba = record.get('PRUEBA', '')
            tiempo = record.get('TIEMPO', '')
            fecha = record.get('F. COMPETENCIA', '')
            
            if pd.notna(prueba) and pd.notna(tiempo):
                prueba_str = str(prueba).strip()
                tiempo_str = str(tiempo).strip()
                
                # Buscar el evento del sistema que coincide
                system_event = None
                for sys_event, db_prueba in prueba_mappings.items():
                    if (prueba_str.upper() == db_prueba.upper() or 
                        prueba_str.upper().replace(' ', '') == db_prueba.upper().replace(' ', '') or
                        db_prueba.upper() in prueba_str.upper()):
                        system_event = sys_event
                        break
                
                if system_event and tiempo_str and tiempo_str not in ['0', '0.0', 'nan']:
                    # Convertir tiempo a formato simple (MM:SS.dd)
                    clean_time = self._clean_time_format(tiempo_str)
                    if clean_time:
                        # Si ya existe un tiempo para este evento, tomar el mejor
                        if system_event in times_by_event:
                            current_time = times_by_event[system_event]['tiempo']
                            if self._compare_times(clean_time, current_time) < 0:  # Nuevo tiempo es mejor
                                times_by_event[system_event] = {
                                    'tiempo': clean_time,
                                    'fecha': fecha,
                                    'prueba_original': prueba_str
                                }
                        else:
                            times_by_event[system_event] = {
                                'tiempo': clean_time,
                                'fecha': fecha,
                                'prueba_original': prueba_str
                            }
        
        # Extraer solo los tiempos para retornar
        latest_times = {event: data['tiempo'] for event, data in times_by_event.items()}
        
        return latest_times, f"Se encontraron {len(latest_times)} tiempos para {swimmer_data['name']}"
    
    def _clean_time_format(self, time_str):
        """Convertir tiempo a formato MM:SS.dd"""
        try:
            time_str = str(time_str).strip()
            
            # Si ya está en formato timestamp (HH:MM:SS.microseconds)
            if ':' in time_str and len(time_str.split(':')) == 3:
                parts = time_str.split(':')
                minutes = int(parts[1])
                seconds_part = parts[2]
                if '.' in seconds_part:
                    secs, microsecs = seconds_part.split('.')
                    return f"{minutes}:{secs}.{microsecs[:2]}"
                else:
                    return f"{minutes}:{seconds_part}.00"
            
            # Si está en formato MM:SS.dd
            elif ':' in time_str:
                return time_str
            
            # Si es solo segundos
            else:
                seconds = float(time_str)
                minutes = int(seconds // 60)
                remaining_secs = seconds % 60
                return f"{minutes}:{remaining_secs:06.3f}"
                
        except:
            return None
    
    def _compare_times(self, time1, time2):
        """Comparar dos tiempos en formato MM:SS.dd. Retorna -1 si time1 < time2, 1 si time1 > time2, 0 si iguales"""
        try:
            def time_to_seconds(time_str):
                if ':' in time_str:
                    parts = time_str.split(':')
                    return int(parts[0]) * 60 + float(parts[1])
                else:
                    return float(time_str)
            
            secs1 = time_to_seconds(time1)
            secs2 = time_to_seconds(time2)
            
            if secs1 < secs2:
                return -1
            elif secs1 > secs2:
                return 1
            else:
                return 0
        except:
            return 0
    
    def get_swimmer_info_from_database(self, swimmer_match):
        """Extraer información completa del nadador de la base de datos"""
        row = swimmer_match['full_data']
        
        # Extraer información básica
        swimmer_info = {
            'name': swimmer_match['name'],
            'team': 'Club TEN',  # Default team
            'age': None,
            'category': '',
            'gender': ''
        }
        
        # Mapeo de columnas comunes en bases de datos de natación
        column_mappings = {
            'equipo': ['equipo', 'club', 'team', 'entidad'],
            'edad': ['edad', 'age', 'años'],
            'categoria': ['cat', 'categoria', 'category', 'cat.'],
            'sexo': ['sexo', 'gender', 'género', 'sex', 'm/f'],
            'nacimiento': ['nacimiento', 'fecha_nac', 'birth', 'nac']
        }
        
        # Buscar información en las columnas
        for col in row.index:
            col_str = str(col).lower().strip()
            valor = row[col]
            
            if pd.notna(valor) and str(valor).strip():
                valor_str = str(valor).strip()
                
                # Equipo/Club
                if any(keyword in col_str for keyword in column_mappings['equipo']):
                    swimmer_info['team'] = valor_str
                
                # Edad - intentar extraer de diferentes formatos
                elif any(keyword in col_str for keyword in column_mappings['edad']):
                    try:
                        # Extraer solo números de la cadena
                        age_match = re.search(r'\d+', valor_str)
                        if age_match:
                            swimmer_info['age'] = int(age_match.group())
                    except:
                        pass
                
                # Categoría
                elif any(keyword in col_str for keyword in column_mappings['categoria']):
                    swimmer_info['category'] = valor_str
                
                # Sexo/Género - normalizar valores
                elif any(keyword in col_str for keyword in column_mappings['sexo']):
                    gender_str = valor_str.upper()
                    if gender_str in ['M', 'MASCULINO', 'HOMBRE', 'MALE']:
                        swimmer_info['gender'] = 'M'
                    elif gender_str in ['F', 'FEMENINO', 'MUJER', 'FEMALE']:
                        swimmer_info['gender'] = 'F'
                    else:
                        swimmer_info['gender'] = gender_str[0] if gender_str else ''
        
        # Intentar inferir edad desde fecha de nacimiento si no hay edad directa
        if not swimmer_info['age']:
            for col in row.index:
                col_str = str(col).lower()
                if any(keyword in col_str for keyword in column_mappings['nacimiento']):
                    try:
                        birth_date = pd.to_datetime(row[col])
                        today = datetime.now()
                        swimmer_info['age'] = today.year - birth_date.year
                        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                            swimmer_info['age'] -= 1
                    except:
                        pass
        
        # Asignar categoría automática si no está disponible pero tenemos edad y género
        if not swimmer_info['category'] and swimmer_info['age'] and swimmer_info['gender']:
            swimmer_info['category'] = self.get_category_by_age(swimmer_info['age'], swimmer_info['gender'])
        
        # Valores por defecto para datos faltantes
        if not swimmer_info['age']:
            swimmer_info['age'] = 12  # Edad por defecto
        if not swimmer_info['gender']:
            swimmer_info['gender'] = 'M'  # Género por defecto
        if not swimmer_info['category']:
            swimmer_info['category'] = self.get_category_by_age(swimmer_info['age'], swimmer_info['gender'])
        
        return swimmer_info
    
    def create_swimmer_from_database(self, swimmer_match):
        """Crear registro de nadador desde la base de datos con sus últimos tiempos"""
        # Obtener información básica
        swimmer_info = self.get_swimmer_info_from_database(swimmer_match)
        
        # Obtener últimos tiempos usando el nuevo método
        latest_times, message = self.get_swimmer_latest_times(swimmer_info)
        
        # Preparar datos para inscripción
        swimmer_data = {
            'name': swimmer_info['name'],
            'team': swimmer_info['team'],
            'age': swimmer_info['age'] or 12,
            'category': swimmer_info['category'] or self.get_category_by_age(swimmer_info['age'] or 12, swimmer_info['gender'] or 'M'),
            'gender': swimmer_info['gender'] or 'M',
            'events': latest_times
        }
        
        return swimmer_data, f"Nadador preparado con {len(latest_times)} pruebas desde la base de datos"
    
    def get_swimmer_for_editing(self, index):
        """Obtener datos de un nadador para edición"""
        df = self.load_existing_data()
        if df is None or index >= len(df):
            return None, "Nadador no encontrado"
        
        row = df.iloc[index]
        
        # Extraer eventos inscritos
        events_data = {}
        for event in self.swimming_events:
            if pd.notna(row.get(event)):
                events_data[event] = str(row[event])
        
        swimmer_data = {
            'name': row['NOMBRE Y AP'],
            'team': row['EQUIPO'],
            'age': int(row['EDAD']),
            'category': row['CAT.'],
            'gender': row['SEXO'],
            'events': events_data
        }
        
        return swimmer_data, "Datos del nadador obtenidos"
    
    def generate_pdf_report(self, swimmers, teams, categories, genders, events_stats):
        """Generar reporte PDF con logo de la empresa"""
        if not REPORTLAB_AVAILABLE:
            print("ReportLab no está instalado en este entorno Python.")
            print("Para generar reportes PDF, ejecute uno de los siguientes comandos:")
            print("  pip install reportlab")
            print("  pip3 install reportlab") 
            print("  python -m pip install reportlab")
            print("  python3 -m pip install reportlab")
            print("\nSi está usando un entorno virtual, asegúrese de activarlo primero.")
            return None
        
        try:
            # Crear buffer para PDF en memoria
            buffer = BytesIO()
            
            # Crear documento PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=72)
            
            # Contenido del PDF
            story = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('CustomTitle',
                                         parent=styles['Heading1'],
                                         fontSize=18,
                                         spaceAfter=30,
                                         alignment=TA_CENTER)
            
            heading_style = ParagraphStyle('CustomHeading',
                                           parent=styles['Heading2'],
                                           fontSize=14,
                                           spaceAfter=12,
                                           alignment=TA_LEFT)
            
            copyright_style = ParagraphStyle('Copyright',
                                             parent=styles['Normal'],
                                             fontSize=8,
                                             alignment=TA_CENTER)
            
            # Agregar logo si existe
            logo_path = 'img/TEN.png'
            if os.path.exists(logo_path):
                try:
                    logo = Image(logo_path, width=2*inch, height=1*inch)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                    story.append(Spacer(1, 20))
                except:
                    pass
            
            # Título del reporte
            story.append(Paragraph("REPORTE DE INSCRIPCIONES", title_style))
            story.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 30))
            
            # Resumen general
            story.append(Paragraph("RESUMEN GENERAL", heading_style))
            summary_data = [
                ["Total de Nadadores", str(len(swimmers))],
                ["Equipos Diferentes", str(len(teams))],
                ["Categorías Activas", str(len(categories))],
                ["Pruebas con Inscripciones", str(len(events_stats))],
                ["Total de Inscripciones en Pruebas", str(sum(events_stats.values()) if events_stats else 0)]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Distribución por género
            story.append(Paragraph("DISTRIBUCIÓN POR GÉNERO", heading_style))
            gender_data = [["Género", "Cantidad", "Porcentaje"]]
            total_swimmers = len(swimmers)
            for gender, count in genders.items():
                percentage = (count / total_swimmers) * 100 if total_swimmers > 0 else 0
                gender_data.append([gender, str(count), f"{percentage:.1f}%"])
            
            gender_table = Table(gender_data, colWidths=[2*inch, 1*inch, 1*inch])
            gender_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(gender_table)
            story.append(Spacer(1, 20))
            
            # Top 5 pruebas más populares
            if events_stats:
                story.append(Paragraph("TOP 5 PRUEBAS MÁS POPULARES", heading_style))
                top_events = sorted(events_stats.items(), key=lambda x: x[1], reverse=True)[:5]
                events_data = [["Posición", "Prueba", "Nadadores"]]
                for i, (event, count) in enumerate(top_events, 1):
                    events_data.append([str(i), event, str(count)])
                
                events_table = Table(events_data, colWidths=[1*inch, 3*inch, 1*inch])
                events_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(events_table)
                story.append(Spacer(1, 20))
            
            # Nueva página para lista de nadadores
            story.append(PageBreak())
            story.append(Paragraph("LISTA COMPLETA DE NADADORES", title_style))
            story.append(Spacer(1, 20))
            
            # Tabla de nadadores
            swimmers_data = [["#", "Nombre", "Equipo", "Edad", "Categoría", "Sexo", "Pruebas"]]
            for i, swimmer in enumerate(swimmers, 1):
                events_count = len(swimmer['events'])
                gender_label = "Masculino" if swimmer['gender'] == 'M' else "Femenino"
                swimmers_data.append([
                    str(i),
                    swimmer['name'],
                    swimmer['team'],
                    str(swimmer['age']),
                    swimmer['category'],
                    gender_label,
                    str(events_count)
                ])
            
            swimmers_table = Table(swimmers_data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 0.7*inch, 1*inch, 0.8*inch, 0.7*inch])
            swimmers_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(swimmers_table)
            story.append(Spacer(1, 30))
            
            # Copyright footer
            story.append(Paragraph("Sistema de Gestión de Competencias de Natación - Todos los derechos reservados", copyright_style))
            
            # Generar PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            print(f"Error generando PDF: {str(e)}")
            return None
    
    def bulk_import_from_excel(self, uploaded_file):
        """Importa múltiples nadadores desde un archivo Excel"""
        try:
            # Leer archivo Excel
            df = pd.read_excel(uploaded_file)
            
            # Validar columnas requeridas
            required_columns = ['NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f"Faltan columnas requeridas: {', '.join(missing_columns)}"
            
            # Filtrar filas con datos válidos
            df = df.dropna(subset=['NOMBRE Y AP'])
            
            if len(df) == 0:
                return False, "No se encontraron nadadores válidos en el archivo"
            
            imported_swimmers = []
            errors = []
            duplicates = []
            
            # Procesar cada nadador
            for index, row in df.iterrows():
                try:
                    swimmer_name = str(row['NOMBRE Y AP']).strip()
                    if not swimmer_name or swimmer_name.lower() == 'nan':
                        continue
                        
                    # Datos básicos del nadador
                    team = str(row['EQUIPO']).strip() if pd.notna(row['EQUIPO']) else ""
                    age = int(row['EDAD']) if pd.notna(row['EDAD']) else 0
                    category = str(row['CAT.']).strip() if pd.notna(row['CAT.']) else ""
                    gender = str(row['SEXO']).strip().upper() if pd.notna(row['SEXO']) else ""
                    
                    # Validar datos básicos
                    if age <= 0:
                        errors.append(f"Fila {index + 2}: Edad inválida para {swimmer_name}")
                        continue
                    
                    if gender not in ['M', 'F']:
                        errors.append(f"Fila {index + 2}: Sexo debe ser M o F para {swimmer_name}")
                        continue
                    
                    # Auto-generar categoría si no se proporciona
                    if not category:
                        category = self.get_category_by_age(age, gender)
                    
                    # Verificar si ya existe el nadador
                    if os.path.exists(self.archivo_inscripcion):
                        existing_df = pd.read_excel(self.archivo_inscripcion)
                        if swimmer_name.lower() in existing_df['NOMBRE Y AP'].str.lower().values:
                            duplicates.append(swimmer_name)
                            continue
                    
                    # Procesar tiempos de las pruebas
                    events_data = {}
                    for event in self.swimming_events:
                        if event in df.columns and pd.notna(row[event]):
                            time_value = row[event]
                            # Convertir a string si es numérico
                            if isinstance(time_value, (int, float)):
                                time_str = f"{int(time_value//60):02d}:{time_value%60:05.2f}"
                            else:
                                time_str = str(time_value).strip()
                            
                            # Validar formato de tiempo
                            if self.validate_time_format(time_str):
                                events_data[event] = time_str
                    
                    # Solo agregar nadadores con al menos una prueba
                    if events_data:
                        # Crear nuevo nadador
                        new_swimmer = {
                            'NOMBRE Y AP': swimmer_name,
                            'EQUIPO': team,
                            'EDAD': age,
                            'CAT.': category,
                            'SEXO': gender,
                            **{event: events_data.get(event, "") for event in self.swimming_events}
                        }
                        
                        imported_swimmers.append(new_swimmer)
                    else:
                        errors.append(f"Fila {index + 2}: {swimmer_name} no tiene pruebas válidas")
                        
                except Exception as e:
                    errors.append(f"Fila {index + 2}: Error procesando datos - {str(e)}")
                    continue
            
            # Guardar nadadores importados
            if imported_swimmers:
                success = self.save_swimmers_to_excel(imported_swimmers)
                if success:
                    result_msg = f"✅ Se importaron {len(imported_swimmers)} nadadores correctamente"
                    
                    if duplicates:
                        result_msg += f"\n⚠️ Se omitieron {len(duplicates)} nadadores duplicados: {', '.join(duplicates[:3])}"
                        if len(duplicates) > 3:
                            result_msg += f" y {len(duplicates) - 3} más"
                    
                    if errors:
                        result_msg += f"\n❌ {len(errors)} errores encontrados"
                        if len(errors) <= 5:
                            result_msg += f":\n• " + "\n• ".join(errors)
                        else:
                            result_msg += f":\n• " + "\n• ".join(errors[:5]) + f"\n• ... y {len(errors) - 5} errores más"
                    
                    return True, result_msg
                else:
                    return False, "Error guardando los datos importados"
            else:
                return False, f"No se pudo importar ningún nadador. Errores:\n• " + "\n• ".join(errors[:10])
                
        except Exception as e:
            return False, f"Error leyendo el archivo: {str(e)}"
    
    def save_swimmers_to_excel(self, swimmers_data):
        """Guarda múltiples nadadores al archivo Excel"""
        try:
            # Cargar datos existentes o crear nuevo DataFrame
            if os.path.exists(self.archivo_inscripcion):
                existing_df = pd.read_excel(self.archivo_inscripcion)
                new_df = pd.DataFrame(swimmers_data)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = pd.DataFrame(swimmers_data)
            
            # Asegurar que todas las columnas estén presentes
            all_columns = ['NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO'] + self.swimming_events
            for col in all_columns:
                if col not in combined_df.columns:
                    combined_df[col] = ""
            
            # Reordenar columnas
            combined_df = combined_df[all_columns]
            
            # Guardar archivo
            combined_df.to_excel(self.archivo_inscripcion, index=False)
            return True
            
        except Exception as e:
            print(f"Error guardando nadadores: {str(e)}")
            return False
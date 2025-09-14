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
        # Importar el gestor de eventos
        try:
            from event_manager import EventManager
            self.event_manager = EventManager()
        except ImportError:
            self.event_manager = None
        
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
        """Determinar categoría basada en la edad, usando las categorías del evento si están disponibles"""
        age = int(age)

        # Si tenemos event manager configurado, usar las categorías del evento
        if self.event_manager:
            event_categories = self.get_event_categories()
            if event_categories:
                # Buscar la categoría correspondiente en las configuradas para el evento
                for category in event_categories:
                    category_name = category.get('name', '')
                    age_range = category.get('age_range', '')

                    if age_range:
                        # Parsear el rango de edad
                        min_age, max_age = self.event_manager.parse_age_range(age_range)
                        if min_age is not None and max_age is not None:
                            if min_age <= age <= max_age:
                                return category_name

                # Si no encuentra coincidencia en las categorías del evento, informar
                return f"EDAD {age} NO CONFIGURADA"

        # Lógica de categorías por defecto (fallback)
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
            
        # Normalizar el formato: coma a punto, eliminar espacios
        time_str = str(time_str).strip().replace(',', '.')
        
        # Manejar casos especiales de Excel
        if time_str.lower() in ['nan', 'none', 'null']:
            return True, None
        
        try:
            # Formato MM:SS.dd o M:SS.dd
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    minutes = int(float(parts[0]))  # Usar float primero por si hay decimales
                    seconds = float(parts[1])
                    if 0 <= minutes <= 59 and 0 <= seconds < 60:
                        # Formatear consistentemente
                        formatted_time = f"{minutes:02d}:{seconds:05.2f}"
                        return True, formatted_time
            
            # Formato solo segundos (SS.dd o SSS.dd)
            else:
                total_seconds = float(time_str)
                if 0 <= total_seconds <= 3600:  # Máximo 1 hora
                    # Convertir a formato MM:SS.dd si es mayor a 60 segundos
                    if total_seconds >= 60:
                        minutes = int(total_seconds // 60)
                        seconds = total_seconds % 60
                        formatted_time = f"{minutes:02d}:{seconds:05.2f}"
                    else:
                        formatted_time = f"00:{total_seconds:05.2f}"
                    return True, formatted_time
                    
        except (ValueError, TypeError) as e:
            # Log del error para debugging
            pass
            
        return False, f"Formato de tiempo inválido: '{time_str}'. Use MM:SS,dd o MM:SS.dd"
    
    def load_existing_data(self):
        if os.path.exists(self.archivo_inscripcion):
            try:
                df = pd.read_excel(self.archivo_inscripcion)
                return df
            except Exception as e:
                print(f"Error al cargar datos existentes: {e}")
                return None
        return None
    
    def get_available_events(self):
        """Obtener las pruebas disponibles para el evento"""
        if self.event_manager:
            selected_events = self.event_manager.get_selected_events()
            if selected_events:
                return selected_events
        return self.swimming_events

    def get_available_events_for_swimmer_category(self, category_name):
        """Obtener las pruebas disponibles para un nadador según su categoría"""
        if self.event_manager:
            return self.event_manager.get_available_events_for_swimmer(category_name)
        return self.get_available_events()

    def get_event_categories(self):
        """Obtener las categorías configuradas para el evento"""
        if self.event_manager:
            return self.event_manager.get_categories()
        return [{'name': cat, 'age_range': ''} for cat in self.categories]

    def find_swimmer_category_by_age_and_gender(self, age, gender):
        """Buscar la categoría apropiada para un nadador basándose en edad y género"""
        if self.event_manager:
            event_categories = self.event_manager.get_categories()

            # Si hay categorías configuradas en el evento, intentar encontrar una que coincida
            for category in event_categories:
                # Si la categoría tiene rango de edad específico, intentar parsearlo
                age_range = category.get('age_range', '').strip()
                if age_range and self._age_matches_range(age, age_range):
                    return category['name']

            # Si no se encuentra coincidencia específica, retornar la primera categoría como fallback
            if event_categories:
                return event_categories[0]['name']

        # Fallback al sistema tradicional de categorías por edad/género
        return self.get_category_by_age(age, gender)

    def _age_matches_range(self, age, age_range):
        """Verificar si una edad coincide con un rango de edad textual"""
        try:
            # Buscar patrones como "12-13", "12 a 13", "12-13 años", etc.
            import re

            # Patrón para rango: "12-13", "12 a 13", "12 - 13"
            range_pattern = r'(\d+)[\s]*[-aA]\s*(\d+)'
            match = re.search(range_pattern, age_range)

            if match:
                min_age = int(match.group(1))
                max_age = int(match.group(2))
                return min_age <= age <= max_age

            # Patrón para edad específica: "12", "12 años"
            single_pattern = r'(\d+)'
            match = re.search(single_pattern, age_range)

            if match:
                target_age = int(match.group(1))
                return age == target_age

        except (ValueError, AttributeError):
            pass

        return False

    def create_empty_registration_file(self):
        available_events = self.get_available_events()
        columns = ['NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO'] + available_events
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

        available_events = self.get_available_events()
        swimmers = []
        for index, row in df.iterrows():
            events_registered = []
            for event in available_events:
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
        """Cargar la base de datos desde FPROYECCION 2025T y M. PROYECCION 2025 combinadas"""
        if not os.path.exists(self.archivo_base_datos):
            return None, f"No se encontró el archivo {self.archivo_base_datos}"
        
        try:
            dfs_to_combine = []
            sheets_loaded = []
            
            # Hojas objetivo (femenino y masculino)
            target_sheets = ['FPROYECCION 2025T', 'M. PROYECCION 2025']
            
            xl_file = pd.ExcelFile(self.archivo_base_datos)
            
            for sheet_name in target_sheets:
                try:
                    if sheet_name in xl_file.sheet_names:
                        df_sheet = pd.read_excel(self.archivo_base_datos, sheet_name=sheet_name, header=0)
                        
                        # Filtrar columnas relevantes (evitar duplicaciones)
                        relevant_columns = ['ATLETA', 'EQUIPO', 'CATEGORIA', 'SEXO', 'EDAD', 'PRUEBA', 'TIEMPO', 'F. COMPETENCIA']
                        available_columns = [col for col in relevant_columns if col in df_sheet.columns]
                        
                        if available_columns and len(df_sheet) > 0:
                            df_filtered = df_sheet[available_columns].copy()
                            dfs_to_combine.append(df_filtered)
                            sheets_loaded.append(sheet_name)
                except Exception as e:
                    print(f"Error al cargar hoja {sheet_name}: {e}")
                    continue
            
            # Si no se pudieron cargar las hojas objetivo, buscar alternativas
            if not dfs_to_combine:
                for sheet in xl_file.sheet_names:
                    if any(keyword in sheet.upper() for keyword in ['PROYECCION', '2025', 'FPROYECCION']):
                        try:
                            df = pd.read_excel(self.archivo_base_datos, sheet_name=sheet, header=0)
                            if 'ATLETA' in df.columns:
                                dfs_to_combine.append(df)
                                sheets_loaded.append(sheet)
                                break
                        except:
                            continue
            
            # Combinar las hojas cargadas
            if dfs_to_combine:
                combined_df = pd.concat(dfs_to_combine, ignore_index=True)
                # Eliminar duplicados basados en atleta, prueba y tiempo
                combined_df = combined_df.drop_duplicates(subset=['ATLETA', 'PRUEBA', 'TIEMPO'], keep='first')
                
                return combined_df, f"Base de datos cargada: {len(combined_df)} registros de {len(sheets_loaded)} hojas ({', '.join(sheets_loaded)})"
            else:
                return None, "No se pudieron cargar datos de las hojas de la base de datos"
                
        except Exception as e:
            return None, f"Error al cargar base de datos: {e}"
    
    def search_swimmer_in_database(self, search_term):
        """Buscar nadador en la base de datos por nombre, filtrando por categorías del evento"""
        df, message = self.load_database()
        if df is None:
            return [], message

        # Buscar en la columna ATLETA
        if 'ATLETA' not in df.columns:
            return [], "No se encontró columna ATLETA en la base de datos"

        # Buscar coincidencias por nombre
        search_term = search_term.lower().strip()
        name_mask = df['ATLETA'].astype(str).str.lower().str.contains(search_term, na=False, regex=False)
        matching_rows = df[name_mask]

        # Obtener categorías configuradas en el evento
        event_categories = self.get_event_categories()
        if event_categories and self.event_manager:
            # Extraer nombres de las categorías del evento
            event_category_names = [cat['name'] for cat in event_categories]

            # Filtrar por categorías del evento si están configuradas
            if 'CATEGORIA' in df.columns:
                category_mask = matching_rows['CATEGORIA'].isin(event_category_names)
                matching_rows = matching_rows[category_mask]

                if matching_rows.empty:
                    return [], f"No se encontraron nadadores de '{search_term}' en las categorías del evento: {', '.join(event_category_names)}"

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

        total_message = f"Se encontraron {len(matches)} atletas únicos"
        if event_categories and self.event_manager:
            event_category_names = [cat['name'] for cat in event_categories]
            total_message += f" en las categorías: {', '.join(event_category_names)}"

        return matches, total_message
    
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
        # Usamos mapeo directo ya que los nombres deben coincidir exactamente
        prueba_mappings = {
            '50M CROLL': '50M CROLL',
            '100M CROLL': '100M CROLL',
            '200M CROLL': '200M CROLL',
            '400M CROLL': '400M CROLL',
            '50M ESPALDA': '50M ESPALDA',
            '100M ESPALDA': '100M ESPALDA',
            '200M ESPALDA': '200M ESPALDA',
            '50M PECHO': '50M PECHO',
            '100M PECHO': '100M PECHO',
            '200M PECHO': '200M PECHO',
            '50M MARIPOSA': '50M MARIPOSA',
            '100M MARIPOSA': '100M MARIPOSA',
            '200M MARIPOSA': '200M MARIPOSA',
            '200M COMBINADO INDIVIDUAL': '200M COMBINADO INDIVIDUAL',
            '400M COMBINADO INDIVIDUAL': '400M COMBINADO INDIVIDUAL',
            # Mapeos adicionales para variaciones en la base de datos
            '50M LIBRE': '50M CROLL',
            '100M LIBRE': '100M CROLL',
            '200M LIBRE': '200M CROLL',
            '400M LIBRE': '400M CROLL',
            '200M COMBINADO': '200M COMBINADO INDIVIDUAL',
            '400M COMBINADO': '400M COMBINADO INDIVIDUAL'
        }

        # Obtener pruebas disponibles del evento
        available_events = self.get_available_events()

        # Si tenemos categoría del nadador, filtrar por pruebas de la categoría
        swimmer_category = swimmer_data.get('category')
        if swimmer_category:
            category_events = self.get_available_events_for_swimmer_category(swimmer_category)
            if category_events:
                available_events = category_events

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
                prueba_upper = prueba_str.upper().strip()

                # Primero buscar coincidencia exacta en el mapeo
                if prueba_upper in prueba_mappings:
                    system_event = prueba_mappings[prueba_upper]
                else:
                    # Buscar coincidencias aproximadas
                    for db_prueba, sys_event_mapped in prueba_mappings.items():
                        if (prueba_upper == db_prueba.upper() or
                            prueba_upper.replace(' ', '') == db_prueba.upper().replace(' ', '')):
                            system_event = sys_event_mapped
                            break

                # Solo incluir si el evento está disponible en el evento actual
                if system_event and system_event in available_events and tiempo_str and tiempo_str not in ['0', '0.0', 'nan']:
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
            swimmer_info['category'] = self.find_swimmer_category_by_age_and_gender(swimmer_info['age'], swimmer_info['gender'])
        
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
            'category': swimmer_info['category'] or self.find_swimmer_category_by_age_and_gender(swimmer_info['age'] or 12, swimmer_info['gender'] or 'M'),
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
        available_events = self.get_available_events()

        # Extraer eventos inscritos
        events_data = {}
        for event in available_events:
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
            # Colores del logo TEN (azul corporativo)
            TEN_BLUE = colors.HexColor('#1E88E5')  # Azul principal del logo
            TEN_LIGHT_BLUE = colors.HexColor('#64B5F6')  # Azul claro del gradiente
            TEN_DARK_BLUE = colors.HexColor('#1565C0')  # Azul oscuro
            TEN_ACCENT = colors.HexColor('#E3F2FD')  # Azul muy claro para fondos
            
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
                                         alignment=TA_CENTER,
                                         textColor=TEN_DARK_BLUE)
            
            heading_style = ParagraphStyle('CustomHeading',
                                           parent=styles['Heading2'],
                                           fontSize=14,
                                           spaceAfter=12,
                                           alignment=TA_LEFT,
                                           textColor=TEN_BLUE)
            
            copyright_style = ParagraphStyle('Copyright',
                                             parent=styles['Normal'],
                                             fontSize=8,
                                             alignment=TA_CENTER,
                                             textColor=TEN_DARK_BLUE)
            
            # Agregar logo si existe (mantener proporciones originales)
            logo_path = 'img/TEN.png'
            if os.path.exists(logo_path):
                try:
                    # Cargar logo con proporciones originales
                    from PIL import Image as PILImage
                    pil_img = PILImage.open(logo_path)
                    original_width, original_height = pil_img.size
                    aspect_ratio = original_width / original_height
                    
                    # Definir altura deseada y calcular ancho proporcional
                    desired_height = 1*inch
                    desired_width = desired_height * aspect_ratio
                    
                    logo = Image(logo_path, width=desired_width, height=desired_height)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                    story.append(Spacer(1, 20))
                except Exception as e:
                    # Fallback a dimensiones fijas si hay error
                    logo = Image(logo_path, width=2*inch, height=1*inch)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                    story.append(Spacer(1, 20))
            
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
                ('BACKGROUND', (0, 0), (-1, 0), TEN_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), TEN_ACCENT),
                ('GRID', (0, 0), (-1, -1), 1, TEN_DARK_BLUE)
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
                ('BACKGROUND', (0, 0), (-1, 0), TEN_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), TEN_ACCENT),
                ('GRID', (0, 0), (-1, -1), 1, TEN_DARK_BLUE)
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
                    ('BACKGROUND', (0, 0), (-1, 0), TEN_BLUE),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), TEN_ACCENT),
                    ('GRID', (0, 0), (-1, -1), 1, TEN_DARK_BLUE)
                ]))
                story.append(events_table)
                story.append(Spacer(1, 20))
            
            # Nueva página para lista detallada de nadadores
            story.append(PageBreak())
            story.append(Paragraph("PLANILLA DETALLADA DE INSCRIPCIONES", title_style))
            story.append(Spacer(1, 20))
            
            # Generar reporte detallado por nadador
            for i, swimmer in enumerate(swimmers, 1):
                # Información básica del nadador
                swimmer_info_style = ParagraphStyle(
                    'SwimmerInfo',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=TEN_DARK_BLUE,
                    fontName='Helvetica-Bold',
                    spaceAfter=8
                )
                
                gender_label = "Masculino" if swimmer['gender'] == 'M' else "Femenino"
                story.append(Paragraph(f"<b>{i}. {swimmer['name']}</b>", swimmer_info_style))
                
                # Datos básicos en tabla
                basic_data = [
                    ["Equipo:", swimmer['team']],
                    ["Edad:", f"{swimmer['age']} años"],
                    ["Categoría:", swimmer['category']],
                    ["Sexo:", gender_label]
                ]
                
                basic_table = Table(basic_data, colWidths=[1.2*inch, 3*inch])
                basic_table.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('TEXTCOLOR', (0, 0), (0, -1), TEN_DARK_BLUE),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5)
                ]))
                story.append(basic_table)
                story.append(Spacer(1, 10))
                
                # Pruebas inscritas
                if swimmer['events']:
                    story.append(Paragraph("<b>Pruebas Inscritas:</b>", ParagraphStyle('EventsHeader', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', textColor=TEN_BLUE)))
                    
                    events_data = [["Prueba", "Tiempo de Inscripción"]]
                    for event_string in swimmer['events']:
                        if ':' in event_string:
                            event_name, event_time = event_string.split(':', 1)
                            events_data.append([event_name.strip(), event_time.strip()])
                        else:
                            events_data.append([event_string, "Sin tiempo"])
                    
                    events_table = Table(events_data, colWidths=[3*inch, 1.5*inch])
                    events_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), TEN_BLUE),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('TOPPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), TEN_ACCENT),
                        ('GRID', (0, 0), (-1, -1), 1, TEN_DARK_BLUE),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8)
                    ]))
                    story.append(events_table)
                else:
                    story.append(Paragraph("<i>Sin pruebas registradas</i>", ParagraphStyle('NoEvents', parent=styles['Normal'], fontSize=9, textColor=TEN_LIGHT_BLUE, fontStyle='italic')))
                
                # Separador entre nadadores
                story.append(Spacer(1, 15))
                if i < len(swimmers):  # No agregar línea después del último nadador
                    story.append(Table([[""], [""]], colWidths=[7*inch], rowHeights=[0.5, 0.5]))
                    story.append(Spacer(1, 10))
            
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

            # Obtener pruebas disponibles del evento
            available_events = self.get_available_events()

            imported_swimmers = []
            errors = []
            duplicates = []
            imported_names = []

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
                        category = self.find_swimmer_category_by_age_and_gender(age, gender)

                    # Verificar si ya existe el nadador
                    if os.path.exists(self.archivo_inscripcion):
                        existing_df = pd.read_excel(self.archivo_inscripcion)
                        if swimmer_name.lower() in existing_df['NOMBRE Y AP'].str.lower().values:
                            duplicates.append(swimmer_name)
                            errors.append(f"Fila {index + 2}: {swimmer_name} ya existe en la base de datos")
                            continue

                    # Procesar tiempos de las pruebas (solo las disponibles en el evento)
                    events_data = {}
                    for event in available_events:
                        if event in df.columns and pd.notna(row[event]):
                            time_value = row[event]

                            # Convertir a string y normalizar formato
                            if isinstance(time_value, (int, float)):
                                # Si es numérico (segundos totales), convertir a MM:SS.CS
                                time_str = f"{int(time_value//60):02d}:{time_value%60:05.2f}"
                            else:
                                # Si es texto, normalizar formato (coma a punto)
                                time_str = str(time_value).strip().replace(',', '.')

                            # Validar formato de tiempo
                            is_valid, validated_time = self.validate_time_format(time_str)
                            if is_valid:
                                events_data[event] = validated_time
                            else:
                                # Agregar información de error más específica
                                errors.append(f"Fila {index + 2}: Formato de tiempo inválido '{time_value}' en {event} para {swimmer_name}")

                    # Solo agregar nadadores con al menos una prueba
                    if events_data:
                        # Crear nuevo nadador
                        new_swimmer = {
                            'NOMBRE Y AP': swimmer_name,
                            'EQUIPO': team,
                            'EDAD': age,
                            'CAT.': category,
                            'SEXO': gender,
                            **{event: events_data.get(event, "") for event in available_events}
                        }

                        imported_swimmers.append(new_swimmer)
                        imported_names.append(swimmer_name)
                    else:
                        errors.append(f"Fila {index + 2}: {swimmer_name} no tiene pruebas válidas")

                except Exception as e:
                    errors.append(f"Fila {index + 2}: Error procesando datos - {str(e)}")
                    continue

            # Determinar el resultado final
            total_processed = len(imported_swimmers) + len(duplicates) + (len(errors) - len(duplicates))

            if imported_swimmers:
                # Hay nadadores para importar
                success = self.save_swimmers_to_excel(imported_swimmers)
                if success:
                    result_msg = f"✅ **Importación exitosa:** {len(imported_swimmers)} nadadores agregados"

                    # Mostrar nadadores importados
                    result_msg += f"\n\n📝 **Nadadores AGREGADOS ({len(imported_names)}):**"
                    if len(imported_names) <= 10:
                        result_msg += f"\n• " + "\n• ".join(imported_names)
                    else:
                        result_msg += f"\n• " + "\n• ".join(imported_names[:10])
                        result_msg += f"\n• ... y {len(imported_names) - 10} más"

                    # Mostrar duplicados omitidos
                    if duplicates:
                        result_msg += f"\n\n⚠️ **Duplicados OMITIDOS ({len(duplicates)}):**"
                        if len(duplicates) <= 10:
                            result_msg += f"\n• " + "\n• ".join(duplicates)
                        else:
                            result_msg += f"\n• " + "\n• ".join(duplicates[:10])
                            result_msg += f"\n• ... y {len(duplicates) - 10} más"

                    # Mostrar otros errores
                    if len(errors) > len(duplicates):  # Hay otros errores además de duplicados
                        other_errors = [e for e in errors if "ya existe en la base de datos" not in e]
                        if other_errors:
                            result_msg += f"\n❌ **Errores adicionales ({len(other_errors)}):**"
                            if len(other_errors) <= 3:
                                result_msg += f"\n• " + "\n• ".join(other_errors)
                            else:
                                result_msg += f"\n• " + "\n• ".join(other_errors[:3]) + f"\n• ... y {len(other_errors) - 3} más"

                    return True, result_msg
                else:
                    return False, "Error guardando los datos importados"

            elif duplicates and len(errors) == len(duplicates):
                # Solo hay duplicados, ningún nadador nuevo
                result_msg = f"⚠️ **Todos los nadadores ya existen en la base de datos**"
                result_msg += f"\n\n📋 **Duplicados detectados ({len(duplicates)}):**"
                if len(duplicates) <= 10:
                    result_msg += f"\n• " + "\n• ".join(duplicates)
                else:
                    result_msg += f"\n• " + "\n• ".join(duplicates[:10])
                    result_msg += f"\n• ... y {len(duplicates) - 10} más"
                return False, result_msg

            else:
                # Solo errores, sin duplicados o con otros errores
                return False, f"❌ No se pudo importar ningún nadador. Errores encontrados:\n• " + "\n• ".join(errors[:10])

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
            available_events = self.get_available_events()
            all_columns = ['NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO'] + available_events
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
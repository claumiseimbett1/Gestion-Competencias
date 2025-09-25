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
        
    def calculate_age_by_criteria(self, birth_date, reference_date=None, criteria='event_date'):
        """Calcular edad según el criterio configurado"""
        if not birth_date or pd.isna(birth_date):
            return None

        try:
            from datetime import datetime, date

            # Convertir birth_date a datetime si es necesario
            if isinstance(birth_date, str):
                # Probar diferentes formatos de fecha
                date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
                birth_datetime = None
                for fmt in date_formats:
                    try:
                        birth_datetime = datetime.strptime(birth_date, fmt)
                        break
                    except ValueError:
                        continue
                if not birth_datetime:
                    return None
                birth_date = birth_datetime.date()
            elif hasattr(birth_date, 'date'):
                birth_date = birth_date.date()
            elif not isinstance(birth_date, date):
                return None

            # Determinar fecha de referencia según el criterio
            if criteria == 'december_31':
                # Edad al 31 de diciembre del año del evento
                if reference_date:
                    if hasattr(reference_date, 'year'):
                        reference_year = reference_date.year
                    else:
                        reference_year = datetime.now().year
                else:
                    reference_year = datetime.now().year
                reference_date = date(reference_year, 12, 31)
            else:
                # Edad el día del evento (por defecto)
                if not reference_date:
                    reference_date = date.today()
                elif hasattr(reference_date, 'date'):
                    reference_date = reference_date.date()

            # Calcular edad
            age = reference_date.year - birth_date.year
            if reference_date.month < birth_date.month or \
               (reference_date.month == birth_date.month and reference_date.day < birth_date.day):
                age -= 1

            return age

        except Exception as e:
            print(f"Error calculando edad: {e}")
            return None

    def _get_swimmer_events_dict(self, swimmer):
        """Helper method to get swimmer events as dict, handling both dict and list formats"""
        events = swimmer.get('events', {})
        if isinstance(events, dict):
            return events
        elif isinstance(events, list):
            # Convert list format to dict format
            events_dict = {}
            for item in events:
                if isinstance(item, dict) and 'event' in item and 'time' in item:
                    events_dict[item['event']] = item['time']
                elif isinstance(item, str) and ':' in item:
                    # Handle format "event: time"
                    parts = item.split(':', 1)
                    if len(parts) == 2:
                        events_dict[parts[0].strip()] = parts[1].strip()
            return events_dict
        else:
            return {}

    def _get_swimmer_events_list(self, swimmer):
        """Helper method to get list of events with times, handling both dict and list formats"""
        events_dict = self._get_swimmer_events_dict(swimmer)
        return [event for event, time in events_dict.items() if time and str(time).strip()]

    def _get_medal_explanation(self, participants):
        """Helper method to get explanation of medal allocation based on participant count"""
        if participants >= 3:
            return "3+ participantes: Oro, Plata y Bronce"
        elif participants == 2:
            return "2 participantes: Oro y Plata únicamente"
        elif participants == 1:
            return "1 participante: Solo Oro"
        else:
            return "Sin participantes: Sin medallas"

    def get_category_by_age(self, age, gender, birth_date=None):
        """Determinar categoría basada en la edad, usando las categorías del evento si están disponibles"""

        # Si tenemos fecha de nacimiento y event manager, calcular edad según criterio
        if birth_date and self.event_manager:
            event_info = self.event_manager.get_event_info()
            if event_info:
                age_criteria = event_info.get('age_criteria', 'event_date')
                event_start_date = None
                if event_info.get('start_date'):
                    try:
                        from datetime import datetime
                        event_start_date = datetime.fromisoformat(event_info['start_date']).date()
                    except:
                        pass

                calculated_age = self.calculate_age_by_criteria(birth_date, event_start_date, age_criteria)
                if calculated_age:
                    age = calculated_age

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

    def get_available_events_for_swimmer_category(self, category_name, swimmer_age=None):
        """Obtener las pruebas disponibles para un nadador según su categoría y edad"""
        if self.event_manager:
            return self.event_manager.get_available_events_for_swimmer(category_name, swimmer_age)
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
        columns = ['NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO', 'FECHA DE NA'] + available_events
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
                    'gender': row['SEXO'],
                    'birth_date': row.get('FECHA DE NA', '')
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
                'SEXO': swimmer_data['gender'],
                'FECHA DE NA': swimmer_data.get('birth_date', '')
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
            df.loc[index, 'FECHA DE NA'] = swimmer_data.get('birth_date', '')
            
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
                'birth_date': row.get('FECHA DE NA', ''),
                'events': events_registered
            })

        return swimmers
    
    # ===== MÉTODOS PARA REPORTES =====

    def generate_team_report(self):
        """Generar reporte detallado de inscripciones por equipo"""
        swimmers = self.get_swimmers_list()
        if not swimmers:
            return None, "No hay nadadores inscritos"

        try:
            # Agrupar nadadores por equipo
            teams_data = {}

            for swimmer in swimmers:
                team_name = swimmer['team']
                if team_name not in teams_data:
                    teams_data[team_name] = {
                        'swimmers': [],
                        'total_swimmers': 0,
                        'categories': {},
                        'genders': {'M': 0, 'F': 0},
                        'total_events': 0
                    }

                # Agregar nadador al equipo
                teams_data[team_name]['swimmers'].append(swimmer)
                teams_data[team_name]['total_swimmers'] += 1

                # Contar categorías
                category = swimmer['category']
                teams_data[team_name]['categories'][category] = teams_data[team_name]['categories'].get(category, 0) + 1

                # Contar géneros
                teams_data[team_name]['genders'][swimmer['gender']] += 1

                # Contar eventos del nadador
                swimmer_events = self._get_swimmer_events_list(swimmer)
                teams_data[team_name]['total_events'] += len(swimmer_events)

            # Ordenar equipos por número de nadadores (descendente)
            sorted_teams = dict(sorted(teams_data.items(), key=lambda x: x[1]['total_swimmers'], reverse=True))

            return sorted_teams, f"Reporte generado para {len(sorted_teams)} equipos"

        except Exception as e:
            return None, f"Error generando reporte: {e}"

    def export_team_report_to_excel(self, teams_data):
        """Exportar reporte de equipos a Excel"""
        if not teams_data:
            return None, "No hay datos para exportar"

        try:
            import pandas as pd
            from io import BytesIO

            # Crear buffer para Excel
            buffer = BytesIO()

            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Hoja de resumen por equipos
                summary_data = []
                for team_name, team_info in teams_data.items():
                    summary_data.append({
                        'Equipo': team_name,
                        'Total Nadadores': team_info['total_swimmers'],
                        'Masculino': team_info['genders']['M'],
                        'Femenino': team_info['genders']['F'],
                        'Total Inscripciones': team_info['total_events'],
                        'Categorías': ', '.join(team_info['categories'].keys())
                    })

                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Resumen por Equipos', index=False)

                # Hoja detallada de nadadores por equipo
                detailed_data = []
                for team_name, team_info in teams_data.items():
                    for swimmer in team_info['swimmers']:
                        # Obtener eventos inscritos
                        events_list = []
                        events_data = self._get_swimmer_events_dict(swimmer)
                        for event, time in events_data.items():
                            if time and time.strip():
                                events_list.append(f"{event}: {time}")

                        detailed_data.append({
                            'Equipo': team_name,
                            'Nadador': swimmer['name'],
                            'Edad': swimmer['age'],
                            'Categoría': swimmer['category'],
                            'Sexo': 'Masculino' if swimmer['gender'] == 'M' else 'Femenino',
                            'Eventos Inscritos': '; '.join(events_list),
                            'Total Eventos': len(events_list)
                        })

                detailed_df = pd.DataFrame(detailed_data)
                detailed_df.to_excel(writer, sheet_name='Detalle de Nadadores', index=False)

            buffer.seek(0)
            return buffer.getvalue(), "reporte_equipos.xlsx"

        except Exception as e:
            return None, f"Error exportando a Excel: {e}"

    def preview_team_report(self):
        """Generar previsualización del reporte de equipos"""
        swimmers = self.get_swimmers_list()
        if not swimmers:
            return None, "No hay nadadores inscritos"

        try:
            # Agrupar nadadores por equipo
            teams_data = {}

            for swimmer in swimmers:
                team_name = swimmer['team']
                if team_name not in teams_data:
                    teams_data[team_name] = {
                        'swimmers': [],
                        'total_swimmers': 0,
                        'categories': {},
                        'genders': {'M': 0, 'F': 0},
                        'total_events': 0
                    }

                teams_data[team_name]['swimmers'].append(swimmer)
                teams_data[team_name]['total_swimmers'] += 1

                # Contar por categoría
                category = swimmer['category']
                if category not in teams_data[team_name]['categories']:
                    teams_data[team_name]['categories'][category] = 0
                teams_data[team_name]['categories'][category] += 1

                # Contar géneros
                teams_data[team_name]['genders'][swimmer['gender']] += 1

                # Contar eventos del nadador
                swimmer_events = self._get_swimmer_events_list(swimmer)
                teams_data[team_name]['total_events'] += len(swimmer_events)

            # Ordenar equipos por número de nadadores (descendente)
            sorted_teams = dict(sorted(teams_data.items(), key=lambda x: x[1]['total_swimmers'], reverse=True))

            return sorted_teams, "Previsualización generada exitosamente"

        except Exception as e:
            return None, f"Error generando previsualización de equipos: {e}"

    def generate_medals_report(self):
        """Generar reporte de medallas por categoría según número de inscritos"""
        swimmers = self.get_swimmers_list()
        if not swimmers:
            return None, "No hay nadadores inscritos"

        try:
            # Obtener eventos disponibles del evento configurado
            available_events = self.get_available_events()

            # Agrupar por categoría y evento
            category_events = {}

            for swimmer in swimmers:
                category = swimmer['category']
                gender = swimmer['gender']

                # Crear clave única por categoría y género
                category_key = f"{category} - {'Masculino' if gender == 'M' else 'Femenino'}"

                if category_key not in category_events:
                    category_events[category_key] = {}

                # Contar participantes por evento en esta categoría
                events_data = self._get_swimmer_events_dict(swimmer)
                for event, time in events_data.items():
                    if time and time.strip() and event in available_events:
                        if event not in category_events[category_key]:
                            category_events[category_key][event] = {
                                'participants': [],
                                'count': 0
                            }

                        category_events[category_key][event]['participants'].append({
                            'name': swimmer['name'],
                            'team': swimmer['team'],
                            'time': time
                        })
                        category_events[category_key][event]['count'] += 1

            # Calcular medallas por evento/categoría
            medals_data = {}

            for category_key, events in category_events.items():
                medals_data[category_key] = {}

                for event, event_data in events.items():
                    participants_count = event_data['count']

                    # Lógica correcta de medallas para campeonato deportivo
                    medals = {'Oro': 0, 'Plata': 0, 'Bronce': 0}

                    if participants_count >= 3:
                        # 3 o más participantes: Oro, Plata y Bronce
                        medals = {'Oro': 1, 'Plata': 1, 'Bronce': 1}
                    elif participants_count == 2:
                        # 2 participantes: Solo Oro y Plata
                        medals = {'Oro': 1, 'Plata': 1, 'Bronce': 0}
                    elif participants_count == 1:
                        # 1 participante: Solo Oro
                        medals = {'Oro': 1, 'Plata': 0, 'Bronce': 0}

                    medals_data[category_key][event] = {
                        'participants_count': participants_count,
                        'participants_list': event_data['participants'],
                        'medals': medals,
                        'total_medals': sum(medals.values()),
                        'medal_explanation': self._get_medal_explanation(participants_count)
                    }

            return medals_data, f"Reporte de medallas generado para {len(medals_data)} categorías"

        except Exception as e:
            return None, f"Error generando reporte de medallas: {e}"

    def preview_medals_report(self):
        """Generar previsualización del reporte de medallas"""
        swimmers = self.get_swimmers_list()
        if not swimmers:
            return None, "No hay nadadores inscritos"

        try:
            # Obtener eventos disponibles
            available_events = self.get_available_events()

            # Agrupar por categoría-género y contar participantes por evento
            category_events = {}

            for swimmer in swimmers:
                # Crear clave única para categoría-género
                category_key = f"{swimmer['category']} {swimmer['gender']}"

                if category_key not in category_events:
                    category_events[category_key] = {}

                # Contar participantes por evento en esta categoría
                events_data = self._get_swimmer_events_dict(swimmer)
                for event, time in events_data.items():
                    if time and time.strip() and event in available_events:
                        if event not in category_events[category_key]:
                            category_events[category_key][event] = {
                                'participants': [],
                                'count': 0
                            }

                        category_events[category_key][event]['participants'].append({
                            'name': swimmer['name'],
                            'team': swimmer['team'],
                            'time': time
                        })
                        category_events[category_key][event]['count'] += 1

            # Calcular medallas por categoría-evento
            medals_data = {}
            for category, events in category_events.items():
                medals_data[category] = {}
                for event, event_data in events.items():
                    participants = event_data['count']

                    # Lógica de medallas según número de participantes
                    medals = {'Oro': 0, 'Plata': 0, 'Bronce': 0}

                    if participants >= 3:
                        medals['Oro'] = 1
                        medals['Plata'] = 1
                        medals['Bronce'] = 1
                    elif participants == 2:
                        medals['Oro'] = 1
                        medals['Plata'] = 1
                    elif participants == 1:
                        medals['Oro'] = 1

                    medals_data[category][event] = {
                        'participants_count': participants,
                        'participants_list': event_data['participants'],
                        'medals': medals,
                        'total_medals': sum(medals.values()),
                        'medal_explanation': self._get_medal_explanation(participants)
                    }

            return medals_data, f"Previsualización de medallas generada para {len(medals_data)} categorías"

        except Exception as e:
            return None, f"Error generando previsualización de medallas: {e}"

    def generate_payments_report(self):
        """Generar reporte de pagos de clubes"""
        swimmers = self.get_swimmers_list()
        if not swimmers:
            return None, "No hay nadadores inscritos"

        try:
            # Obtener valores de tarifas desde el event manager
            swimmer_fee = 0
            team_fee = 0

            if self.event_manager and hasattr(self.event_manager, 'get_event_info'):
                event_info = self.event_manager.get_event_info()
                if event_info:
                    swimmer_fee = event_info.get('swimmer_fee', 0) or 0
                    team_fee = event_info.get('team_fee', 0) or 0

            # Si no hay tarifas configuradas, usar valores por defecto
            if swimmer_fee == 0:
                swimmer_fee = 25000
            if team_fee == 0:
                team_fee = 50000

            # Agrupar por equipo para calcular pagos
            teams_payments = {}

            for swimmer in swimmers:
                team_name = swimmer['team']

                if team_name not in teams_payments:
                    teams_payments[team_name] = {
                        'swimmers': [],
                        'swimmer_count': 0,
                        'total_events': 0,
                        'swimmer_fee_total': 0,
                        'team_fee': team_fee,
                        'total_payment': 0
                    }

                # Agregar nadador al equipo
                swimmer_events = self._get_swimmer_events_list(swimmer)
                teams_payments[team_name]['swimmers'].append({
                    'name': swimmer['name'],
                    'category': swimmer['category'],
                    'gender': 'Masculino' if swimmer['gender'] == 'M' else 'Femenino',
                    'events_count': len(swimmer_events)
                })

                teams_payments[team_name]['swimmer_count'] += 1
                teams_payments[team_name]['total_events'] += len(swimmer_events)

            # Calcular totales de pago
            for team_name, team_data in teams_payments.items():
                # Pago por nadadores
                team_data['swimmer_fee_total'] = team_data['swimmer_count'] * swimmer_fee

                # Pago total (nadadores + equipo)
                team_data['total_payment'] = team_data['swimmer_fee_total'] + team_data['team_fee']

            # Ordenar por pago total (descendente)
            sorted_payments = dict(sorted(teams_payments.items(),
                                        key=lambda x: x[1]['total_payment'],
                                        reverse=True))

            return sorted_payments, swimmer_fee, team_fee, f"Reporte de pagos generado para {len(sorted_payments)} equipos"

        except Exception as e:
            return None, 0, 0, f"Error generando reporte de pagos: {e}"

    def export_medals_report_to_excel(self, medals_data):
        """Exportar reporte de medallas a Excel"""
        if not medals_data:
            return None, "No hay datos de medallas para exportar"

        try:
            import pandas as pd
            from io import BytesIO

            buffer = BytesIO()

            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Hoja de resumen de medallas
                summary_data = []
                detail_data = []

                for category, events in medals_data.items():
                    category_medals = {'Oro': 0, 'Plata': 0, 'Bronce': 0}
                    category_events = 0

                    for event, event_data in events.items():
                        medals = event_data['medals']
                        participants = event_data['participants']

                        # Sumar medallas de la categoría
                        for medal_type, count in medals.items():
                            category_medals[medal_type] += count

                        category_events += 1

                        # Datos detallados por evento
                        detail_data.append({
                            'Categoría': category,
                            'Evento': event,
                            'Participantes': participants,
                            'Oro': medals['Oro'],
                            'Plata': medals['Plata'],
                            'Bronce': medals['Bronce'],
                            'Total Medallas': sum(medals.values())
                        })

                    # Resumen por categoría
                    summary_data.append({
                        'Categoría': category,
                        'Eventos': category_events,
                        'Oro': category_medals['Oro'],
                        'Plata': category_medals['Plata'],
                        'Bronce': category_medals['Bronce'],
                        'Total Medallas': sum(category_medals.values())
                    })

                # Crear DataFrames y exportar
                summary_df = pd.DataFrame(summary_data)
                detail_df = pd.DataFrame(detail_data)

                summary_df.to_excel(writer, sheet_name='Resumen de Medallas', index=False)
                detail_df.to_excel(writer, sheet_name='Detalle por Evento', index=False)

            buffer.seek(0)
            return buffer.getvalue(), "reporte_medallas.xlsx"

        except Exception as e:
            return None, f"Error exportando reporte de medallas: {e}"

    def export_payments_report_to_excel(self, payments_data, swimmer_fee, team_fee):
        """Exportar reporte de pagos a Excel"""
        if not payments_data:
            return None, "No hay datos de pagos para exportar"

        try:
            import pandas as pd
            from io import BytesIO

            buffer = BytesIO()

            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Hoja de resumen de pagos
                summary_data = []
                detail_data = []

                total_swimmers = 0
                total_teams = len(payments_data)
                total_revenue = 0

                for team_name, team_data in payments_data.items():
                    total_swimmers += team_data['swimmer_count']
                    total_revenue += team_data['total_payment']

                    # Resumen por equipo
                    summary_data.append({
                        'Equipo': team_name,
                        'Nadadores': team_data['swimmer_count'],
                        'Pago por Nadadores': f"${team_data['swimmer_fee_total']:,.0f}",
                        'Pago por Equipo': f"${team_data['team_fee']:,.0f}",
                        'Total a Pagar': f"${team_data['total_payment']:,.0f}",
                        'Total Inscripciones': team_data['total_events']
                    })

                    # Detalle por nadador
                    for swimmer in team_data['swimmers']:
                        detail_data.append({
                            'Equipo': team_name,
                            'Nadador': swimmer['name'],
                            'Categoría': swimmer['category'],
                            'Sexo': swimmer['gender'],
                            'Eventos': swimmer['events_count'],
                            'Pago Individual': f"${swimmer_fee:,.0f}"
                        })

                # Agregar totales
                summary_data.append({
                    'Equipo': 'TOTAL GENERAL',
                    'Nadadores': total_swimmers,
                    'Pago por Nadadores': f"${total_swimmers * swimmer_fee:,.0f}",
                    'Pago por Equipo': f"${total_teams * team_fee:,.0f}",
                    'Total a Pagar': f"${total_revenue:,.0f}",
                    'Total Inscripciones': sum(team_data['total_events'] for team_data in payments_data.values())
                })

                # Crear DataFrames y exportar
                summary_df = pd.DataFrame(summary_data)
                detail_df = pd.DataFrame(detail_data)

                summary_df.to_excel(writer, sheet_name='Resumen de Pagos', index=False)
                detail_df.to_excel(writer, sheet_name='Detalle de Nadadores', index=False)

            buffer.seek(0)
            return buffer.getvalue(), "reporte_pagos.xlsx"

        except Exception as e:
            return None, f"Error exportando reporte de pagos: {e}"

    def generate_team_pdf(self, team_name, team_info):
        """Generar PDF individual para un equipo específico con estadísticas e inscripciones detalladas"""
        if not team_info:
            return None, "No hay datos del equipo"

        try:
            # Importar ReportLab si está disponible
            if not REPORTLAB_AVAILABLE:
                return None, "ReportLab no está disponible. Por favor instala reportlab: pip install reportlab"

            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from io import BytesIO
            from datetime import datetime

            # Crear buffer para el PDF
            buffer = BytesIO()

            # Crear documento PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)

            # Estilos personalizados
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=18,
                spaceAfter=0.3*inch,
                textColor=colors.HexColor('#1f4e79'),
                alignment=1  # Center
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2e75b6'),
                spaceAfter=0.2*inch
            )

            subheading_style = ParagraphStyle(
                'CustomSubheading',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.HexColor('#2e75b6'),
                spaceAfter=0.1*inch
            )

            # Contenido del PDF
            content = []

            # Título principal
            title = Paragraph(f"REPORTE DE INSCRIPCIÓN<br/>EQUIPO: {team_name.upper()}", title_style)
            content.append(title)
            content.append(Spacer(1, 0.3*inch))

            # Estadísticas del equipo
            stats_title = Paragraph("ESTADÍSTICAS DEL EQUIPO", heading_style)
            content.append(stats_title)

            stats_data = [
                ["Concepto", "Cantidad"],
                ["Total Nadadores", str(team_info['total_swimmers'])],
                ["Nadadores Masculinos", str(team_info['genders']['M'])],
                ["Nadadores Femeninos", str(team_info['genders']['F'])],
                ["Total Inscripciones", str(team_info['total_events'])]
            ]

            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e75b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f2f8ff')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d4d4d4'))
            ]))

            content.append(stats_table)
            content.append(Spacer(1, 0.3*inch))

            # Distribución por categorías
            if team_info['categories']:
                categories_title = Paragraph("DISTRIBUCIÓN POR CATEGORÍAS", heading_style)
                content.append(categories_title)

                categories_data = [["Categoría", "Cantidad de Nadadores"]]
                for category, count in team_info['categories'].items():
                    categories_data.append([category, str(count)])

                categories_table = Table(categories_data, colWidths=[3*inch, 2*inch])
                categories_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e75b6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d4d4d4')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
                ]))

                content.append(categories_table)
                content.append(Spacer(1, 0.3*inch))

            # Inscripciones detalladas por nadador
            swimmers_title = Paragraph("INSCRIPCIONES DETALLADAS POR NADADOR", heading_style)
            content.append(swimmers_title)

            for i, swimmer in enumerate(team_info['swimmers']):
                # Datos del nadador
                swimmer_name = Paragraph(f"<b>{i+1}. {swimmer['name']}</b>", subheading_style)
                content.append(swimmer_name)

                # Información básica del nadador
                basic_info = [
                    ["Información", "Detalle"],
                    ["Edad", f"{swimmer['age']} años"],
                    ["Categoría", swimmer['category']],
                    ["Género", "Masculino" if swimmer['gender'] == 'M' else "Femenino"]
                ]

                basic_table = Table(basic_info, colWidths=[1.5*inch, 2*inch])
                basic_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d4d4d4')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
                ]))

                content.append(basic_table)
                content.append(Spacer(1, 0.1*inch))

                # Inscripciones del nadador con tiempos
                events_data = [["Evento", "Tiempo Inscripción"]]
                events_dict = self._get_swimmer_events_dict(swimmer)

                for event, time in events_dict.items():
                    if time and str(time).strip():
                        events_data.append([event, str(time)])

                if len(events_data) > 1:  # Si hay eventos inscritos
                    events_table = Table(events_data, colWidths=[3*inch, 1.5*inch])
                    events_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#70AD47')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d4d4d4')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f8f0')])
                    ]))

                    content.append(events_table)
                else:
                    no_events = Paragraph("Sin inscripciones en eventos", styles['Normal'])
                    content.append(no_events)

                content.append(Spacer(1, 0.2*inch))

                # Separar nadadores si hay muchos (nueva página cada 4 nadadores)
                if (i + 1) % 4 == 0 and i < len(team_info['swimmers']) - 1:
                    content.append(PageBreak())

            # Pie de página con fecha y hora
            content.append(Spacer(1, 0.5*inch))
            footer = Paragraph(
                f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</i>",
                styles['Normal']
            )
            content.append(footer)

            # Construir PDF
            doc.build(content)
            buffer.seek(0)

            return buffer.getvalue(), f"reporte_equipo_{team_name.replace(' ', '_')}.pdf"

        except Exception as e:
            return None, f"Error generando PDF del equipo: {e}"

    def generate_club_payment_invoice(self, team_name, team_data, swimmer_fee, team_fee):
        """Generar PDF de cuenta de cobro para un club específico"""
        if not team_data:
            return None, "No hay datos del equipo"

        try:
            # Importar ReportLab si está disponible
            if not REPORTLAB_AVAILABLE:
                return None, "ReportLab no está disponible. Por favor instala reportlab: pip install reportlab"

            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from io import BytesIO
            from datetime import datetime

            # Crear buffer para el PDF
            buffer = BytesIO()

            # Crear documento PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)

            # Estilos personalizados
            styles = getSampleStyleSheet()

            # Estilo para título principal
            title_style = ParagraphStyle(
                'InvoiceTitle',
                parent=styles['Title'],
                fontSize=20,
                spaceAfter=0.3*inch,
                textColor=colors.HexColor('#1f4e79'),
                alignment=1,  # Center
                fontName='Helvetica-Bold'
            )

            # Estilo para encabezados
            heading_style = ParagraphStyle(
                'InvoiceHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2e75b6'),
                spaceAfter=0.2*inch,
                fontName='Helvetica-Bold'
            )

            # Estilo para información legal
            legal_style = ParagraphStyle(
                'LegalInfo',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#666666'),
                alignment=1  # Center
            )

            # Contenido del PDF
            content = []

            # Título principal
            title = Paragraph("CUENTA DE COBRO", title_style)
            content.append(title)
            content.append(Spacer(1, 0.2*inch))

            # Información de la factura
            invoice_date = datetime.now().strftime('%d/%m/%Y')
            invoice_info = [
                ["Fecha:", invoice_date],
                ["Club/Equipo:", team_name],
                ["Concepto:", "Inscripción Competencia de Natación"],
                ["Estado:", "PENDIENTE DE PAGO"]
            ]

            invoice_table = Table(invoice_info, colWidths=[2*inch, 3*inch])
            invoice_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 3), (1, 3), colors.HexColor('#ffe6e6'))  # Resaltar estado pendiente
            ]))

            content.append(invoice_table)
            content.append(Spacer(1, 0.3*inch))

            # Detalle de nadadores
            swimmers_title = Paragraph("DETALLE DE NADADORES INSCRITOS", heading_style)
            content.append(swimmers_title)

            # Crear tabla con los nadadores
            swimmers_data = [["#", "Nombre del Nadador", "Categoría", "Eventos", "Valor"]]

            total_swimmer_cost = 0
            for i, swimmer in enumerate(team_data['swimmers'], 1):
                swimmers_data.append([
                    str(i),
                    swimmer['name'],
                    swimmer['category'],
                    str(swimmer['events_count']),
                    f"${swimmer_fee:,.0f}"
                ])
                total_swimmer_cost += swimmer_fee

            swimmers_table = Table(swimmers_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 0.8*inch, 1*inch])
            swimmers_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e75b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Nombres alineados a la izquierda
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d4d4d4')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))

            content.append(swimmers_table)
            content.append(Spacer(1, 0.2*inch))

            # Resumen de costos
            cost_title = Paragraph("RESUMEN DE COSTOS", heading_style)
            content.append(cost_title)

            cost_summary = [
                ["Concepto", "Cantidad", "Valor Unitario", "Subtotal"],
                [f"Inscripción Nadadores ({team_data['swimmer_count']})", str(team_data['swimmer_count']), f"${swimmer_fee:,.0f}", f"${total_swimmer_cost:,.0f}"],
                ["Inscripción de Equipo", "1", f"${team_fee:,.0f}", f"${team_fee:,.0f}"],
                ["", "", "", ""],
                ["TOTAL A PAGAR", "", "", f"${team_data['total_payment']:,.0f}"]
            ]

            cost_table = Table(cost_summary, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.2*inch])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e75b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#4472C4')),
                ('TEXTCOLOR', (0, 4), (-1, 4), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, 3), 'LEFT'),  # Conceptos alineados a la izquierda
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, 3), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTSIZE', (0, 4), (-1, 4), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, 3), 1, colors.HexColor('#d4d4d4')),
                ('GRID', (0, 4), (-1, 4), 2, colors.HexColor('#2e75b6')),
                ('ROWBACKGROUNDS', (0, 1), (-1, 3), [colors.white, colors.HexColor('#f0f8ff')])
            ]))

            content.append(cost_table)
            content.append(Spacer(1, 0.4*inch))

            # Información de pago
            payment_title = Paragraph("INFORMACIÓN DE PAGO", heading_style)
            content.append(payment_title)

            payment_info = Paragraph(
                "<b>Forma de Pago:</b> Transferencia bancaria o consignación<br/>"
                "<b>Plazo de Pago:</b> 5 días hábiles a partir de la fecha de esta cuenta<br/>"
                "<b>Referencia:</b> Incluir nombre del equipo en la transferencia<br/><br/>"
                "<i>* Esta cuenta de cobro es válida únicamente para el equipo especificado</i><br/>"
                "<i>* El pago debe realizarse antes del inicio de la competencia</i>",
                styles['Normal']
            )
            content.append(payment_info)
            content.append(Spacer(1, 0.3*inch))

            # Pie de página
            footer_info = Paragraph(
                f"<i>Cuenta de cobro generada el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}<br/>"
                "Sistema de Gestión de Competencias - TEN</i>",
                legal_style
            )
            content.append(footer_info)

            # Construir PDF
            doc.build(content)
            buffer.seek(0)

            return buffer.getvalue(), f"cuenta_cobro_{team_name.replace(' ', '_')}.pdf"

        except Exception as e:
            return None, f"Error generando cuenta de cobro: {e}"

    def preview_payments_report(self):
        """Generar previsualización del reporte de pagos"""
        swimmers = self.get_swimmers_list()
        if not swimmers:
            return None, 0, 0, "No hay nadadores inscritos"

        try:
            # Obtener valores de tarifas desde el event manager
            swimmer_fee = 0
            team_fee = 0

            if self.event_manager and hasattr(self.event_manager, 'get_event_info'):
                event_info = self.event_manager.get_event_info()
                if event_info:
                    swimmer_fee = event_info.get('swimmer_fee', 0) or 0
                    team_fee = event_info.get('team_fee', 0) or 0

            # Si no hay tarifas configuradas, usar valores por defecto
            if swimmer_fee == 0:
                swimmer_fee = 25000
            if team_fee == 0:
                team_fee = 50000

            # Agrupar pagos por equipo
            teams_payments = {}

            for swimmer in swimmers:
                team_name = swimmer['team']
                if team_name not in teams_payments:
                    teams_payments[team_name] = {
                        'swimmers': [],
                        'swimmer_count': 0,
                        'total_events': 0,
                        'swimmer_fee_total': 0,
                        'team_fee_total': team_fee,
                        'total_payment': 0
                    }

                # Agregar nadador al equipo
                swimmer_events = self._get_swimmer_events_list(swimmer)
                teams_payments[team_name]['swimmers'].append({
                    'name': swimmer['name'],
                    'category': swimmer['category'],
                    'gender': 'Masculino' if swimmer['gender'] == 'M' else 'Femenino',
                    'events_count': len(swimmer_events)
                })

                teams_payments[team_name]['swimmer_count'] += 1
                teams_payments[team_name]['total_events'] += len(swimmer_events)

            # Calcular totales de pago
            for team_name, team_data in teams_payments.items():
                # Pago por nadadores
                team_data['swimmer_fee_total'] = team_data['swimmer_count'] * swimmer_fee

                # Pago total del equipo
                team_data['total_payment'] = team_data['swimmer_fee_total'] + team_data['team_fee_total']

            # Ordenar por total de pago (descendente)
            sorted_payments = dict(sorted(teams_payments.items(),
                                        key=lambda x: x[1]['total_payment'],
                                        reverse=True))

            return sorted_payments, swimmer_fee, team_fee, f"Previsualización de pagos generada para {len(sorted_payments)} equipos"

        except Exception as e:
            return None, 0, 0, f"Error generando previsualización de pagos: {e}"

    # ===== MÉTODOS PARA BÚSQUEDA EN BASE DE DATOS =====
    
    def load_database(self):
        """Cargar la base de datos desde FPROYECCION 2025T, M. PROYECCION 2025 y ATLETAS combinadas"""
        if not os.path.exists(self.archivo_base_datos):
            return None, f"No se encontró el archivo {self.archivo_base_datos}"

        try:
            xl_file = pd.ExcelFile(self.archivo_base_datos)

            # Primero cargar la hoja ATLETAS para obtener fechas de nacimiento
            atletas_df = None
            if 'ATLETAS' in xl_file.sheet_names:
                try:
                    atletas_df = pd.read_excel(self.archivo_base_datos, sheet_name='ATLETAS', header=0)
                    print(f"Hoja ATLETAS cargada con {len(atletas_df)} registros")
                except Exception as e:
                    print(f"Error al cargar hoja ATLETAS: {e}")

            dfs_to_combine = []
            sheets_loaded = []

            # Hojas objetivo (femenino y masculino)
            target_sheets = ['FPROYECCION 2025T', 'M. PROYECCION 2025']

            for sheet_name in target_sheets:
                try:
                    if sheet_name in xl_file.sheet_names:
                        df_sheet = pd.read_excel(self.archivo_base_datos, sheet_name=sheet_name, header=0)

                        # Filtrar columnas relevantes (evitar duplicaciones)
                        relevant_columns = ['ATLETA', 'EQUIPO', 'CATEGORIA', 'SEXO', 'EDAD', 'PRUEBA', 'TIEMPO', 'F. COMPETENCIA']
                        available_columns = [col for col in relevant_columns if col in df_sheet.columns]

                        if available_columns and len(df_sheet) > 0:
                            df_filtered = df_sheet[available_columns].copy()

                            # Si tenemos la hoja ATLETAS, hacer merge para obtener fechas de nacimiento
                            if atletas_df is not None and 'ATLETA' in df_filtered.columns:
                                # Buscar columnas de fecha de nacimiento en ATLETAS
                                birth_date_columns = []
                                for col in atletas_df.columns:
                                    if any(keyword in col.upper() for keyword in ['NACIMIENTO', 'BIRTH', 'FECHA']):
                                        birth_date_columns.append(col)

                                if birth_date_columns and 'ATLETA' in atletas_df.columns:
                                    # Preparar DataFrame de atletas para merge
                                    try:
                                        atletas_merge = atletas_df[['ATLETA'] + birth_date_columns].copy()
                                        # Limpiar nombres para mejor matching
                                        atletas_merge['ATLETA_CLEAN'] = atletas_merge['ATLETA'].astype(str).str.strip().str.upper()
                                        df_filtered['ATLETA_CLEAN'] = df_filtered['ATLETA'].astype(str).str.strip().str.upper()

                                        # Hacer merge
                                        df_merged = df_filtered.merge(
                                            atletas_merge,
                                            left_on='ATLETA_CLEAN',
                                            right_on='ATLETA_CLEAN',
                                            how='left',
                                            suffixes=('', '_ATLETAS')
                                        )

                                        # Limpiar columnas auxiliares
                                        df_merged = df_merged.drop(['ATLETA_CLEAN', 'ATLETA_ATLETAS'], axis=1, errors='ignore')

                                        # Verificar si el merge fue exitoso
                                        merged_count = df_merged[birth_date_columns[0]].notna().sum()
                                        total_count = len(df_merged)

                                        print(f"Merge con ATLETAS - {sheet_name}: {merged_count}/{total_count} registros con fecha de nacimiento")

                                        df_filtered = df_merged
                                    except Exception as e:
                                        print(f"Error en merge con ATLETAS para {sheet_name}: {e}")
                                        # Continuar sin las fechas de nacimiento si falla el merge

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
        try:
            df, message = self.load_database()
            if df is None:
                return [], message

            # Buscar en la columna ATLETA
            if 'ATLETA' not in df.columns:
                return [], "No se encontró columna ATLETA en la base de datos"

            # Buscar coincidencias por nombre
            search_term = search_term.lower().strip()
            if not search_term:
                return [], "Ingrese un término de búsqueda válido"

            name_mask = df['ATLETA'].astype(str).str.lower().str.contains(search_term, na=False, regex=False)
            matching_rows = df[name_mask]

            if matching_rows.empty:
                return [], f"No se encontraron atletas con el nombre '{search_term}'"

            # Obtener configuración del evento para edad y categorías
            event_categories = self.get_event_categories()
            event_info = None
            age_criteria = 'event_date'
            event_start_date = None

            if self.event_manager:
                event_info = self.event_manager.get_event_info()
                if event_info:
                    age_criteria = event_info.get('age_criteria', 'event_date')
                    if event_info.get('start_date'):
                        try:
                            from datetime import datetime
                            event_start_date = datetime.fromisoformat(event_info['start_date']).date()
                        except:
                            pass

            # Filtrar por categorías usando fecha de nacimiento si está disponible
            if event_categories and self.event_manager:
                # Extraer nombres de las categorías del evento
                event_category_names = [cat['name'] for cat in event_categories]

                # Buscar columna de fecha de nacimiento (incluyendo las que vienen de ATLETAS)
                birth_date_column = None
                # Buscar por nombres exactos y patrones
                for col in matching_rows.columns:
                    col_upper = col.upper()
                    if any(keyword in col_upper for keyword in ['NACIMIENTO', 'BIRTH', 'FECHA_NAC', 'F_NACIMIENTO']):
                        birth_date_column = col
                        print(f"Encontrada columna de fecha de nacimiento: {col}")
                        break

                if birth_date_column:
                    # Filtrar por edad calculada desde fecha de nacimiento
                    valid_rows = []
                    debug_info = []

                    for idx, row in matching_rows.iterrows():
                        birth_date = row.get(birth_date_column)
                        athlete_name = row.get('ATLETA', 'N/A')

                        if birth_date and not pd.isna(birth_date):
                            calculated_age = self.calculate_age_by_criteria(birth_date, event_start_date, age_criteria)
                            if calculated_age:
                                debug_info.append(f"{athlete_name}: {birth_date} → edad {calculated_age}")
                                # Buscar categoría correspondiente
                                for category in event_categories:
                                    category_name = category.get('name', '')
                                    age_range = category.get('age_range', '')
                                    if age_range:
                                        min_age, max_age = self.event_manager.parse_age_range(age_range)
                                        if min_age is not None and max_age is not None:
                                            if min_age <= calculated_age <= max_age:
                                                valid_rows.append(idx)
                                                debug_info.append(f"  ✓ Válido para categoría {category_name} ({age_range})")
                                                break
                                else:
                                    debug_info.append(f"  ✗ No válido para ninguna categoría del evento")
                            else:
                                debug_info.append(f"{athlete_name}: Error calculando edad desde {birth_date}")
                        else:
                            debug_info.append(f"{athlete_name}: Sin fecha de nacimiento válida")

                    print(f"Filtrado por fecha de nacimiento:")
                    for info in debug_info[:10]:  # Mostrar solo los primeros 10 para no saturar
                        print(f"  {info}")

                    if valid_rows:
                        matching_rows = matching_rows.loc[valid_rows]
                        print(f"Resultado final: {len(valid_rows)} nadadores válidos de {len(debug_info)} evaluados")
                    else:
                        return [], f"No se encontraron nadadores de '{search_term}' con edades válidas para las categorías del evento. Criterio: {age_criteria}"

                elif 'CATEGORIA' in matching_rows.columns:
                    # Fallback: filtrar por categorías directamente
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

                # Calcular edad actualizada si hay fecha de nacimiento
                calculated_age = None
                birth_date_column = None
                # Buscar fecha de nacimiento en las columnas disponibles
                for col in first_record.index:
                    col_upper = str(col).upper()
                    if any(keyword in col_upper for keyword in ['NACIMIENTO', 'BIRTH', 'FECHA_NAC', 'F_NACIMIENTO']):
                        if not pd.isna(first_record[col]):
                            birth_date_column = col
                            print(f"Usando fecha de nacimiento de columna: {col}")
                            break

                if birth_date_column and event_start_date and age_criteria:
                    calculated_age = self.calculate_age_by_criteria(first_record[birth_date_column], event_start_date, age_criteria)

                match_data = {
                    'index': 0,  # No importante ya que agrupamos
                    'name': athlete_name,
                    'full_data': first_record,  # Información básica del primer registro
                    'all_records': athlete_records,  # Todos los registros del atleta
                }

                # Agregar edad calculada si está disponible
                if calculated_age:
                    match_data['calculated_age'] = calculated_age
                    match_data['age_criteria'] = age_criteria

                matches.append(match_data)

            total_message = f"Se encontraron {len(matches)} atletas únicos"
            if event_categories and self.event_manager:
                event_category_names = [cat['name'] for cat in event_categories]
                total_message += f" en las categorías: {', '.join(event_category_names)}"

            return matches, total_message

        except Exception as e:
            return [], f"Error procesando búsqueda: {str(e)}"
    
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
            'birth_date': row.get('FECHA DE NA', ''),
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
            all_columns = ['NOMBRE Y AP', 'EQUIPO', 'EDAD', 'CAT.', 'SEXO', 'FECHA DE NA'] + available_events
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
import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

class EventManager:
    def __init__(self):
        self.config_file = 'event_config.json'
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

    def save_event_config(self, event_name, categories, event_order, category_events, min_age, max_age):
        """Guardar la configuración del evento"""
        config = {
            'event_name': event_name,
            'categories': categories,
            'event_order': event_order,
            'category_events': category_events,
            'min_age': min_age,
            'max_age': max_age,
            'created_date': datetime.now().isoformat(),
            'modified_date': datetime.now().isoformat()
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True, f"Evento '{event_name}' guardado exitosamente"
        except Exception as e:
            return False, f"Error al guardar configuración: {e}"

    def load_event_config(self):
        """Cargar la configuración del evento existente"""
        if not os.path.exists(self.config_file):
            return None

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            return None

    def get_available_events(self):
        """Obtener la lista de todas las pruebas disponibles"""
        return self.swimming_events

    def get_selected_events(self):
        """Obtener las pruebas seleccionadas para el evento actual"""
        config = self.load_event_config()
        if config:
            return config.get('event_order', [])
        return []

    def get_categories(self):
        """Obtener las categorías configuradas para el evento"""
        config = self.load_event_config()
        if config:
            return config.get('categories', [])
        return []

    def get_category_events(self):
        """Obtener las pruebas asignadas por categoría"""
        config = self.load_event_config()
        if config:
            return config.get('category_events', {})
        return {}

    def get_event_info(self):
        """Obtener información completa del evento"""
        config = self.load_event_config()
        if config:
            return {
                'name': config.get('event_name', ''),
                'categories': config.get('categories', []),
                'events': config.get('event_order', []),
                'category_events': config.get('category_events', {}),
                'min_age': config.get('min_age', 8),
                'max_age': config.get('max_age', 18),
                'created_date': config.get('created_date', ''),
                'modified_date': config.get('modified_date', '')
            }
        return None

    def validate_swimmer_age(self, age):
        """Validar si la edad del nadador está dentro del rango permitido"""
        config = self.load_event_config()
        if config:
            min_age = config.get('min_age', 8)
            max_age = config.get('max_age', 18)
            return min_age <= age <= max_age
        return True

    def validate_event_selection(self, event):
        """Validar si la prueba está seleccionada para el evento"""
        selected_events = self.get_selected_events()
        return event in selected_events if selected_events else True

    def update_event_config(self, event_name=None, categories=None, event_order=None, category_events=None, min_age=None, max_age=None):
        """Actualizar configuración existente"""
        config = self.load_event_config()
        if not config:
            return False, "No existe configuración de evento"

        if event_name is not None:
            config['event_name'] = event_name
        if categories is not None:
            config['categories'] = categories
        if event_order is not None:
            config['event_order'] = event_order
        if category_events is not None:
            config['category_events'] = category_events
        if min_age is not None:
            config['min_age'] = min_age
        if max_age is not None:
            config['max_age'] = max_age

        config['modified_date'] = datetime.now().isoformat()

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True, "Configuración actualizada exitosamente"
        except Exception as e:
            return False, f"Error al actualizar configuración: {e}"

    def delete_event_config(self):
        """Eliminar la configuración del evento"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
                return True, "Configuración de evento eliminada"
            return False, "No existe configuración de evento"
        except Exception as e:
            return False, f"Error al eliminar configuración: {e}"

    def is_event_configured(self):
        """Verificar si existe un evento configurado"""
        return os.path.exists(self.config_file)

    def get_event_summary(self):
        """Obtener resumen del evento para mostrar"""
        config = self.load_event_config()
        if config:
            event_count = len(config.get('event_order', []))
            categories_count = len(config.get('categories', []))
            age_range = f"{config.get('min_age', 8)}-{config.get('max_age', 18)} años"

            return {
                'name': config.get('event_name', 'Sin nombre'),
                'events_count': event_count,
                'categories_count': categories_count,
                'age_range': age_range,
                'events_list': config.get('event_order', []),
                'categories_list': config.get('categories', [])
            }
        return None

    def filter_database_events(self, database_events):
        """Filtrar pruebas de la base de datos según las seleccionadas en el evento"""
        selected_events = self.get_selected_events()
        if not selected_events:
            return database_events

        # Mapeo de pruebas del sistema a pruebas de base de datos
        event_mappings = {
            '50M CROLL': ['50m LIBRE', '50M CROLL', '50 LIBRE'],
            '100M CROLL': ['100m LIBRE', '100M CROLL', '100 LIBRE'],
            '200M CROLL': ['200m LIBRE', '200M CROLL', '200 LIBRE'],
            '400M CROLL': ['400m LIBRE', '400M CROLL', '400 LIBRE'],
            '50M ESPALDA': ['50m ESPALDA', '50M ESPALDA', '50 ESPALDA'],
            '100M ESPALDA': ['100m ESPALDA', '100M ESPALDA', '100 ESPALDA'],
            '200M ESPALDA': ['200m ESPALDA', '200M ESPALDA', '200 ESPALDA'],
            '50M PECHO': ['50m PECHO', '50M PECHO', '50 PECHO'],
            '100M PECHO': ['100m PECHO', '100M PECHO', '100 PECHO'],
            '200M PECHO': ['200m PECHO', '200M PECHO', '200 PECHO'],
            '50M MARIPOSA': ['50m MARIPOSA', '50M MARIPOSA', '50 MARIPOSA'],
            '100M MARIPOSA': ['100m MARIPOSA', '100M MARIPOSA', '100 MARIPOSA'],
            '200M MARIPOSA': ['200m MARIPOSA', '200M MARIPOSA', '200 MARIPOSA'],
            '200M COMBINADO INDIVIDUAL': ['200m COMBINADO', '200M COMBINADO', '200 COMBINADO'],
            '400M COMBINADO INDIVIDUAL': ['400m COMBINADO', '400M COMBINADO', '400 COMBINADO']
        }

        # Crear lista de pruebas de base de datos permitidas
        allowed_db_events = []
        for selected_event in selected_events:
            if selected_event in event_mappings:
                allowed_db_events.extend(event_mappings[selected_event])

        # Filtrar eventos de base de datos
        filtered_events = {}
        for event_name, event_data in database_events.items():
            # Buscar si alguna variación del evento está permitida
            for allowed_event in allowed_db_events:
                if (event_name.upper().replace(' ', '') == allowed_event.upper().replace(' ', '') or
                    allowed_event.upper() in event_name.upper()):
                    filtered_events[event_name] = event_data
                    break

        return filtered_events

    # ===== MÉTODOS PARA GESTIÓN DE CATEGORÍAS =====

    def load_categories_from_excel(self, uploaded_file):
        """Cargar categorías desde archivo Excel"""
        try:
            df = pd.read_excel(uploaded_file)

            # Buscar columnas relevantes (flexible)
            name_col = None
            age_col = None

            for col in df.columns:
                col_lower = str(col).lower()
                if 'nombre' in col_lower or 'categoria' in col_lower or 'category' in col_lower:
                    name_col = col
                elif 'edad' in col_lower or 'age' in col_lower or 'rango' in col_lower:
                    age_col = col

            if not name_col:
                return False, "No se encontró columna de nombre de categoría (debe contener 'nombre', 'categoria' o 'category')"

            categories = []
            for _, row in df.iterrows():
                if pd.notna(row[name_col]):
                    category_name = str(row[name_col]).strip()
                    age_range = ""

                    if age_col and pd.notna(row[age_col]):
                        age_range = str(row[age_col]).strip()

                    if category_name:
                        categories.append({
                            'name': category_name,
                            'age_range': age_range
                        })

            if not categories:
                return False, "No se encontraron categorías válidas en el archivo"

            return True, categories

        except Exception as e:
            return False, f"Error al leer archivo: {str(e)}"

    def validate_category_name(self, name, existing_categories, exclude_index=None):
        """Validar que el nombre de categoría no esté duplicado"""
        name_lower = name.lower().strip()
        for i, cat in enumerate(existing_categories):
            if i != exclude_index and cat['name'].lower().strip() == name_lower:
                return False, f"La categoría '{name}' ya existe"
        return True, "Nombre válido"

    def get_category_by_name(self, category_name):
        """Obtener categoría por nombre"""
        categories = self.get_categories()
        for category in categories:
            if category['name'].lower() == category_name.lower():
                return category
        return None

    def get_events_for_category(self, category_name):
        """Obtener pruebas asignadas a una categoría específica"""
        category_events = self.get_category_events()
        return category_events.get(category_name, [])

    def assign_events_to_category(self, category_name, events):
        """Asignar pruebas a una categoría"""
        config = self.load_event_config()
        if not config:
            return False, "No existe configuración de evento"

        if 'category_events' not in config:
            config['category_events'] = {}

        config['category_events'][category_name] = events
        config['modified_date'] = datetime.now().isoformat()

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True, f"Pruebas asignadas a {category_name}"
        except Exception as e:
            return False, f"Error al asignar pruebas: {e}"

    def validate_event_configuration(self):
        """Validar que la configuración del evento sea completa"""
        config = self.load_event_config()
        if not config:
            return False, "No existe configuración de evento"

        errors = []

        # Validar datos básicos
        if not config.get('event_name', '').strip():
            errors.append("Falta el nombre del evento")

        # Validar categorías
        categories = config.get('categories', [])
        if not categories:
            errors.append("No hay categorías definidas")
        else:
            for i, cat in enumerate(categories):
                if not cat.get('name', '').strip():
                    errors.append(f"Categoría {i+1} no tiene nombre")

        # Validar pruebas del evento
        event_order = config.get('event_order', [])
        if not event_order:
            errors.append("No hay pruebas seleccionadas para el evento")

        # Validar asignación de pruebas por categoría
        category_events = config.get('category_events', {})
        for category in categories:
            cat_name = category['name']
            if cat_name not in category_events or not category_events[cat_name]:
                errors.append(f"La categoría '{cat_name}' no tiene pruebas asignadas")

        # Validar edades
        min_age = config.get('min_age', 0)
        max_age = config.get('max_age', 0)
        if min_age >= max_age:
            errors.append("El rango de edades no es válido")

        if errors:
            return False, "; ".join(errors)

        return True, "Configuración válida"

    def get_available_events_for_swimmer(self, category_name):
        """Obtener las pruebas disponibles para un nadador según su categoría"""
        if not category_name:
            return self.get_selected_events()

        return self.get_events_for_category(category_name)
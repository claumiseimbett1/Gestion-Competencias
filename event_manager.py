import json
import os
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

    def save_event_config(self, event_name, selected_events, min_age, max_age):
        """Guardar la configuración del evento"""
        config = {
            'event_name': event_name,
            'selected_events': selected_events,
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
            return config.get('selected_events', [])
        return []

    def get_event_info(self):
        """Obtener información completa del evento"""
        config = self.load_event_config()
        if config:
            return {
                'name': config.get('event_name', ''),
                'events': config.get('selected_events', []),
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

    def update_event_config(self, event_name=None, selected_events=None, min_age=None, max_age=None):
        """Actualizar configuración existente"""
        config = self.load_event_config()
        if not config:
            return False, "No existe configuración de evento"

        if event_name is not None:
            config['event_name'] = event_name
        if selected_events is not None:
            config['selected_events'] = selected_events
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
            event_count = len(config.get('selected_events', []))
            age_range = f"{config.get('min_age', 8)}-{config.get('max_age', 18)} años"

            return {
                'name': config.get('event_name', 'Sin nombre'),
                'events_count': event_count,
                'age_range': age_range,
                'events_list': config.get('selected_events', [])
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
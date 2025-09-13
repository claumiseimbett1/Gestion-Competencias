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

    def save_event_config(self, event_name, categories, event_order, category_events, min_age, max_age,
                         swimmer_fee=None, team_fee=None, welcome_message=None, event_logo=None):
        """Guardar la configuración del evento"""
        config = {
            'event_name': event_name,
            'categories': categories,
            'event_order': event_order,
            'category_events': category_events,
            'min_age': min_age,
            'max_age': max_age,
            'swimmer_fee': swimmer_fee or 0,
            'team_fee': team_fee or 0,
            'welcome_message': welcome_message or '',
            'event_logo': event_logo,
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

    def update_event_config(self, event_name=None, categories=None, event_order=None, category_events=None,
                          min_age=None, max_age=None, swimmer_fee=None, team_fee=None,
                          welcome_message=None, event_logo=None):
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
        if swimmer_fee is not None:
            config['swimmer_fee'] = swimmer_fee
        if team_fee is not None:
            config['team_fee'] = team_fee
        if welcome_message is not None:
            config['welcome_message'] = welcome_message
        if event_logo is not None:
            config['event_logo'] = event_logo

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

    def parse_age_range(self, age_range_str):
        """Parsear un string de rango de edad y retornar min_age, max_age"""
        try:
            if not age_range_str or not age_range_str.strip():
                return None, None

            age_range = age_range_str.strip()

            # Patrón para rango: "12-13", "12 a 13", "12 - 13"
            import re
            range_pattern = r'(\d+)[\s]*[-aA]\s*(\d+)'
            match = re.search(range_pattern, age_range)

            if match:
                min_age = int(match.group(1))
                max_age = int(match.group(2))
                return min_age, max_age

            # Patrón para edad específica: "12", "12 años"
            single_pattern = r'(\d+)'
            match = re.search(single_pattern, age_range)

            if match:
                age = int(match.group(1))
                return age, age

        except (ValueError, AttributeError):
            pass

        return None, None

    def validate_category_age_range(self, age_range_str):
        """Validar que el rango de edad sea válido"""
        if not age_range_str or not age_range_str.strip():
            return False, "El rango de edad es requerido"

        min_age, max_age = self.parse_age_range(age_range_str)

        if min_age is None or max_age is None:
            return False, "Formato de edad inválido. Use: '12-13' o '12 a 13' o '12'"

        if min_age < 5 or max_age > 80:
            return False, "Las edades deben estar entre 5 y 80 años"

        if min_age > max_age:
            return False, "La edad inicial debe ser menor o igual que la final"

        return True, f"{min_age}-{max_age}" if min_age != max_age else str(min_age)

    def sort_categories_by_age(self, categories):
        """Ordenar categorías por rango de edad (menor a mayor)"""
        def get_sort_key(category):
            min_age, max_age = self.parse_age_range(category.get('age_range', ''))
            return min_age if min_age is not None else 999

        return sorted(categories, key=get_sort_key)

    def format_age_range(self, min_age, max_age):
        """Formatear rango de edad en string estándar"""
        if min_age == max_age:
            return str(min_age)
        else:
            return f"{min_age}-{max_age}"

    def generate_event_pdf_report(self):
        """Generar reporte PDF del evento configurado"""
        if not REPORTLAB_AVAILABLE:
            return None, "ReportLab no está disponible"

        event_info = self.get_event_info()
        if not event_info:
            return None, "No hay evento configurado"

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from reportlab.platypus.flowables import Image
            from io import BytesIO

            # Colores del tema TEN
            TEN_BLUE = colors.HexColor('#1E88E5')
            TEN_LIGHT_BLUE = colors.HexColor('#64B5F6')
            TEN_DARK_BLUE = colors.HexColor('#1565C0')
            TEN_ACCENT = colors.HexColor('#E3F2FD')

            # Crear buffer para PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=72)

            story = []
            styles = getSampleStyleSheet()

            # Estilos personalizados
            title_style = ParagraphStyle('EventTitle',
                                       parent=styles['Heading1'],
                                       fontSize=24,
                                       spaceAfter=20,
                                       alignment=TA_CENTER,
                                       textColor=TEN_DARK_BLUE,
                                       fontName='Helvetica-Bold')

            subtitle_style = ParagraphStyle('EventSubtitle',
                                          parent=styles['Heading2'],
                                          fontSize=16,
                                          spaceAfter=15,
                                          alignment=TA_CENTER,
                                          textColor=TEN_BLUE)

            section_style = ParagraphStyle('SectionHeader',
                                         parent=styles['Heading2'],
                                         fontSize=14,
                                         spaceAfter=12,
                                         textColor=TEN_BLUE,
                                         fontName='Helvetica-Bold')

            # Logo del evento si existe
            if event_info.get('event_logo'):
                try:
                    logo_path = f"event_logos/{event_info['event_logo']}"
                    if os.path.exists(logo_path):
                        logo = Image(logo_path, width=2*inch, height=1.5*inch)
                        logo.hAlign = 'CENTER'
                        story.append(logo)
                        story.append(Spacer(1, 20))
                except:
                    pass

            # Título del evento
            story.append(Paragraph(event_info['name'], title_style))
            story.append(Paragraph("Reporte de Configuración del Evento", subtitle_style))
            story.append(Spacer(1, 30))

            # Mensaje de bienvenida si existe
            welcome_msg = event_info.get('welcome_message', '').strip()
            if welcome_msg:
                story.append(Paragraph("MENSAJE DE BIENVENIDA", section_style))
                welcome_style = ParagraphStyle('Welcome',
                                             parent=styles['Normal'],
                                             fontSize=12,
                                             spaceAfter=15,
                                             alignment=TA_LEFT)
                story.append(Paragraph(welcome_msg.replace('\n', '<br/>'), welcome_style))
                story.append(Spacer(1, 20))

            # Información general
            story.append(Paragraph("INFORMACIÓN GENERAL", section_style))
            general_data = [
                ['Campo', 'Valor'],
                ['Nombre del Evento', event_info['name']],
                ['Rango de Edades', f"{event_info['min_age']} - {event_info['max_age']} años"],
                ['Valor por Nadador', f"${event_info.get('swimmer_fee', 0):,.0f}"],
                ['Valor por Equipo', f"${event_info.get('team_fee', 0):,.0f}"],
                ['Total de Categorías', str(len(event_info['categories']))],
                ['Total de Pruebas', str(len(event_info['events']))],
                ['Fecha de Creación', event_info.get('created_date', '').split('T')[0]],
            ]

            general_table = Table(general_data, colWidths=[2.5*inch, 3*inch])
            general_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), TEN_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), TEN_ACCENT),
                ('GRID', (0, 0), (-1, -1), 1, TEN_DARK_BLUE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(general_table)
            story.append(Spacer(1, 30))

            # Categorías
            story.append(Paragraph("CATEGORÍAS DEL EVENTO", section_style))
            categories_data = [['#', 'Nombre', 'Rango de Edad', 'Pruebas Asignadas']]

            # Ordenar categorías por edad
            sorted_categories = self.sort_categories_by_age(event_info['categories'])

            for i, category in enumerate(sorted_categories, 1):
                cat_name = category['name']
                age_range = category['age_range']
                cat_events = event_info['category_events'].get(cat_name, [])
                events_count = len(cat_events)

                categories_data.append([
                    str(i),
                    cat_name,
                    age_range,
                    str(events_count)
                ])

            categories_table = Table(categories_data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1*inch])
            categories_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), TEN_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), TEN_ACCENT),
                ('GRID', (0, 0), (-1, -1), 1, TEN_DARK_BLUE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(categories_table)
            story.append(Spacer(1, 30))

            # Pruebas del evento
            story.append(Paragraph("PRUEBAS DEL EVENTO (ORDEN)", section_style))
            events_data = [['Orden', 'Prueba']]

            for i, event in enumerate(event_info['events'], 1):
                events_data.append([str(i), event])

            events_table = Table(events_data, colWidths=[1*inch, 4*inch])
            events_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), TEN_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), TEN_ACCENT),
                ('GRID', (0, 0), (-1, -1), 1, TEN_DARK_BLUE),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(events_table)

            # Nueva página para asignaciones detalladas
            story.append(PageBreak())
            story.append(Paragraph("ASIGNACIÓN DETALLADA DE PRUEBAS POR CATEGORÍA", section_style))

            for category in sorted_categories:
                cat_name = category['name']
                age_range = category['age_range']
                cat_events = event_info['category_events'].get(cat_name, [])

                story.append(Paragraph(f"{cat_name} ({age_range})",
                                     ParagraphStyle('CategoryName', parent=styles['Heading3'],
                                                  fontSize=12, textColor=TEN_DARK_BLUE,
                                                  spaceAfter=8)))

                if cat_events:
                    events_text = ", ".join(cat_events)
                    story.append(Paragraph(events_text, styles['Normal']))
                else:
                    story.append(Paragraph("<i>Sin pruebas asignadas</i>",
                                         ParagraphStyle('NoEvents', parent=styles['Normal'],
                                                      fontName='Helvetica-Oblique',
                                                      textColor=colors.grey)))

                story.append(Spacer(1, 15))

            # Footer
            story.append(Spacer(1, 50))
            footer_style = ParagraphStyle('Footer',
                                        parent=styles['Normal'],
                                        fontSize=8,
                                        alignment=TA_CENTER,
                                        textColor=TEN_DARK_BLUE)
            story.append(Paragraph("Sistema de Gestión de Competencias TEN - Reporte Generado Automáticamente",
                                 footer_style))

            # Generar PDF
            doc.build(story)
            buffer.seek(0)

            # Guardar archivo
            filename = f"reporte_evento_{event_info['name'].replace(' ', '_')}.pdf"
            return buffer.getvalue(), filename

        except Exception as e:
            return None, f"Error generando PDF: {str(e)}"

    def save_event_logo(self, uploaded_file, event_name):
        """Guardar logo del evento"""
        try:
            # Crear directorio para logos si no existe
            logo_dir = "event_logos"
            os.makedirs(logo_dir, exist_ok=True)

            # Generar nombre de archivo único
            file_extension = uploaded_file.name.split('.')[-1].lower()
            safe_event_name = "".join(c for c in event_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            logo_filename = f"{safe_event_name.replace(' ', '_')}_logo.{file_extension}"
            logo_path = os.path.join(logo_dir, logo_filename)

            # Guardar archivo
            with open(logo_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            return True, logo_filename

        except Exception as e:
            return False, f"Error guardando logo: {str(e)}"
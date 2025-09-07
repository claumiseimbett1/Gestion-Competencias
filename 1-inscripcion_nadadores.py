import pandas as pd
import os
from datetime import datetime
from pathlib import Path

class SwimmerRegistration:
    def __init__(self):
        self.archivo_inscripcion = 'planilla_inscripcion.xlsx'
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
    
    def add_swimmer(self, swimmer_data):
        try:
            df_existing = self.load_existing_data()
            
            if df_existing is None:
                success, message = self.create_empty_registration_file()
                if not success:
                    return False, message
                df_existing = self.load_existing_data()
            
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
            
            return True, "Nadador registrado exitosamente"
            
        except Exception as e:
            return False, f"Error al registrar nadador: {e}"
    
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
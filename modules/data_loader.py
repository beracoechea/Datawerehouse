import pandas as pd
import json

def load_data(file_path):
    """Carga datos desde archivos JSON, CSV o Excel."""
    try:
        if file_path.endswith('.json'):
            df = pd.read_json(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Formato de archivo no soportado.")
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        return f"Error al cargar el archivo: {e}"

def get_data_summary(df):
    """Obtiene un resumen básico del DataFrame."""
    if isinstance(df, pd.DataFrame):
        num_registros = len(df)
        num_columnas = df.shape[1]
        columnas = df.columns.tolist()
        preview = df.head().to_dict('records')
        return {"num_registros": num_registros, "num_columnas": num_columnas, "columnas": columnas, "preview": preview}
    return None
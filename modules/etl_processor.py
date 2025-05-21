import pandas as pd

def handle_missing_values(df, method='drop'):
    """Maneja valores nulos."""
    if isinstance(df, pd.DataFrame):
        if method == 'drop':
            return df.dropna()
        elif method == 'fill_mean':
            return df.fillna(df.mean(numeric_only=True))
        elif method == 'fill_median':
            return df.fillna(df.median(numeric_only=True))
    return df

def remove_duplicates(df, subset=None):
    """Elimina filas duplicadas."""
    if isinstance(df, pd.DataFrame):
        return df.drop_duplicates(subset=subset)
    return df

def correct_data_types(df, column_types):
    """Corrige los tipos de datos de las columnas."""
    if isinstance(df, pd.DataFrame):
        try:
            return df.astype(column_types)
        except Exception as e:
            return f"Error al convertir tipos de datos: {e}"
    return df

def normalize_data(df, columns):
    """Normaliza los datos utilizando MinMaxScaler."""
    if isinstance(df, pd.DataFrame) and columns:
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        df[columns] = scaler.fit_transform(df[columns])
    return df

def filter_data(df, column, condition, value):
    """Filtra datos basado en una condición."""
    if isinstance(df, pd.DataFrame) and column in df.columns:
        if condition == 'greater_than':
            return df[df[column] > value]
        elif condition == 'less_than':
            return df[df[column] < value]
        elif condition == 'equals':
            return df[df[column] == value]
    return df

def aggregate_data(df, group_by, aggregation):
    """Agrega datos."""
    if isinstance(df, pd.DataFrame) and group_by in df.columns and aggregation:
        try:
            return df.groupby(group_by).agg(aggregation).reset_index()
        except Exception as e:
            return f"Error al agregar datos: {e}"
    return df

def apply_etl_transformations(df):
    df = df.dropna()
    df = df.drop_duplicates()
    for col in df.select_dtypes(include='number').columns:
        df[col] = (df[col] - df[col].mean()) / df[col].std()  # normalización
    return df

import pandas as pd

def get_descriptive_stats(df):
    """Obtiene estadísticas descriptivas."""
    if isinstance(df, pd.DataFrame):
        return df.describe().to_dict()
    return None

def get_column_distributions(df, column):
    """Obtiene la distribución de una columna."""
    if isinstance(df, pd.DataFrame) and column in df.columns:
        return df[column].value_counts().to_dict()
    return None
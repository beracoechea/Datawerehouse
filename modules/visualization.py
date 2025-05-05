import plotly.express as px
import pandas as pd

def create_summary_table(summary):
    """Crea una tabla de resumen."""
    if summary:
        return pd.DataFrame([summary]).to_dict('records')
    return []

def create_preview_table(data):
    """Crea una tabla de previsualización de datos."""
    if isinstance(data, list) and data:
        return data
    return []

def create_histogram(df, column):
    """Crea un histograma."""
    if isinstance(df, pd.DataFrame) and column in df.columns:
        return px.histogram(df, x=column)
    return {}

def create_boxplot(df, column):
    """Crea un boxplot."""
    if isinstance(df, pd.DataFrame) and column in df.columns:
        return px.box(df, y=column)
    return {}

def create_scatter_plot(df, x_col, y_col, color=None):
    """Crea un scatter plot."""
    if isinstance(df, pd.DataFrame) and x_col in df.columns and y_col in df.columns:
        return px.scatter(df, x=x_col, y=y_col, color=color)
    return {}

def create_heatmap(df, values, x, y):
    """Crea un heatmap."""
    if isinstance(df, pd.DataFrame) and values in df.columns and x in df.columns and y in df.columns:
        pivot_table = df.pivot_table(values=values, index=y, columns=x)
        return px.imshow(pivot_table, color_continuous_scale='viridis')
    return {}

def create_dendrogram(df, columns):
    """Crea un dendrograma (requiere scipy y plotly.figure_factory)."""
    if isinstance(df, pd.DataFrame) and len(columns) >= 2:
        from scipy.cluster.hierarchy import linkage
        import plotly.figure_factory as ff
        X = df[columns].values
        linked = linkage(X, 'ward')
        return ff.create_dendrogram(linked, orientation='bottom', labels=df.index.tolist())
    return {}
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

def render_mineria_datos(processed_data):
    if 'processed_df' not in processed_data:
        return html.P("No hay datos procesados disponibles. Aplica una transformación en la pestaña de ETL.")
    
    df = processed_data['processed_df']
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()
    all_cols = df.columns.tolist()

    return dbc.Container([
        html.H3("Análisis Exploratorio y Minería de Datos"),
        dbc.Row([
            dbc.Col([
                html.H4("Análisis Exploratorio de Datos (EDA)"),
                dcc.Dropdown(
                    id='eda-histogram-column',
                    options=[{'label': col, 'value': col} for col in numeric_cols],
                    placeholder="Seleccionar columna para histograma"
                ),
                dcc.Graph(id='eda-histogram'),
                dcc.Dropdown(
                    id='eda-boxplot-column',
                    options=[{'label': col, 'value': col} for col in numeric_cols],
                    placeholder="Seleccionar columna para boxplot"
                ),
                dcc.Graph(id='eda-boxplot'),
                html.H5("Estadísticas Descriptivas"),
                html.Div(id='descriptive-stats'),
                html.H5("Distribución de Columnas"),
                dcc.Dropdown(
                    id='column-distribution-column',
                    options=[{'label': col, 'value': col} for col in all_cols],
                    placeholder="Seleccionar columna para distribución"
                ),
                html.Div(id='column-distribution'),
            ], md=6),
            dbc.Col([
                html.H4("Técnicas de Minería de Datos"),
                html.H5("Clustering (K-Means)"),
                dcc.Dropdown(
                    id='kmeans-columns',
                    options=[{'label': col, 'value': col} for col in numeric_cols],
                    multi=True,
                    placeholder="Columnas para K-Means (mínimo 2)"
                ),
                dcc.Slider(id='kmeans-clusters', min=2, max=10, value=3, marks={i: str(i) for i in range(2, 11)}),
                dbc.Button("Aplicar K-Means", id="apply-kmeans", color="success", className="mb-2"),
                dcc.Graph(id='kmeans-scatter'),
                html.Div(id='kmeans-results'),

                html.H5("Clasificación (Árbol de Decisión)"),
                dcc.Dropdown(
                    id='dt-features',
                    options=[{'label': col, 'value': col} for col in all_cols if col not in non_numeric_cols],
                    multi=True,
                    placeholder="Características para clasificación"
                ),
                dcc.Dropdown(
                    id='dt-target',
                    options=[{'label': col, 'value': col} for col in non_numeric_cols],
                    placeholder="Columna objetivo"
                ),
                dbc.Button("Aplicar Árbol de Decisión", id="apply-dt", color="success", className="mb-2"),
                html.Div(id='dt-results'),
            ], md=6),
        ]),
    ])

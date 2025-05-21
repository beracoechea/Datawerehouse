from dash import html, dcc
import dash_bootstrap_components as dbc

def render_toma_decision():
    return dbc.Container([
        html.H3("Visualización para la Toma de Decisión"),
        html.P("Aquí puedes seleccionar visualizaciones específicas generadas en las pestañas anteriores para facilitar la toma de decisiones."),
        
        dcc.Dropdown(
            id='decision-viz-selector',
            options=[
                {'label': 'Tabla de Datos Transformados (ETL)', 'value': 'transformed_table'},
                {'label': 'Histograma (EDA)', 'value': 'eda_histogram'},
                {'label': 'Boxplot (EDA)', 'value': 'eda_boxplot'},
                {'label': 'Gráfico de Dispersión K-Means', 'value': 'kmeans_scatter'}
            ],
            multi=True,
            placeholder="Selecciona las visualizaciones a mostrar"
        ),

        html.Div(id='selected-visualizations-output')
    ])

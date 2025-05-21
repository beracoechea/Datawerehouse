import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from pages import carga_datos, etl, mineria_datos, toma_decision
from callbacks import carga_datos_callbacks, etl_callbacks, mineria_datos_callbacks, toma_decision_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Almacenamiento de datos en memoria
stored_data = {}
processed_data = {}
analysis_results = {}
mining_results = {}

app.layout = dbc.Container(fluid=True, children=[
    html.H1("Almacén de Datos Interactivo"),
    dbc.Tabs([
        dbc.Tab(label="Carga de Datos", tab_id="carga-datos"),
        dbc.Tab(label="ETL", tab_id="etl"),
        dbc.Tab(label="Minería de Datos", tab_id="mineria-datos"),
        dbc.Tab(label="Toma de Decisión", tab_id="toma-decision"),
    ], id="tabs", active_tab="carga-datos"),
    html.Div(id="tab-content"),
])

# Callback para renderizar el contenido de cada pestaña
@app.callback(Output("tab-content", "children"), [Input("tabs", "active_tab")])
def render_tab_content(active_tab):
    if active_tab == "carga-datos":
        return carga_datos.render_carga_datos()
    elif active_tab == "etl":
        return etl.render_etl(stored_data)
    elif active_tab == "mineria-datos":
        return mineria_datos.render_mineria_datos(processed_data)
    elif active_tab == "toma-decision":
        return toma_decision.render_toma_decision()
    return "Selecciona una pestaña"

# Inicializar los callbacks pasando la instancia de app y los diccionarios de almacenamiento
carga_datos_callbacks.register_callbacks(app, stored_data)
etl_callbacks.register_callbacks(app, stored_data, processed_data)
mineria_datos_callbacks.register_callbacks(app, stored_data, processed_data, analysis_results, mining_results)
toma_decision_callbacks.register_callbacks(app, stored_data, processed_data, analysis_results, mining_results)

if __name__ == '__main__':
    app.run(debug=True)
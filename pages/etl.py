from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

def render_etl(stored_data):
    table_style = {
        'style_table': {'overflowX': 'auto', 'maxWidth': '100%'},
        'style_cell': {
            'textAlign': 'left',
            'minWidth': '100px',
            'maxWidth': '180px',
            'whiteSpace': 'nowrap',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'padding': '6px',
            'fontFamily': 'Arial',
            'fontSize': '14px',
        },
        'style_cell_conditional': [
            {'if': {'column_type': 'numeric'}, 'textAlign': 'right'}
        ],
        'style_header': {
            'backgroundColor': '#f8f9fa',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        'style_data': {
            'backgroundColor': 'white',
            'color': 'black'
        }
    }

    if 'raw_df' in stored_data and isinstance(stored_data['raw_df'], pd.DataFrame):
        df = stored_data['raw_df']
        columns = df.columns.tolist()
        return dbc.Container([
            html.H3("Proceso de ETL"),
            dbc.Row([
                dbc.Col([
                    html.H4("Datos Originales"),
                    dash_table.DataTable(
                        id='original-data-table',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.head(10).to_dict('records'),
                        page_size=10,
                        **table_style
                    ),
                    html.Div(id='etl-operations')
                ], md=6),
                dbc.Col([
                    html.H4("Datos Transformados"),
                    html.Div(id='transformed-data-output'),
                ], md=6),
            ]),
            dbc.Row([
                dbc.Col([
                    html.H5("Operaciones de Limpieza"),
                    dcc.Dropdown(
                        id='missing-value-method',
                        options=[
                            {'label': 'Eliminar filas con valores nulos', 'value': 'drop'},
                            {'label': 'Imputar con la media', 'value': 'fill_mean'},
                            {'label': 'Imputar con la mediana', 'value': 'fill_median'},
                        ],
                        placeholder="Manejar valores nulos"
                    ),
                    dbc.Button("Aplicar", id="apply-missing-value", color="primary", className="mr-2"),
                    dcc.Dropdown(
                        id='duplicate-columns',
                        options=[{'label': col, 'value': col} for col in columns],
                        multi=True,
                        placeholder="Columnas para buscar duplicados (opcional)"
                    ),
                    dbc.Button("Eliminar Duplicados", id="apply-duplicates", color="primary", className="mr-2"),
                    html.H5("Operaciones de Transformación"),
                    dcc.Dropdown(
                        id='normalize-columns',
                        options=[{'label': col, 'value': col} for col in df.select_dtypes(include=['number']).columns],
                        multi=True,
                        placeholder="Columnas a normalizar"
                    ),
                    dbc.Button("Normalizar", id="apply-normalization", color="primary", className="mr-2"),
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id='filter-column',
                                options=[{'label': col, 'value': col} for col in columns],
                                placeholder="Filtrar columna"
                            ),
                        ], md=4),
                        dbc.Col([
                            dcc.Dropdown(
                                id='filter-condition',
                                options=[
                                    {'label': 'Mayor que', 'value': 'greater_than'},
                                    {'label': 'Menor que', 'value': 'less_than'},
                                    {'label': 'Igual a', 'value': 'equals'},
                                ],
                                placeholder="Condición"
                            ),
                        ], md=4),
                        dbc.Col([
                            dcc.Input(id='filter-value', type='text', placeholder="Valor"),
                        ], md=4),
                    ], className="mb-2"),
                    dbc.Button("Filtrar", id="apply-filter", color="primary", className="mr-2"),
                ], md=4),
            ]),
        ])
    else:
        return dbc.Container([
            html.H3("Proceso de ETL"),
            html.P("Por favor, carga un archivo en la pestaña 'Carga de Datos' primero.")
        ])

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

def render_carga_datos():
    return dbc.Container([
        html.H3("Carga de Datos"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Arrastra y suelta o ',
                html.A('selecciona archivos')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px 0'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),
        html.Div(id='output-data-upload'),
    ])
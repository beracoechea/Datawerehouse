from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import io
import base64
from modules import data_loader, visualization

def register_callbacks(app, stored_data):
    @app.callback(Output('output-data-upload', 'children'),
                    [Input('upload-data', 'contents')],
                    [State('upload-data', 'filename')])
    def update_output(contents, filename):
        if contents:
            content_type, content_string = contents.split(',')
            try:
                decoded = base64.b64decode(content_string)

                # Leer según tipo de archivo
                if filename.endswith('.json'):
                    df = pd.read_json(io.StringIO(decoded.decode('utf-8')))
                elif filename.endswith('.csv'):
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                elif filename.endswith('.xlsx'):
                    df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
                elif filename.endswith('.xls'):
                    df = pd.read_excel(io.BytesIO(decoded), engine='xlrd')
                else:
                    return html.Div(['Formato de archivo no soportado.'])

                df.columns = [str(col) for col in df.columns]
                stored_data['raw_df'] = df

                summary = data_loader.get_data_summary(df)
                preview_table = visualization.create_preview_table(summary['preview'])

                print("Debugging df.head():")
                print(df.head())

                return html.Div([
                    html.H3(f'Archivo cargado: {filename}'),
                    html.Div(f"Número de registros: {summary['num_registros']}"),
                    html.Div(f"Número de columnas: {summary['num_columnas']}"),
                    html.Div(["Columnas:", html.Ul([html.Li(col) for col in summary['columnas']])]),
                    html.H5("Previsualización de datos:"),
                    dash_table.DataTable(
                        id='table-preview',
                        columns=[{"name": str(i), "id": str(i)} for i in df.columns],
                        data=preview_table,
                        page_size=10
                    ),
                ])
            except Exception as e:
                return html.Div([f'Hubo un error al procesar el archivo: {e}'])
        return html.Div(['Espera a que se cargue un archivo...'])

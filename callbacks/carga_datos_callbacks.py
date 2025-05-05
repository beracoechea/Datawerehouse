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
                if 'json' in filename:
                    df = pd.read_json(content_string)
                elif 'csv' in filename:
                    df = pd.read_csv(content_string)
                elif 'xlsx' in filename:
                    import base64
                    decoded = base64.b64decode(content_string)
                    df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
                elif 'xls' in filename:
                    import base64
                    decoded = base64.b64decode(content_string)
                    df = pd.read_excel(io.BytesIO(decoded), engine='xlrd')
                else:
                    return html.Div(['Formato de archivo no soportado.'])

                # Asegurarse de que los nombres de las columnas sean strings
                df.columns = [str(col) for col in df.columns]

                # Store the DataFrame as a dictionary (serializable)
                stored_data['raw_df_data'] = df.to_dict('records')
                stored_data['raw_df_columns'] = df.columns.tolist()

                summary = data_loader.get_data_summary(df)
                preview_table = visualization.create_preview_table(summary['preview'])

                # 1. Debug: Print the structure of preview_table
                print("Debugging preview_table:")
                print(preview_table)

                # 2. Debug: Print the first few rows of the dataframe
                print("Debugging df.head():")
                print(df.head().to_markdown(index=False, numalign="left", stralign="left"))

                # 3. Debug: Print the columns and their types
                print("Debugging df.info():")
                print(df.info())
                
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

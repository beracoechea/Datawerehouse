import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import json
import io  # Importa la biblioteca io para leer archivos Excel desde la memoria

from modules import data_loader, etl_processor, data_analyzer, data_miner, visualization

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Almacenamiento de datos en memoria (para simplificar el ejemplo)
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
        return render_carga_datos()
    elif active_tab == "etl":
        return render_etl()
    elif active_tab == "mineria-datos":
        return render_mineria_datos()
    elif active_tab == "toma-decision":
        return render_toma_decision()
    return "Selecciona una pestaña"

# Contenido de la pestaña "Carga de Datos"
def render_carga_datos():
    return dbc.Container([
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
            multiple=False
        ),
        html.Div(id='output-data-upload'),
    ])

# Callback para procesar la carga de datos
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
            elif 'xlsx' in filename or 'xls' in filename:
                import base64
                decoded = base64.b64decode(content_string)
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return html.Div(['Formato de archivo no soportado.'])

            stored_data['raw_df'] = df
            summary = data_loader.get_data_summary(df)
            preview_table = visualization.create_preview_table(summary['preview'])

            return html.Div([
                html.H3(f'Archivo cargado: {filename}'),
                html.Div(f"Número de registros: {summary['num_registros']}"),
                html.Div(f"Número de columnas: {summary['num_columnas']}"),
                html.Div(["Columnas:", html.Ul([html.Li(col) for col in summary['columnas']])]),                
                html.H5("Previsualización de datos:"),
                dash_table.DataTable(
                    id='table-preview',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=preview_table,
                    page_size=10
                ),
            ])
        except Exception as e:
            return html.Div([f'Hubo un error al procesar el archivo: {e}'])
    return html.Div(['Espera a que se cargue un archivo...'])

# Contenido de la pestaña "ETL"
def render_etl():
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
                        page_size=10
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
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id='groupby-column',
                                options=[{'label': col, 'value': col} for col in columns],
                                placeholder="Agrupar por"
                            ),
                        ], md=6),
                        dbc.Col([
                            dcc.Dropdown(
                                id='aggregation-functions',
                                options=[
                                    {'label': 'Suma', 'value': 'sum'},
                                    {'label': 'Promedio', 'value': 'mean'},
                                    {'label': 'Mediana', 'value': 'median'},
                                    {'label': 'Conteo', 'value': 'count'},
                                    {'label': 'Mínimo', 'value': 'min'},
                                    {'label': 'Máximo', 'value': 'max'},
                                ],
                                multi=True,
                                placeholder="Funciones de agregación"
                            ),
                        ], md=6),
                    ], className="mb-2"),
                    dbc.Button("Agregar", id="apply-aggregation", color="primary"),
                ], md=4),
            ]),
        ])
    else:
        return dbc.Container([
            html.H3("Proceso de ETL"),
            html.P("Por favor, carga un archivo en la pestaña 'Carga de Datos' primero.")
        ])

# Callbacks para las operaciones de ETL
@app.callback(
    Output('transformed-data-output', 'children'),
    [Input('apply-missing-value', 'n_clicks'),
     Input('apply-duplicates', 'n_clicks'),
     Input('apply-normalization', 'n_clicks'),
     Input('apply-filter', 'n_clicks'),
     Input('apply-aggregation', 'n_clicks')],
    [State('missing-value-method', 'value'),
     State('duplicate-columns', 'value'),
     State('normalize-columns', 'value'),
     State('filter-column', 'value'),
     State('filter-condition', 'value'),
     State('filter-value', 'value'),
     State('groupby-column', 'value'),
     State('aggregation-functions', 'value')],
    prevent_initial_call=True
)
def apply_etl_operations(n1, n2, n3, n4, n5, missing_method, duplicate_cols, normalize_cols,
                         filter_col, filter_cond, filter_val, groupby_col, agg_funcs):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in stored_data['raw_df'].columns],
            data=stored_data['raw_df'].head(10).to_dict('records'),
            page_size=10
        )

    triggered_id = ctx.triggered_id

    df = stored_data.get('raw_df').copy()
    if df is None:
        return html.P("No hay datos cargados para aplicar ETL.")

    if triggered_id == 'apply-missing-value' and missing_method:
        df = etl_processor.handle_missing_values(df, method=missing_method)
    elif triggered_id == 'apply-duplicates' and duplicate_cols:
        df = etl_processor.remove_duplicates(df, subset=duplicate_cols)
    elif triggered_id == 'apply-normalization' and normalize_cols:
        df = etl_processor.normalize_data(df, columns=normalize_cols)
    elif triggered_id == 'apply-filter' and filter_col and filter_cond and filter_val:
        try:
            if df[filter_col].dtype in ['int64', 'float64']:
                filter_val = float(filter_val)
            df = etl_processor.filter_data(df, filter_col, filter_cond, filter_val)
        except ValueError:
            return html.P("Por favor, introduce un valor numérico para filtros en columnas numéricas.")
    elif triggered_id == 'apply-aggregation' and groupby_col and agg_funcs:
        aggregation = {col: agg_funcs for col in df.columns if col != groupby_col and df[col].dtype in ['int64', 'float64']}
        if aggregation:
            df = etl_processor.aggregate_data(df, groupby_col, aggregation)
        else:
            return html.P("Selecciona al menos una función de agregación para columnas numéricas.")

    processed_data['processed_df'] = df
    return dash_table.DataTable(
        id='transformed-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.head(10).to_dict('records'),
        page_size=10
    )

# Contenido de la pestaña "Minería de Datos"
def render_mineria_datos():
    if 'processed_df' in processed_data and isinstance(processed_data['processed_df'], pd.DataFrame):
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
    else:
        return dbc.Container([
            html.H3("Minería de Datos"),
            html.P("Por favor, realiza el proceso de ETL en la pestaña 'ETL' primero.")
        ])

# Callbacks para la pestaña "Minería de Datos"
@app.callback(
    Output('eda-histogram', 'figure'),
    [Input('eda-histogram-column', 'value')]
)
def update_histogram(column):
    if column and 'processed_df' in processed_data:
        return visualization.create_histogram(processed_data['processed_df'], column)
    return {}

@app.callback(
    Output('eda-boxplot', 'figure'),
    [Input('eda-boxplot-column', 'value')]
)
def update_boxplot(column):
    if column and 'processed_df' in processed_data:
        return visualization.create_boxplot(processed_data['processed_df'], column)
    return {}

@app.callback(
    Output('descriptive-stats', 'children'),
    [Input('processed-data-output', 'children')] # Depende de que los datos ETL estén listos
)
def update_descriptive_stats(transformed_data):
    if 'processed_df' in processed_data:
        stats = data_analyzer.get_descriptive_stats(processed_data['processed_df'])
        if stats:
            return dash_table.DataTable(
                id='descriptive-stats-table',
                columns=[{"name": i, "id": i} for i in stats.keys()],
                data=[stats],
            )
        return html.P("No hay estadísticas descriptivas disponibles.")
    return html.P("Realiza el ETL para ver las estadísticas.")

@app.callback(
    Output('column-distribution', 'children'),
    [Input('column-distribution-column', 'value')]
)
def update_column_distribution(column):
    if column and 'processed_df' in processed_data:
        distribution = data_analyzer.get_column_distributions(processed_data['processed_df'], column)
        if distribution:
            return html.Div([html.P(f"{key}: {value}") for key, value in distribution.items()])
        return html.P("No hay distribución disponible para esta columna.")
    return html.P("Selecciona una columna para ver su distribución.")

@app.callback(
    Output('kmeans-scatter', 'figure'),
    Output('kmeans-results', 'children'),
    [Input('apply-kmeans', 'n_clicks')],
    [State('kmeans-columns', 'value'),
     State('kmeans-clusters', 'value')],
    prevent_initial_call=True
)
def run_kmeans(n_clicks, columns, n_clusters):
    if n_clicks and columns and len(columns) >= 2 and 'processed_df' in processed_data:
        df = processed_data['processed_df'].copy()
        df_clustered = data_miner.perform_kmeans_clustering(df, n_clusters, columns)
        if 'cluster' in df_clustered.columns and len(columns) == 2:
            fig = visualization.create_scatter_plot(df_clustered, x_col=columns[0], y_col=columns[1], color='cluster')
            results_text = f"Se aplicó K-Means con {n_clusters} clusters a las columnas: {', '.join(columns)}."
            return fig, html.P(results_text)
        elif 'cluster' in df_clustered.columns and len(columns) > 2:
            # Puedes mostrar un scatter plot de los dos primeros componentes principales si hay más de 2 columnas
            from sklearn.decomposition import PCA
            pca = PCA(n_components=2)
            principal_components = pca.fit_transform(df_clustered[columns])
            pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
            pca_df['cluster'] = df_clustered['cluster']
            fig = visualization.create_scatter_plot(pca_df, x_col='PC1', y_col='PC2', color='cluster')
            results_text = f"Se aplicó K-Means con {n_clusters} clusters a las columnas: {', '.join(columns)}. Visualización de los 2 primeros componentes principales."
            return fig, html.P(results_text)
        else:
            return {}, html.P("No se pudieron realizar los gráficos de K-Means.")
    return {}, html.P("Selecciona al menos dos columnas numéricas y el número de clusters para aplicar K-Means.")

@app.callback(
    Output('dt-results', 'children'),
    [Input('apply-dt', 'n_clicks')],
    [State('dt-features', 'value'),
     State('dt-target', 'value')],
    prevent_initial_call=True
)
def run_decision_tree(n_clicks, features, target):
    if n_clicks and features and target and 'processed_df' in processed_data:
        df = processed_data['processed_df'].copy()
        if all(col in df.columns for col in features + [target]):
            df_classified, predictions, accuracy = data_miner.perform_decision_tree_classification(df, features, target)
            if accuracy is not None:
                return html.P(f"Se aplicó un árbol de decisión para clasificar '{target}' usando las características: {', '.join(features)}. Precisión del modelo: {accuracy:.2f}")
            else:
                return html.P("No se pudo realizar la clasificación con el árbol de decisión.")
        else:
            return html.P("Asegúrate de que todas las características y la columna objetivo estén presentes en los datos.")
    return html.P("Selecciona las características y la columna objetivo para realizar la clasificación.")

# Contenido de la pestaña "Toma de Decisión"
def render_toma_decision():
    return dbc.Container([
        html.H3("Visualización para la Toma de Decisión"),
        html.P("Aquí puedes seleccionar visualizaciones específicas generadas en las pestañas anteriores para facilitar la toma de decisiones."),
        html.Div(id='decision-visualizations'),
        dcc.Dropdown(
            id='decision-viz-selector',
            options=[
                {'label': 'Previsualización de Datos Cargados', 'value': 'preview_table'},
                {'label': 'Tabla de Datos Transformados (ETL)', 'value': 'transformed_table'},
                {'label': 'Histograma (EDA)', 'value': 'eda_histogram'},
                {'label': 'Boxplot (EDA)', 'value': 'eda_boxplot'},
                {'label': 'Gráfico de Dispersión K-Means', 'value': 'kmeans_scatter'},
                # Añade más opciones según las visualizaciones que generes
            ],
            multi=True,
            placeholder="Selecciona las visualizaciones a mostrar"
        ),
        html.Div(id='selected-visualizations-output'),
    ])

@app.callback(
    Output('selected-visualizations-output', 'children'),
    [Input('decision-viz-selector', 'value')],
    [State('output-data-upload', 'children'),
     State('transformed-data-output', 'children'),
     State('eda-histogram', 'figure'),
     State('eda-boxplot', 'figure'),
     State('kmeans-scatter', 'figure')]
)
def display_selected_visualizations(selected_viz, upload_output, etl_output, hist_fig, box_fig, kmeans_fig):
    components = []
    if selected_viz:
        if 'preview_table' in selected_viz and upload_output and isinstance(upload_output, html.Div) and len(upload_output.children) > 5:
            components.append(html.Div([html.H4("Previsualización de Datos Cargados"), upload_output.children[-1]]))
        if 'transformed_table' in selected_viz and etl_output and isinstance(etl_output, dash_table.DataTable):
            components.append(html.Div([html.H4("Tabla de Datos Transformados"), etl_output]))
        if 'eda_histogram' in selected_viz and hist_fig:
            components.append(html.Div([html.H4("Histograma (EDA)"), dcc.Graph(figure=hist_fig)]))
        if 'eda_boxplot' in selected_viz and box_fig:
            components.append(html.Div([html.H4("Boxplot (EDA)"), dcc.Graph(figure=box_fig)]))
        if 'kmeans_scatter' in selected_viz and kmeans_fig:
            components.append(html.Div([html.H4("Gráfico de Dispersión K-Means"), dcc.Graph(figure=kmeans_fig)]))
        # Añade condiciones para otras visualizaciones
    return html.Div(components)

if __name__ == '__main__':
    app.run(debug=True)
from dash import dcc, html, Input, Output, State, dash_table

def register_callbacks(app, stored_data, processed_data, analysis_results, mining_results):
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
            # Añade condiciones para otras visualizaciones que puedas generar
        return html.Div(components)
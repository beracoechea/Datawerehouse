from dash import dcc, html, Input, Output, State, callback_context
import pandas as pd
from modules import visualization, data_analyzer, data_miner
from sklearn.decomposition import PCA

def register_callbacks(app, stored_data, processed_data, analysis_results, mining_results):
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
        [Input('transformed-data-output', 'children')] # Depende de que los datos ETL estén listos
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
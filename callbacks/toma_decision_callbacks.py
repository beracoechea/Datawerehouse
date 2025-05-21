from dash import dcc, html, Input, Output
import pandas as pd
from modules.visualization import create_histogram, create_boxplot, create_scatter_plot
from modules.data_miner import perform_kmeans_clustering
from modules.etl_processor import apply_etl_transformations
import dash_bootstrap_components as dbc

# Cargar el archivo directamente desde la carpeta actual
df_data = pd.read_csv("Automobile_data.csv")
df_etl = apply_etl_transformations(df_data.copy())

def register_callbacks(app, *_):
    @app.callback(
        Output('selected-visualizations-output', 'children'),
        Input('decision-viz-selector', 'value')
    )
    def display_selected_visualizations(selected_viz):
        components = []
        if not selected_viz:
            return html.Div()

        if 'transformed_table' in selected_viz:
            table = dbc.Table.from_dataframe(
    df_etl.head(10),  # muestra solo 10 filas
    striped=True,
    bordered=True,
    hover=True,
    responsive=True,
)
            components.append(html.Div([
                html.H4("Tabla de Datos Transformados (ETL)"),
                table
            ]))

        if 'eda_histogram' in selected_viz:
            col = df_data.select_dtypes(include='number').columns[0]
            fig = create_histogram(df_data, col)
            components.append(html.Div([html.H4("Histograma (EDA)"), dcc.Graph(figure=fig)]))

        if 'eda_boxplot' in selected_viz:
            col = df_data.select_dtypes(include='number').columns[0]
            fig = create_boxplot(df_data, col)
            components.append(html.Div([html.H4("Boxplot (EDA)"), dcc.Graph(figure=fig)]))

        if 'kmeans_scatter' in selected_viz:
            cols = df_data.select_dtypes(include='number').columns[:2]
            df_clustered = perform_kmeans_clustering(df_data.copy(), n_clusters=3, columns=cols)
            fig = create_scatter_plot(df_clustered, cols[0], cols[1], color='cluster')
            components.append(html.Div([html.H4("Gráfico de Dispersión K-Means"), dcc.Graph(figure=fig)]))

        return html.Div(components)

from dash import dcc, html, dash_table, Input, Output, State, callback_context
import pandas as pd
from modules import etl_processor

def register_callbacks(app, stored_data, processed_data):
    @app.callback(
        Output('transformed-data-output', 'children'),
        [Input('apply-missing-value', 'n_clicks'),
         Input('apply-duplicates', 'n_clicks'),
         Input('apply-normalization', 'n_clicks'),
         Input('apply-filter', 'n_clicks')],
        [State('missing-value-method', 'value'),
         State('duplicate-columns', 'value'),
         State('normalize-columns', 'value'),
         State('filter-column', 'value'),
         State('filter-condition', 'value'),
         State('filter-value', 'value')],
        prevent_initial_call=True
    )
    def apply_etl_operations(n1, n2, n3, n4, missing_method, duplicate_cols, normalize_cols,
                             filter_col, filter_cond, filter_val):
        ctx = callback_context
        if not ctx.triggered:
            if 'raw_df' in stored_data and isinstance(stored_data['raw_df'], pd.DataFrame):
                return dash_table.DataTable(
                    columns=[{"name": i, "id": i} for i in stored_data['raw_df'].columns],
                    data=stored_data['raw_df'].head(10).to_dict('records'),
                    page_size=10
                )
            else:
                return html.P("No hay datos cargados para mostrar.")

        triggered_id = ctx.triggered_id
        df = stored_data.get('raw_df')
        if df is None:
            return html.P("No hay datos cargados para aplicar ETL.")

        df = df.copy()

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

        processed_data['processed_df'] = df
        return dash_table.DataTable(
            id='transformed-table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.head(10).to_dict('records'),
            page_size=10,
            style_table={'overflowX': 'auto', 'maxWidth': '100%'},
            style_cell={
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
            style_cell_conditional=[
                {'if': {'column_type': 'numeric'}, 'textAlign': 'right'}
            ],
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data={
                'backgroundColor': 'white',
                'color': 'black'
            }
        )

from dash import Dash, html, dcc
import sqlite3
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from . import ids

def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.VIOLIN_PLOT, 'children'),
        Input(ids.USER_DROPDOWN, 'value')
    )
    def update_violin(users: list[str]) -> html.Div:
        if len(users) == 0:
            return html.Div(id=ids.VIOLIN_PLOT)
        
        connection = sqlite3.connect('/Users/trev/Documents/Python/Spotify_Listening_Analysis/spotify_data.db')

        user_id_query = ' or '.join([f'username="{username}"' for username in users])
        user_id_df = pd.read_sql_query(f'SELECT user_id FROM QUERIES WHERE {user_id_query}', connection)

        user_query = ' or '.join([f'AUDIO_FEATURES.user_id="{user_id}"' for user_id in user_id_df['user_id'].tolist()])

        df = pd.read_sql_query(f'SELECT valence,username from AUDIO_FEATURES INNER JOIN QUERIES on AUDIO_FEATURES.user_id = QUERIES.user_id WHERE {user_query}', connection)

        fig = px.violin(df, x=df['valence'], y=df['username'], box=True, color=df['username'])
        
        return html.Div(dcc.Graph(figure = fig))
    
    return html.Div(id=ids.VIOLIN_PLOT)
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from . import ids
import sqlite3
import pandas as pd

def render(app: Dash) -> html.Div:
    connection = sqlite3.connect('/Users/trev/Documents/Python/Spotify_Listening_Analysis/spotify_data.db')
    users_df = pd.read_sql_query('SELECT USER_ID, USERNAME FROM QUERIES', connection)
    all_users = [users_df['username'].iloc[i] for i in range(len(users_df))]

    @app.callback(
        Output(ids.USER_DROPDOWN, 'value'),
        Input(ids.USER_SELECT_ALL, 'n_clicks')
    )
    def select_all_users(_: int) -> list[str]:
        return all_users

    return html.Div(
        children=[
            html.H6("Spotify User"),
            dcc.Dropdown(
                id=ids.USER_DROPDOWN,
                multi=True, 
                options=[{'label': user, 'value': user} for user in all_users], 
                value=all_users
            ),
            html.Button(
                id=ids.USER_SELECT_ALL,
                className='dropdown-button',
                children=['Select All']
            )
        ]
    )
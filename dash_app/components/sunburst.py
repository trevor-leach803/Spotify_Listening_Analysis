from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import sqlite3
from . import ids
from dash.dependencies import Input, Output

def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.SUNBURST_PLOT, 'children'),
        Input(ids.USER_DROPDOWN, 'value')
    )
    def update_sunburst(users: list[str]) -> html.Div:
        connection = sqlite3.connect('/Users/trev/Documents/Python/Spotify_Listening_Analysis/spotify_data.db')

        # If no users are selected in the dropdown, render nothing
        if len(users) == 0:
            return html.Div(id=ids.SUNBURST_PLOT)
        
        sunburst_plots = []
        current_row = []

        for username in users:
            user_id_df = pd.read_sql_query(f'SELECT user_id FROM QUERIES WHERE username = "{username}"', connection)
            user_id = user_id_df['user_id'].iloc[0]

            sun_df = pd.read_sql_query(f'SELECT * FROM ARTISTS WHERE user_id = "{user_id}"', connection)
            
            # This function generates a sunburst plot for a user's top artists and their popularity
            labels = {'top_track_num':'Number of Top Tracks', 'popularity':'Artist Popularity', 'labels':'Artist', 'parent':'Genre'}
            title = f"Genres for {username}'s Top Artists"
            sun_fig = px.sunburst(sun_df, path=['genres','artist_name'],values='top_track_num',color='popularity',color_continuous_scale='RdBu',color_continuous_midpoint=50,labels=labels,title=title)
            current_row.append(html.Td(dcc.Graph(figure=sun_fig)))

            if len(current_row) == 2 or username == users[-1]:
                sunburst_plots.append(html.Tr(current_row))
    
        return sunburst_plots
    
    return html.Div(id=ids.SUNBURST_PLOT)
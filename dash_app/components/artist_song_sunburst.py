from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import sqlite3
from . import ids
from dash.dependencies import Input, Output

def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.ARTIST_SONG_SUNBURST_PLOT, 'children'),
        Input(ids.USER_DROPDOWN, 'value'), 
        Input(ids.GENRE_ARTIST_SUNBURST_PLOT, 'clickData')
    )
    def update_sunburst(users: list[str], clk_data) -> html.Div:
        # If no users are selected in the dropdown, render nothing
        if len(users) == 0:
            return html.Div(id=ids.ARTIST_SONG_SUNBURST_PLOT)
        
        connection = sqlite3.connect('/Users/trev/Documents/Python/Spotify_Listening_Analysis/spotify_data.db')
        
        sunburst_plots = []
        current_row = []

        for username in users:
            user_id_df = pd.read_sql_query(f'SELECT user_id FROM QUERIES WHERE username = "{username}"', connection)
            user_id = user_id_df['user_id'].iloc[0]

            if not clk_data:
                sun_df = pd.read_sql_query(f'SELECT DISTINCT song_title, song_popularity, genres, ARTISTS.artist_name FROM SONG_INFO LEFT JOIN ARTISTS ON SONG_INFO.artist_id = ARTISTS.artist_id WHERE SONG_INFO.user_id = "{user_id}"', connection)
            else:
                selected_genre = clk_data['points'][0]['id']
                sun_df = pd.read_sql_query(f'SELECT DISTINCT song_title, song_popularity, genres, ARTISTS.artist_name FROM SONG_INFO LEFT JOIN ARTISTS ON SONG_INFO.artist_id = ARTISTS.artist_id WHERE SONG_INFO.user_id = "{user_id}" and genres="{selected_genre}"', connection)
            
            # This function generates a sunburst plot for a user's top artists and their popularity
            labels = {'popularity':'Song Popularity', 'labels':'Song', 'parent':'Artist'}
            title = f"Song Popularity for {username}'s Top Artists"
            sun_fig = px.sunburst(sun_df, path=['artist_name','song_title'],color='song_popularity',color_continuous_scale='RdBu',color_continuous_midpoint=50,labels=labels,title=title)
            current_row.append(html.Td(dcc.Graph(figure=sun_fig)))

            if len(current_row) == 2 or username == users[-1]:
                sunburst_plots.append(html.Tr(current_row))
                current_row = []

        return sunburst_plots

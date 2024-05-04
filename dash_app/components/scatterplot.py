from dash import Dash, html, dcc
import pandas as pd
import os
import requests
from PIL import Image
import sqlite3
import plotly.express as px
from dash.dependencies import Input, Output
from . import ids



def retrieve_and_preprocess_images(df, parent_dir):
    if not os.path.exists(parent_dir):
        os.mkdir(parent_dir)
    
    for _, row in df.iterrows():
        response = requests.get(row['album_image_url'])
        if response.status_code:
            album_title = row['album_title'].replace('/', '')
            image_path = os.path.join(parent_dir, f'{album_title}.png')
            with open(image_path, 'wb') as image:
                image.write(response.content)

    return df


def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.SCATTER_PLOT, 'children'),
        Input(ids.USER_DROPDOWN, 'value')
    )
    def update_scatterplot(users: list[str]) -> html.Div:
        if len(users) == 0:
            return html.Div(id=ids.SCATTER_PLOT)
        
        connection = sqlite3.connect('/Users/trev/Documents/Python/Spotify_Listening_Analysis/spotify_data.db')
        
        scatterplots = []
        current_row = []

        for username in users:
            user_id_df = pd.read_sql_query(f'SELECT user_id FROM QUERIES WHERE username = "{username}"', connection)
            user_id = user_id_df['user_id'].iloc[0]

            scatter_df = pd.read_sql_query(f'SELECT song_info.user_id, album_title, song_popularity, popularity, album_image_url FROM SONG_INFO INNER JOIN ARTISTS ON SONG_INFO.artist_id = ARTISTS.artist_id WHERE song_info.user_id = "{user_id}"', connection)

            parent_dir = os.path.join(os.getcwd(),"Spotify_Listening_Analysis", "album_covers")
            scatter_df = retrieve_and_preprocess_images(scatter_df, parent_dir)

            fig = px.scatter(scatter_df, x='popularity', y='song_popularity', title=f'Artist and Song Popularity for {username}\'s Top Tracks')
            fig.update_xaxes(title_text='Artist Popularity')
            fig.update_yaxes(title_text='Song Popularity')

            for _, row in scatter_df.iterrows():
                image_path = os.path.join(parent_dir, f'{row["album_title"].replace("/", "")}.png')
                image = Image.open(image_path)
                fig.add_layout_image(dict(source=image, x=row['popularity'], y=row['song_popularity'], xref="x", yref="y", xanchor="center", yanchor="middle", sizex=10, sizey=10))

            fig.update_layout(
                xaxis=dict(range=[0, 100]),
                yaxis=dict(range=[0, 100])
            )

            current_row.append(html.Td(dcc.Graph(figure=fig)))

            if len(current_row) == 2 or username == users[-1]:
                scatterplots.append(html.Tr(current_row))

        return scatterplots

    return html.Div(id=ids.SCATTER_PLOT)






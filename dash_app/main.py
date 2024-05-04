from dash_bootstrap_components.themes import BOOTSTRAP
from dash import Dash, html, dcc
from components.layout import create_layout
from components import genre_artist_sunburst, artist_song_sunburst, user_dropdown, scatterplot, violin, ids
import sqlite3
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output


app = Dash(external_stylesheets=[BOOTSTRAP])
app.title = "Spotify Listening Analysis"
#app.layout = html.Div([create_layout(app)], className="app-container")
app.layout = html.Div(
    [
        html.H1(app.title),
        html.Hr(),
        html.Div(
            className='dropdown-container',
            children=[
                user_dropdown.render(app)
            ]
        ),
        html.Hr(),
        dcc.Tabs(
            [
                dcc.Tab(
                    label='Valence', 
                    children=[
                        dcc.Graph(id=ids.VIOLIN_PLOT)
                    ]
                ),
                dcc.Tab(
                    label = 'Artist Genres',
                    id=ids.GENRE_ARTIST_SUNBURST_PLOT
                ),
                dcc.Tab(
                    label='Song Popularity',
                    id=ids.ARTIST_SONG_SUNBURST_PLOT
                )
            ]
        )
    ]
)
    

@app.callback(
    Output(ids.VIOLIN_PLOT, 'figure'),
    Input(ids.USER_DROPDOWN, 'value')
)
def update_violin(users: list[str]):
    if len(users) == 0:
        return html.Div(id=ids.VIOLIN_PLOT)
    
    connection = sqlite3.connect('/Users/trev/Documents/Python/Spotify_Listening_Analysis/spotify_data.db')

    user_id_query = ' or '.join([f'username="{username}"' for username in users])
    user_id_df = pd.read_sql_query(f'SELECT user_id FROM QUERIES WHERE {user_id_query}', connection)

    user_query = ' or '.join([f'AUDIO_FEATURES.user_id="{user_id}"' for user_id in user_id_df['user_id'].tolist()])

    df = pd.read_sql_query(f'SELECT valence,username from AUDIO_FEATURES INNER JOIN QUERIES on AUDIO_FEATURES.user_id = QUERIES.user_id WHERE {user_query}', connection)

    fig = px.violin(df, x=df['valence'], y=df['username'], box=True, color=df['username'])
    
    return fig


@app.callback(
    Output(ids.GENRE_ARTIST_SUNBURST_PLOT, 'children'),
    Input(ids.USER_DROPDOWN, 'value'),
    Input(ids.GENRE_ARTIST_SUNBURST_PLOT, 'clickData')
)
def update_sunburst(users: list[str], clk_data):
    # If no users are selected in the dropdown, render nothing
    if len(users) == 0:
        return html.Div(id=ids.GENRE_ARTIST_SUNBURST_PLOT)
    
    connection = sqlite3.connect('/Users/trev/Documents/Python/Spotify_Listening_Analysis/spotify_data.db')
    
    sunburst_plots = []
    current_row = []

    print(clk_data)

    for username in users:
        user_id_df = pd.read_sql_query(f'SELECT user_id FROM QUERIES WHERE username = "{username}"', connection)
        user_id = user_id_df['user_id'].iloc[0]

        if not clk_data:
            sun_df = pd.read_sql_query(f'SELECT * FROM ARTISTS WHERE user_id = "{user_id}"', connection)
        else:
            selected_genre = clk_data['points'][0]['id']
            sun_df = pd.read_sql_query(f'SELECT * FROM ARTISTS WHERE user_id = "{user_id}" and genres="{selected_genre}', connection)
        
        # This function generates a sunburst plot for a user's top artists and their popularity
        labels = {'top_track_num':'Number of Top Tracks', 'popularity':'Artist Popularity', 'labels':'Artist', 'parent':'Genre'}
        title = f"Genres for {username}'s Top Artists"
        sun_fig = px.sunburst(sun_df, path=['genres','artist_name'],values='top_track_num',color='popularity',color_continuous_scale='RdBu',color_continuous_midpoint=50,labels=labels,title=title)
        current_row.append(html.Td(dcc.Graph(figure=sun_fig)))

        if len(current_row) == 2 or username == users[-1]:
            sunburst_plots.append(html.Tr(current_row))
            current_row = []

    return sunburst_plots


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
    



if __name__ == '__main__':
    app.run()
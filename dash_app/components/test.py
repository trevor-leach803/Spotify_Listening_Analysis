import sqlite3
import pandas as pd

connection = sqlite3.connect('/Users/trev/Documents/Python/Spotify_Listening_Analysis/spotify_data.db')
cursor = connection.cursor()

all_users = ['alioopboots','316v4sknrso7vgm6wfhoffra4axa']
user1 = 'alioopboots'
print(f'SELECT * FROM ARTISTS WHERE user_id = "{user1}"')

list_of_users = [f'user_id = "{user}"' for user in all_users]
query_users = " or ".join(list_of_users)
print(query_users)

if len(all_users) == 1:
    sun_df = pd.read_sql_query(f'SELECT * FROM ARTISTS WHERE user_id = "{all_users}"', connection)
else:
    list_of_users = " or ".join([f'user_id = "{user}"' for user in all_users])
    # query_users = " or ".join(list_of_users)
    # print(query_users)
    sun_df = pd.read_sql_query(f'SELECT * FROM ARTISTS WHERE {list_of_users}', connection)

print(sun_df)

#%%
import pandas as pd
import sqlite3
connection = sqlite3.connect('/Users/trev/Documents/Python/Spotify_Listening_Analysis/spotify_data.db')

users_df = pd.read_sql_query('SELECT USER_ID, USERNAME FROM QUERIES', connection)
list_of_names = [users_df['username'].iloc[i] for i in range(len(users_df))]
print(list_of_names)
#%%


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
        cursor = connection.cursor()
        if len(users) == 0:
            return html.Div(id=ids.SUNBURST_PLOT)
        elif len(users) == 1:
            sun_df = pd.read_sql_query(f'SELECT * FROM ARTISTS WHERE user_id = "{users[0]}"', connection)
        else:
            list_of_users = " or ".join([f'user_id = "{user}"' for user in users])
            sun_df = pd.read_sql_query(f'SELECT * FROM ARTISTS WHERE {list_of_users}', connection)

        # This function generates a sunburst plot for a user's top artists and their popularity
        labels = {'top_track_num':'Number of Top Tracks', 'popularity':'Artist Popularity', 'labels':'Artist', 'parent':'Genre'}
        title = f"Genres for alioopboots' Top Artists"
        sun_fig = px.sunburst(sun_df, path=['genres','artist_name'],values='top_track_num',color='popularity',color_continuous_scale='RdBu',color_continuous_midpoint=50,labels=labels,title=title)
    
        return html.Div(dcc.Graph(figure=sun_fig), id=ids.SUNBURST_PLOT)
    
    return html.Div(id=ids.SUNBURST_PLOT)
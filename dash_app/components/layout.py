from dash import Dash, html, dcc
from . import genre_artist_sunburst, artist_song_sunburst, user_dropdown, scatterplot, violin, ids

def create_layout(app: Dash) -> html.Div:
    return html.Div(
        className="app-div",
        children=[
            html.H1(app.title),
            html.Hr(),
            html.Div(
                className='dropdown-container',
                children=[
                    user_dropdown.render(app)
                ]
            ),
            genre_artist_sunburst.render(app),
            dcc.Store(id=ids.SELECTED_GENRE),
            artist_song_sunburst.render(app),
            #scatterplot.render(app),
            violin.render(app)
        ]
    )
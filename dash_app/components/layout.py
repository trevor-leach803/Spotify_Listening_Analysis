from dash import Dash, html
from . import user_dropdown, sunburst, scatterplot

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
            sunburst.render(app),
            scatterplot.render(app)
        ]
    )
from dash_bootstrap_components.themes import BOOTSTRAP
from dash import Dash, html
from components.layout import create_layout

def main() -> None:
    app = Dash(external_stylesheets=[BOOTSTRAP])
    app.title = "Spotify Listening Analysis"
    app.layout = html.Div([create_layout(app)], style={'width':'100%'})
    app.run()

if __name__ == '__main__':
    main()
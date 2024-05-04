import sqlite3
import pandas as pd

def load_data(path: str) -> pd.DataFrame:
    connection = sqlite3.connect('/Users/trev/Documents/Python/Spotify_Listening_Analysis/spotify_data.db')
    
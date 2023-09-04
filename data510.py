import sqlite3
from dotenv import load_dotenv

#Custom
from visualizations import Visualizations
from data import Data


def main():
    load_dotenv()
    
    query = True
    connection = sqlite3.connect('spotify_data.db')
    cursor = connection.cursor()

    while query:
        data_collector = Data(connection=connection, cursor=cursor)

        if not data_collector.check_database():
            print("Exiting script...")
            exit()

        # Collect the data from the API
        top_tracks = data_collector.collect_songs()
        data_collector.add_user()
        data_collector.add_top_tracks(top_tracks)
        data_collector.collect_audio_features()
        data_collector.collect_artist_info()
        connection.commit()

        if data_collector.username:
            user = data_collector.username
        else:
            user = data_collector.user_id

        # Generate visualizations
        vis = Visualizations(connection,data_collector.user_id,user)
        vis.parallel_coordinates_audio_features()
        vis.sunburst_genres()
        vis.scatterplot()

        user_input = ''
        while user_input.upper() not in ['YES', 'Y', 'NO', 'N']:
            user_input = input("Would you like to query another library? Y/N ")
        if user_input.upper() == "N" or user_input.upper() == "NO":
            query = False
            vis.violin_plot_valence()
            connection.close()
            break         


if __name__ == '__main__':
    main()
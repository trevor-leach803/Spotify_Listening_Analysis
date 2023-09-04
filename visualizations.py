import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
import requests
from PIL import Image


class Visualizations:
    def __init__(self,connection,user_id,user):
        self.connection = connection
        self.user_id = user_id
        self.user = user

    def parallel_coordinates_audio_features(self):
        # This function generates a parallel coordinate plot for audio features from a user's top tracks
        print("Creating parallel coordinates plot of audio features...")
        pc_df = pd.read_sql_query(f'SELECT * from audio_features WHERE user_id = "{self.user_id}"', self.connection)
        title = f"Audio Features for {self.user}'s Top Tracks"
        pc_fig = px.parallel_coordinates(pc_df,dimensions=['instrumentalness','acousticness','loudness','danceability','energy','tempo','valence'],title=title)
        pc_fig.show()


    def sunburst_genres(self):
        # This function generates a sunburst plot for a user's top artists and their popularity
        print("Creating sunburst plot of genres...")
        sun_df = pd.read_sql_query(f'SELECT * FROM ARTISTS WHERE user_id = "{self.user_id}"', self.connection)
        labels = {'top_track_num':'Number of Top Tracks', 'popularity':'Artist Popularity', 'labels':'Artist', 'parent':'Genre'}
        title = f"Genres for {self.user}'s Top Artists"
        sun_fig = px.sunburst(sun_df, path=['genres','artist_name'],values='top_track_num',color='popularity',color_continuous_scale='RdBu',color_continuous_midpoint=50,labels=labels,title=title)
        sun_fig.show()


    def violin_plot_valence(self):
        # This function generates a violin plot to compare all queried users' valence values
        print("Creating violin plot of valence...")
        sns.set(font_scale=1.5)
        violin_df = pd.read_sql_query('SELECT valence,username from AUDIO_FEATURES INNER JOIN QUERIES on AUDIO_FEATURES.user_id = QUERIES.user_id', self.connection)
        sns.violinplot(x=violin_df['valence'], y=violin_df['username'], notch=True, width=0.5)
        plt.title('Valence in Top Tracks', fontsize=30)
        plt.show()


    def getImage(self,path,zoom=1):
        return OffsetImage(plt.imread(path), zoom=zoom)


    def scatterplot(self):
        # This function generates a scatter plot of artist vs. song popularity and plots the song's album cover
        print("Creating scatterplot of album covers...")
        scatter_df = pd.read_sql_query(f'SELECT song_info.user_id,album_title,song_popularity,popularity,album_image_url from SONG_INFO INNER JOIN ARTISTS on SONG_INFO.artist_id = ARTISTS.artist_id WHERE song_info.user_id = "{self.user_id}"', self.connection)

        directory = scatter_df['user_id'][0]
        parent_dir = os.getcwd() + "/album_covers/"
        path = os.path.join(parent_dir, directory)

        x = []
        y = []
        paths = []

        # Create a new directory in the current directory to save the images to
        if not os.path.exists(path):
            os.mkdir(path)

        # Retrieve the image from the URL, save it, and re-save it as a PNG for plotting
        for value in scatter_df.index:
            response = requests.get(scatter_df['album_image_url'][value])
            if response.status_code:
                album_title = scatter_df['album_title'][value]
                if '/' in album_title:
                    album_title = scatter_df['album_title'][value].replace('/','')
                jpegfilename = path+'/'+album_title+'.jpeg'
                pngfilename = path+'/'+album_title+'.png'
                with open(jpegfilename, 'wb') as image:
                    image.write(response.content)
        
                png = Image.open(jpegfilename)
                png.save(pngfilename)
                os.remove(jpegfilename)

                # Append the values to the lists for plotting
                x.append(scatter_df['popularity'][value])
                y.append(scatter_df['song_popularity'][value])
                paths.append(pngfilename)

        # Create the plot
        plt.rcParams['figure.figsize'] = (22,20)
        fig, ax = plt.subplots()
        ax.scatter(x, y) 
        ax.set_xlim([0,100])
        ax.set_ylim([0,100])
        plt.title(f'Artist and Song Popularity for {self.user}\'s Top Tracks', fontsize=30)
        plt.xlabel('Artist Popularity', fontsize=20)
        plt.ylabel('Song Popularity', fontsize=20)

        # Plot the image on the scatter plot
        for x0, y0, path in zip(x, y, paths):
            ab = AnnotationBbox(self.getImage(path), (x0, y0), frameon=False)
            ax.add_artist(ab)

        plt.show()
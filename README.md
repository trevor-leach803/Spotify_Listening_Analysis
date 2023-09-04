# Spotify_Listening_Analysis
Final project for DATA 510 at CofC. Uses Spotify API and Spotipy Python library to pull user top tracks and make visualizations with Plotly and Matplotlib.

Steps for use:
1. Go to https://developer.spotify.com/dashboard/ and sign up for a developer account
2. Create an application with whatever name and description
3. Click Edit Settings and specify a redirect URI. I did http://127.0.0.1:9090/callback/
4. Copy the Client ID, Secret Client ID, and Redirect URI into a .env file with the format:
    + SPOTIPY_CLIENT_ID='<client_id>'
    + SPOTIPY_CLIENT_SECRET='<client_secret>'
    + SPOTIPY_REDIRECT_URI='<redirect_uri>'

Running this script will first check the database for whether the user_id has been queried already. If so, it will ask whether the user wants to replace the old data with the new query data. If so, those lines are deleted from the database and the folder of album covers is removed. If not, the script ends.

If the user_id has not been queried before OR if the user wants to re-query the user_id, the script will take the user to a browser to sign into Spotify and provide permission to access their data.

It will then store that information into a SQLite database of 4 tables and then produce 3 visualizations. 

NOTE: You must close the window of the matplotlib visualizations for the script to continue. Otherwise, it will look like the code is in an infinite loop

The user will be prompted if they would like to query another person's Spotify account. If yes, the above will run again. Otherwise, a violin plot will be created using the information for each user already in the database and the script will end.

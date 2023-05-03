# Test
Final project for DATA 510 at CofC. Uses Spotify API and Spotipy Python library to pull user top tracks and make visualizations with Plotly and Matplotlib.

Steps for use:
1. Go to https://developer.spotify.com/dashboard/ and sign up for a developer account
2. Create an application with whatever name and description
3. Click Edit Settings and specify a redirect URI. I did http://127.0.0.1:9090/callback/
4. Copy the Client ID, Secret Client ID, and Redirect URI into the credentials.txt file

Running this script will take the user to a browser to sign into Spotify and provide permission to access their data.

It will then store that information into a SQLite database of 4 tables.

It will produce 3 visualizations. 

NOTE: You must close the window of the matplotlib visualizations for the script to continue. Otherwise, it will look like the code is in an infinite loop

The user will be prompted if they would like to query another person's Spotify account.

If yes, the above will run again.

If no, a violin plot will be created using the information for each user already in the database and the script will end.

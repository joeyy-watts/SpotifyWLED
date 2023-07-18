# SpotifyWLED
A simple script to listen to the currently playing track on your Spotify account and forward it to a WLED (https://github.com/Aircoookie/WLED) LED matrix.

## Usage
1. Setup an App in your Spotify dashboard (https://developer.spotify.com/dashboard)
2. Add your active Spotify account as a user of the App
3. Copy the Client ID and Client Secret into the `client_id.conf` and `client_secret.conf` files respectively 
   1. alternatively, export them to environment variables `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
4. Add your WLED device's IP address (with `http://`; add port, if applicable) to `wled.conf` file
5. Start the script using `main.py`
   1. Upon first run, it will prompt you to log in to Spotify and authorize the app. Follow the instructions.
6. Start playing music on the same Spotify account, and hit `localhost:8081/start` to start

![SpotifyWLED](./spotifywled.png)

# THIS PROJECT IS CURRENTLY ON HOLD
As the performance is quite poor due to the entire thing being in Python, I've decided to rebuild it in Rust (yes, I know :P).

**Development is underway [here](https://github.com/joeyy-watts/rustify-wled).**

# SpotifyWLED
A not-so-simple script to listen to the currently playing track on your Spotify account and forward it to a WLED (https://github.com/Aircoookie/WLED) LED matrix.


_This was created as a fun little side project, please don't mind any less-than-stellar coding standards :)_

_(maybe I'll get around to refactoring it one day..)_

## Features
- Displays the album cover of your currently playing track
- Animations!
  - While playing, the cover pulses to the track's tempo
  - Also pulses slowly when the track is paused
  - _and a lot more to come.._


## Usage
1. Setup an App in your Spotify dashboard (https://developer.spotify.com/dashboard)
2. Add your active Spotify account as a user of the App
3. Copy the Client ID and Client Secret into the `client_id.conf` and `client_secret.conf` files respectively 
   1. alternatively, export them to environment variables `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
4. Add your WLED device's IP address (with `http://`; add port, if applicable) to `wled.conf` file
5. Start the script using `main.py`
   1. Upon first run, it will prompt you to log in to Spotify and authorize the app. Follow the instructions.
6. Start playing music on the same Spotify account, and hit `localhost:8081/start` to start


## Credits
- [Pixelated Font](https://www.dafont.com/pixelated.font) used in the logo, by [Skylar Park](https://www.dafont.com/skylar-park.d2956)
- [WLED](https://github.com/Aircoookie/WLED), by [Aircoookie](https://github.com/Aircoookie)
- [Spotipy](https://github.com/spotipy-dev/spotipy), by [Paul Lamere](https://github.com/plamere)

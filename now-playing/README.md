Requirements

- Python 3.10 or newer: download from (https://www.python.org/downloads/)
- A Spotify account
- A Spotify Developer app

1. Clone the project
   Write this in the terminal:

```
git clone https://github.com/dippityy/CyberdeckCSS360.git
cd CyberdeckCSS360/now-playing
```

2. Install the required packages
   Write this in the terminal:

```
pip install flask requests python-dotenv pytest
```

3. Set up your Spotify Developer credentials

1) Go to (https://developer.spotify.com/dashboard) and log in.
2) Click Create app. Fill in any name and description.
3) For the Redirect URI, enter: `http://127.0.0.1:5000/callback`
4) Once the app is created, copy your Client ID and Client Secret from the dashboard.
5) In the project folder, copy `.env.example` to a new file called `.env` by writing this in the terminal:
   ```
   cp .env.example .env
   ```
6) Open `.env` and paste in your credentials:
   ```
   CLIENT_ID="your_client_id_here"
   CLIENT_SECRET="your_client_secret_here"
   REDIRECT_URI="http://127.0.0.1:5000/callback"
   ```

4. Run the app
   Write this in the terminal:

```
python now_playing.py
```

Open your browser to [http://127.0.0.1:5000]. You'll be redirected to Spotify to log in, and then back to the app where the currently playing song will be displayed.

5. Run the test suite
   Write this in the terminal:

```
pytest
```

What the tests cover

1. Token handling

- Storing an access token saves it correctly
- Storing a refresh token saves it when one is provided
- `get_access_token` returns `None` when no one is logged in
- `get_access_token` returns the cached token when it's still valid

2. Currently playing data

- Returns `None` when nothing is playing on Spotify (status 204)
- Correctly gets the song name, artist, album, and album cover from a Spotify response

3. Flask routes

- The home page (`/`) redirects to `/login` when the user isn't authenticated
- The `/login` route redirects to Spotify's authorization page

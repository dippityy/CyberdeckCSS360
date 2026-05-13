import os

from dotenv import load_dotenv
from flask import Flask, redirect, request

load_dotenv()

from spotipy import Spotify
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
FLASK_URL = os.getenv("FLASK_URL", "http://127.0.0.1:5000")

cache_handler = CacheFileHandler(cache_path=".spotify_cache")
sp_oauth = SpotifyOAuth(
    client_id,
    client_secret,
    f"{FLASK_URL}/callback",
    scope="user-read-playback-state",
    cache_handler=cache_handler,
    show_dialog=True,
)
sp = Spotify(auth_manager=sp_oauth)


@app.route("/")
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return redirect(sp_oauth.get_authorize_url())

    playback = sp.current_playback()

    if playback and playback.get("item"):
        track = playback["item"]
        name = track["name"]
        artist = track["artists"][0]["name"]
        ms = playback["progress_ms"]
        time = f"{ms // 60000}:{str((ms % 60000) // 1000).zfill(2)}"

        cover = track["album"]["images"][0]["url"]
        return f"""
        <img src="{cover}" width="200"><br><br>
        <b>{name}</b><br>
        {artist}<br>
        {time}
        """
    else:
        return "Nothing playing."


@app.route("/callback")
def callback():
    sp_oauth.get_access_token(request.args.get("code"))
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

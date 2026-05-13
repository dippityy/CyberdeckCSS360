import os

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, session, url_for
from flask_cors import CORS

load_dotenv()

from spotipy import Spotify
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
CORS(app, supports_credentials=True)


client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

FLASK_URL = "http://127.0.0.1:5000"
REACT_URL = os.getenv("REACT_URL")

redirect_url = f"{FLASK_URL}/callback"
scope = "user-read-playback-state user-modify-playback-state"

cache_handler = CacheFileHandler(cache_path=".spotify_cache")

sp_oauth = SpotifyOAuth(
    client_id,
    client_secret,
    redirect_url,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True,
)

sp = Spotify(auth_manager=sp_oauth)


@app.route("/")
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(REACT_URL)


@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return jsonify({"error": "No code returned from Spotify"}), 400

    sp_oauth.get_access_token(code)
    return redirect(REACT_URL)


@app.route("/playback")
def playback():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return jsonify({"auth_required": True, "auth_url": f"{FLASK_URL}/login"})

    playback_info = sp.current_playback()

    if playback_info and playback_info.get("item"):
        return jsonify(
            {
                "auth_required": False,
                "track_name": playback_info["item"]["name"],
                "artist_name": playback_info["item"]["artists"][0]["name"],
                "is_playing": playback_info["is_playing"],
                "progress_ms": playback_info["progress_ms"],
                "cover_URL": playback_info["item"]["album"]["images"][0]["url"],
            }
        )
    else:
        return jsonify(
            {
                "auth_required": False,
                "message": "No track currently playing",
                "is_playing": False,
            }
        )


@app.route("/playpause", methods=["POST"])
def toggleplayback():
    playback = sp.current_playback()

    if playback and playback["is_playing"]:
        sp.pause_playback()
        return jsonify({"success": True})

    else:
        sp.start_playback()
        return jsonify({"success": True})


@app.route("/next", methods=["POST"])
def skip_next():
    sp.next_track()
    return jsonify({"success": True})


@app.route("/previous", methods=["POST"])
def skip_previous():
    sp.previous_track()
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True)

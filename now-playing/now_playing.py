import os
import time
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for

load_dotenv()

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://127.0.0.1:5000/callback")
SCOPES = "user-read-currently-playing user-read-playback-state"

app = Flask(__name__, template_folder=".")

_token_state = {"access_token": None, "expires_at": 0, "refresh_token": None}


def _exchange(data):
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data=data,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    response.raise_for_status()
    return response.json()


def _store_tokens(payload):
    _token_state["access_token"] = payload["access_token"]
    _token_state["expires_at"] = time.time() + payload["expires_in"] - 60
    if "refresh_token" in payload:
        _token_state["refresh_token"] = payload["refresh_token"]


def get_access_token():
    if _token_state["access_token"] and time.time() < _token_state["expires_at"]:
        return _token_state["access_token"]
    if _token_state["refresh_token"]:
        try:
            _store_tokens(
                _exchange(
                    {
                        "grant_type": "refresh_token",
                        "refresh_token": _token_state["refresh_token"],
                    }
                )
            )
            return _token_state["access_token"]
        except requests.HTTPError:
            _token_state["refresh_token"] = None
    return None


def fetch_web_api(endpoint, method="GET", body=None):
    token = get_access_token()
    if not token:
        return None
    response = requests.request(
        method=method,
        url=f"https://api.spotify.com/{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        json=body,
    )
    if response.status_code == 204:
        return None
    response.raise_for_status()
    return response.json()


def get_currently_playing():
    playback = fetch_web_api("v1/me/player/currently-playing")
    if not playback or not playback.get("item"):
        return None
    item = playback["item"]
    return {
        "name": item["name"],
        "artists": ", ".join(a["name"] for a in item["artists"]),
        "album": item["album"]["name"],
        "cover": item["album"]["images"][0]["url"],
        "is_playing": playback.get("is_playing", False),
    }


@app.route("/")
def index():
    if not get_access_token():
        return redirect(url_for("login"))
    return render_template("index.html", track=get_currently_playing())


@app.route("/login")
def login():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    return redirect(f"https://accounts.spotify.com/authorize?{urlencode(params)}")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    _store_tokens(
        _exchange(
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            }
        )
    )
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()

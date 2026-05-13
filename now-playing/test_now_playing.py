import os

os.environ.setdefault("CLIENT_ID", "test_client_id")
os.environ.setdefault("CLIENT_SECRET", "test_client_secret")
os.environ.setdefault("REDIRECT_URI", "http://127.0.0.1:5000/callback")

from unittest.mock import patch

import now_playing
import pytest


@pytest.fixture(autouse=True)
def reset_token_state():
    now_playing._token_state.update(
        {
            "access_token": None,
            "expires_at": 0,
            "refresh_token": None,
        }
    )


# ---- Token handling ----


def test_store_tokens_saves_access_token():
    now_playing._store_tokens({"access_token": "abc123", "expires_in": 3600})
    assert now_playing._token_state["access_token"] == "abc123"


def test_store_tokens_saves_refresh_token_when_present():
    now_playing._store_tokens(
        {"access_token": "abc", "expires_in": 3600, "refresh_token": "refresh_xyz"}
    )
    assert now_playing._token_state["refresh_token"] == "refresh_xyz"


def test_get_access_token_returns_none_when_not_logged_in():
    assert now_playing.get_access_token() is None


def test_get_access_token_returns_cached_token_when_valid():
    now_playing._store_tokens({"access_token": "cached", "expires_in": 3600})
    assert now_playing.get_access_token() == "cached"


# ---- Currently playing ----


def test_get_currently_playing_returns_none_when_nothing_plays():
    now_playing._store_tokens({"access_token": "fake", "expires_in": 3600})
    with patch("now_playing.requests.request") as mock_req:
        mock_req.return_value.status_code = 204
        assert now_playing.get_currently_playing() is None


def test_get_currently_playing_extracts_song_info():
    now_playing._store_tokens({"access_token": "fake", "expires_in": 3600})
    spotify_response = {
        "is_playing": True,
        "item": {
            "name": "Solo",
            "artists": [{"name": "Frank Ocean"}],
            "album": {
                "name": "Blonde",
                "images": [{"url": "http://example.com/cover.jpg"}],
            },
        },
    }
    with patch("now_playing.requests.request") as mock_req:
        mock_req.return_value.status_code = 200
        mock_req.return_value.json.return_value = spotify_response
        track = now_playing.get_currently_playing()

    assert track["name"] == "Solo"
    assert track["artists"] == "Frank Ocean"
    assert track["album"] == "Blonde"
    assert track["cover"] == "http://example.com/cover.jpg"
    assert track["is_playing"] is True


# ---- Flask routes ----


def test_index_redirects_to_login_when_not_authenticated():
    client = now_playing.app.test_client()
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_redirects_to_spotify():
    client = now_playing.app.test_client()
    response = client.get("/login")
    assert response.status_code == 302
    assert "accounts.spotify.com/authorize" in response.headers["Location"]

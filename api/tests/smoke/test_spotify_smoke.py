"""
Smoke tests for the CyberdeckCSS360 Spotify API backend.

Covers every route defined in api/api.py using unittest.mock so no
real Spotify credentials or network calls are needed in CI.

The CI/CD pipeline runs these as:
    cd api && pytest tests/smoke/ -v
"""

import os
import sys
import json
import unittest.mock as mock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

_FAKE_ENV = {
    "SPOTIPY_CLIENT_ID": "fake_client_id_ci",
    "SPOTIPY_CLIENT_SECRET": "fake_client_secret_ci",
    "SPOTIPY_REDIRECT_URI": "http://localhost:5000/callback",
    "REACT_URL": "http://localhost:5173",
    "SECRET_KEY": "ci_test_secret",
}

FAKE_PLAYBACK_ACTIVE = {
    "is_playing": True,
    "progress_ms": 45_000,
    "item": {
        "name": "Smoke Test Song",
        "duration_ms": 200_000,
        "artists": [{"name": "Smoke Test Artist"}],
        "album": {
            "name": "Smoke Test Album",
            "images": [{"url": "http://example.com/cover.jpg"}],
        },
    },
}

FAKE_PLAYLISTS = {
    "items": [{"id": "pl_001", "name": "Chill Vibes",
               "images": [{"url": "http://example.com/pl.jpg"}],
               "owner": {"display_name": "Test User"}}]
}

FAKE_ALBUMS = {
    "items": [{"album": {"id": "alb_001", "name": "Test Album",
                         "uri": "spotify:album:alb_001",
                         "artists": [{"name": "Test Artist"}],
                         "images": [{"url": "http://example.com/alb.jpg"}]}}]
}

FAKE_RECENT = {
    "items": [{"track": {"id": "t1", "name": "Recent Song",
                         "artists": [{"id": "a1", "name": "Recent Artist"}]}}]
}

FAKE_TOP_ARTISTS = {"items": [{"id": "a2", "name": "Top Artist"}]}
FAKE_TOP_TRACKS = {"items": [{"id": "t2"}]}
FAKE_SEARCH_RESULTS = {
    "tracks": {"items": [{"id": "t3", "name": "Discovered Song",
                          "uri": "spotify:track:t3",
                          "artists": [{"id": "a1", "name": "Recent Artist"}],
                          "album": {"images": [{"url": "http://example.com/disc.jpg"}]}}]}
}


@pytest.fixture(scope="session")
def app():
    with mock.patch.dict(os.environ, _FAKE_ENV):
        fake_token = {"access_token": "fake_access_token",
                      "refresh_token": "fake_refresh_token",
                      "token_type": "Bearer", "expires_at": 9_999_999_999,
                      "scope": "user-read-playback-state"}
        mock_cache = mock.MagicMock()
        mock_cache.get_cached_token.return_value = fake_token
        mock_oauth = mock.MagicMock()
        mock_oauth.validate_token.return_value = True
        mock_oauth.get_authorize_url.return_value = "https://accounts.spotify.com/authorize?fake=1"
        mock_oauth.get_access_token.return_value = fake_token
        mock_sp = mock.MagicMock()
        with mock.patch("spotipy.cache_handler.CacheFileHandler", return_value=mock_cache), \
             mock.patch("spotipy.oauth2.SpotifyOAuth", return_value=mock_oauth), \
             mock.patch("spotipy.Spotify", return_value=mock_sp):
            import api
            api.app.config.update({"TESTING": True, "SECRET_KEY": "ci_test_secret"})
            api.app._test_mock_oauth = mock_oauth
            api.app._test_mock_sp = mock_sp
            yield api.app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def sp(app):
    s = app._test_mock_sp
    s.reset_mock()
    s.current_playback.return_value = FAKE_PLAYBACK_ACTIVE
    s.current_user_playlists.return_value = FAKE_PLAYLISTS
    s.current_user_saved_albums.return_value = FAKE_ALBUMS
    s.current_user_recently_played.return_value = FAKE_RECENT
    s.current_user_top_artists.return_value = FAKE_TOP_ARTISTS
    s.current_user_top_tracks.return_value = FAKE_TOP_TRACKS
    s.search.return_value = FAKE_SEARCH_RESULTS
    return s


@pytest.fixture()
def oauth(app):
    return app._test_mock_oauth


@pytest.mark.skip(reason="Home route serves React build from ../dist (not present in CI)")
class TestHomeRoute:
    def test_home_authenticated(self, client, oauth):
        oauth.validate_token.return_value = True
        assert client.get("/").status_code in (302, 200)

    def test_home_unauthenticated(self, client, oauth):
        oauth.validate_token.return_value = False
        assert client.get("/").status_code in (302, 200)


class TestLoginRoute:
    def test_login_redirects(self, client):
        assert client.get("/login").status_code == 302

    def test_login_no_crash(self, client):
        assert client.get("/login").status_code != 500


class TestCallbackRoute:
    def test_callback_no_code_returns_400(self, client):
        resp = client.get("/callback")
        assert resp.status_code == 400
        assert "error" in json.loads(resp.data)

    def test_callback_with_code_no_crash(self, client, oauth):
        oauth.get_access_token.return_value = {"access_token": "tok"}
        assert client.get("/callback?code=fake").status_code in (200, 302)


class TestPlaybackRoute:
    def test_playback_with_track(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        resp = client.get("/api/playback")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("auth_required") is False
        assert data["track_name"] == "Smoke Test Song"
        for k in ("artist_name", "is_playing", "progress_ms", "duration_ms", "cover_URL"):
            assert k in data

    def test_playback_nothing_playing(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        sp.current_playback.return_value = None
        assert json.loads(client.get("/api/playback").data).get("is_playing") is False

    def test_playback_unauthenticated(self, client, oauth):
        oauth.validate_token.return_value = False
        data = json.loads(client.get("/api/playback").data)
        assert data.get("auth_required") is True
        assert "auth_url" in data


class TestPlayPauseRoute:
    def test_pause_when_playing(self, client, sp):
        sp.current_playback.return_value = {"is_playing": True}
        resp = client.post("/api/playpause")
        assert resp.status_code == 200
        assert json.loads(resp.data).get("success") is True
        sp.pause_playback.assert_called_once()

    def test_resume_when_paused(self, client, sp):
        sp.current_playback.return_value = {"is_playing": False}
        assert json.loads(client.post("/api/playpause").data).get("success") is True
        sp.start_playback.assert_called_once()

    def test_start_when_nothing_playing(self, client, sp):
        sp.current_playback.return_value = None
        client.post("/api/playpause")
        sp.start_playback.assert_called_once()


class TestNextRoute:
    def test_next_returns_success(self, client, sp):
        resp = client.post("/api/next")
        assert resp.status_code == 200
        assert json.loads(resp.data).get("success") is True
        sp.next_track.assert_called_once()

    def test_next_no_crash(self, client):
        assert client.post("/api/next").status_code != 500


class TestPreviousRoute:
    def test_previous_returns_success(self, client, sp):
        resp = client.post("/api/previous")
        assert resp.status_code == 200
        assert json.loads(resp.data).get("success") is True
        sp.previous_track.assert_called_once()

    def test_previous_no_crash(self, client):
        assert client.post("/api/previous").status_code != 500


class TestDiscoverRoute:
    def test_discover_authenticated(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        data = json.loads(client.get("/api/discover").data)
        assert data.get("auth_required") is False
        assert isinstance(data.get("suggestions"), list)

    def test_discover_unauthenticated(self, client, oauth):
        oauth.validate_token.return_value = False
        assert json.loads(client.get("/api/discover").data).get("auth_required") is True

    def test_discover_no_crash(self, client):
        assert client.get("/api/discover").status_code != 500


class TestPlaylistsRoute:
    def test_playlists_authenticated(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        data = json.loads(client.get("/api/playlists").data)
        assert data.get("auth_required") is False
        pl = data["playlists"][0]
        for k in ("id", "name", "cover_url", "owner"):
            assert k in pl

    def test_playlists_unauthenticated(self, client, oauth):
        oauth.validate_token.return_value = False
        assert json.loads(client.get("/api/playlists").data).get("auth_required") is True


class TestPlayBrowseRoute:
    def test_play_browse_starts_playback(self, client, sp):
        resp = client.post("/api/play-browse",
                           json={"context_uri": "spotify:playlist:pl_001"},
                           content_type="application/json")
        assert resp.status_code == 200
        assert json.loads(resp.data).get("success") is True
        sp.start_playback.assert_called_once_with(context_uri="spotify:playlist:pl_001")

    def test_play_browse_no_crash(self, client):
        assert client.post("/api/play-browse",
                           json={"context_uri": "spotify:album:alb_001"},
                           content_type="application/json").status_code != 500


class TestAlbumsRoute:
    def test_albums_authenticated(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        data = json.loads(client.get("/api/albums").data)
        assert data.get("auth_required") is False
        for k in ("id", "name", "artist", "uri"):
            assert k in data["albums"][0]

    def test_albums_unauthenticated(self, client, oauth):
        oauth.validate_token.return_value = False
        assert json.loads(client.get("/api/albums").data).get("auth_required") is True


class TestLogoutRoute:
    def test_logout_success(self, client):
        resp = client.get("/api/logout")
        assert resp.status_code == 200
        assert json.loads(resp.data).get("success") is True

    def test_logout_no_crash(self, client):
        assert client.get("/api/logout").status_code != 500


class TestAuthStatusRoute:
    def test_auth_status_authenticated(self, client, oauth):
        oauth.validate_token.return_value = True
        assert json.loads(client.get("/api/auth-status").data).get("authenticated") is True

    def test_auth_status_not_authenticated(self, client, oauth):
        oauth.validate_token.return_value = False
        assert json.loads(client.get("/api/auth-status").data).get("authenticated") is False

    def test_auth_status_no_token_leak(self, client, oauth):
        oauth.validate_token.return_value = True
        data = json.loads(client.get("/api/auth-status").data)
        assert "access_token" not in data and "refresh_token" not in data


class TestPlayTrackRoute:
    def test_play_track_success(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        resp = client.post(
            "/api/play-track",
            json={"uri": "spotify:track:abc123"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert json.loads(resp.data).get("success") is True
        sp.start_playback.assert_called_once_with(uris=["spotify:track:abc123"])

    def test_play_track_missing_uri(self, client, oauth):
        oauth.validate_token.return_value = True
        resp = client.post(
            "/api/play-track",
            json={},
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "error" in json.loads(resp.data)

    def test_play_track_unauthenticated(self, client, oauth):
        oauth.validate_token.return_value = False
        resp = client.post(
            "/api/play-track",
            json={"uri": "spotify:track:abc123"},
            content_type="application/json",
        )
        assert resp.status_code == 401
        assert json.loads(resp.data).get("auth_required") is True

    def test_play_track_spotify_error(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        sp.start_playback.side_effect = Exception("No active device")
        resp = client.post(
            "/api/play-track",
            json={"uri": "spotify:track:abc123"},
            content_type="application/json",
        )
        assert resp.status_code == 502
        assert "error" in json.loads(resp.data)


class TestAddToQueueRoute:
    def test_add_to_queue_success(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        resp = client.post(
            "/api/queue",
            json={"uri": "spotify:track:xyz789"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert json.loads(resp.data).get("success") is True
        sp.add_to_queue.assert_called_once_with("spotify:track:xyz789")

    def test_add_to_queue_missing_uri(self, client, oauth):
        oauth.validate_token.return_value = True
        resp = client.post(
            "/api/queue",
            json={},
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_add_to_queue_unauthenticated(self, client, oauth):
        oauth.validate_token.return_value = False
        resp = client.post(
            "/api/queue",
            json={"uri": "spotify:track:xyz789"},
            content_type="application/json",
        )
        assert resp.status_code == 401
        assert json.loads(resp.data).get("auth_required") is True

    def test_add_to_queue_spotify_error(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        sp.add_to_queue.side_effect = Exception("No active device")
        resp = client.post(
            "/api/queue",
            json={"uri": "spotify:track:xyz789"},
            content_type="application/json",
        )
        assert resp.status_code == 502


class TestAddToPlaylistRoute:
    def test_add_to_playlist_success(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        resp = client.post(
            "/api/playlists/pl_001/add",
            json={"uri": "spotify:track:abc"},
            content_type="application/json",
        )
        assert resp.status_code == 200
        assert json.loads(resp.data).get("success") is True
        sp.playlist_add_items.assert_called_once_with("pl_001", ["spotify:track:abc"])

    def test_add_to_playlist_missing_uri(self, client, oauth):
        oauth.validate_token.return_value = True
        resp = client.post(
            "/api/playlists/pl_001/add",
            json={},
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_add_to_playlist_unauthenticated(self, client, oauth):
        oauth.validate_token.return_value = False
        resp = client.post(
            "/api/playlists/pl_001/add",
            json={"uri": "spotify:track:abc"},
            content_type="application/json",
        )
        assert resp.status_code == 401

    def test_add_to_playlist_spotify_error(self, client, oauth, sp):
        oauth.validate_token.return_value = True
        sp.playlist_add_items.side_effect = Exception("Forbidden")
        resp = client.post(
            "/api/playlists/pl_001/add",
            json={"uri": "spotify:track:abc"},
            content_type="application/json",
        )
        assert resp.status_code == 502

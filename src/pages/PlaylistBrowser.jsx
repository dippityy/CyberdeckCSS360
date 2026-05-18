import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import backButton from "../assets/back.png";

function PlaylistBrowser() {
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/api/playlists", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        setPlaylists(data.playlists || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const playPlaylist = async (playlistId) => {
    try {
      await fetch("/api/play-playlist", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          context_uri: `spotify:playlist:${playlistId}`,
        }),
      });
    } catch (err) {
      console.error("Error playing playlist: ", err);
    }
  };

  return (
    <div className="playlist-browser">
      <div className="navigate-browse">
        <button className="btn-back" onClick={() => navigate("/")}>
          <img src={backButton} alt="Back to Playback" />
        </button>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {!loading && (
        <div className="playlists-grid">
          {playlists.map((playlist) => (
            <div key={playlist.id} className="playlist-card">
              {playlist.cover_url && (
                <button onClick={() => playPlaylist(playlist.id)}>
                  <img
                    src={playlist.cover_url}
                    alt={playlist.name}
                    className="playlist-cover"
                  />
                </button>
              )}
              <h3 onClick={() => playPlaylist(playlist.id)}>{playlist.name}</h3>
              <p>By: {playlist.owner}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PlaylistBrowser;

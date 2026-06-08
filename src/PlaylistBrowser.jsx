import { useState, useEffect } from "react";
import "./PlaylistsAlbums.css";
import PlaylistTracks from "./PlaylistTracks";

function PlaylistBrowser() {
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null); // { id, name }

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

  const playPlaylist = async (e, playlistId) => {
    // Stop click from also opening the drilldown
    e.stopPropagation();
    try {
      await fetch("/api/play-browse", {
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

  // ── Drilldown view ────────────────────────────────────────
  if (selected) {
    return (
      <PlaylistTracks
        playlistId={selected.id}
        playlistName={selected.name}
        onBack={() => setSelected(null)}
      />
    );
  }

  // ── Grid view ─────────────────────────────────────────────
  return (
    <div className="browser">
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {!loading && (
        <div className="browser-grid">
          {playlists.map((playlist) => (
            <div
              key={playlist.id}
              className="browse-card"
              onClick={() => setSelected({ id: playlist.id, name: playlist.name })}
              style={{ cursor: "pointer" }}
              title={`Browse "${playlist.name}"`}
            >
              {playlist.cover_url && (
                <button
                  onClick={(e) => playPlaylist(e, playlist.id)}
                  title="Play now"
                >
                  <img
                    src={playlist.cover_url}
                    alt={playlist.name}
                    className="browse-cover"
                  />
                </button>
              )}
              <h3>{playlist.name}</h3>
              <p>By: {playlist.owner}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PlaylistBrowser;

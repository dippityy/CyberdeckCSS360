import { useState, useEffect } from "react";
import "./PlaylistsAlbums.css";
import AlbumTracks from "./AlbumTracks";

function AlbumBrowser() {
  const [albums, setAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null); // { id }

  useEffect(() => {
    fetch("/api/albums", { credentials: "include" })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setAlbums(data.albums || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const playAlbum = async (e, albumUri) => {
    e.stopPropagation();
    try {
      await fetch("/api/play-browse", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context_uri: albumUri }),
      });
    } catch (err) {
      console.error("Error playing album:", err);
    }
  };

  // ── Drilldown view ─────────────────────────────────────────
  if (selected) {
    return (
      <AlbumTracks
        albumId={selected.id}
        onBack={() => setSelected(null)}
      />
    );
  }

  // ── Grid view ──────────────────────────────────────────────
  return (
    <div className="browser">
      {loading && <p>Loading…</p>}
      {error && <p>Error: {error}</p>}
      {!loading && !error && (
        <div className="browser-grid">
          {albums.map((album) => (
            <div
              key={album.id}
              className="browse-card"
              onClick={() => setSelected({ id: album.id })}
              style={{ cursor: "pointer" }}
              title={`Browse "${album.name}"`}
            >
              {album.cover_url && (
                <button onClick={(e) => playAlbum(e, album.uri)} title="Play now">
                  <img
                    src={album.cover_url}
                    alt={album.name}
                    className="browse-cover"
                  />
                </button>
              )}
              <h3>{album.name}</h3>
              <p>{album.artist}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AlbumBrowser;

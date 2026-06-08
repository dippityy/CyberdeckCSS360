import { useState, useEffect } from "react";
import "./TrackBrowser.css";

const fmt = (ms) => {
  const s = Math.max(0, Math.floor(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
};

function AlbumTracks({ albumId, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState(null); // { index, type: "play"|"queue" }

  useEffect(() => {
    setLoading(true);
    fetch(`/api/albums/${albumId}/tracks`, { credentials: "include" })
      .then((res) => res.json())
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [albumId]);

  const playTrack = async (uri, index) => {
    try {
      await fetch("/api/play-track", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uri }),
      });
      setFeedback({ index, type: "play" });
      setTimeout(() => setFeedback(null), 1500);
    } catch (err) {
      console.error("Error playing track:", err);
    }
  };

  const queueTrack = async (uri, index) => {
    try {
      await fetch("/api/queue", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uri }),
      });
      setFeedback({ index, type: "queue" });
      setTimeout(() => setFeedback(null), 1500);
    } catch (err) {
      console.error("Error queuing track:", err);
    }
  };

  const playAlbum = async () => {
    if (!data?.album?.uri) return;
    try {
      await fetch("/api/play-browse", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context_uri: data.album.uri }),
      });
    } catch (err) {
      console.error("Error playing album:", err);
    }
  };

  return (
    <div className="tb-root">
      <button className="tb-back" onClick={onBack} aria-label="Back to albums">
        <span className="tb-back-arrow">←</span>
        <span>Return</span>
      </button>

      {data?.album && (
        <div className="tb-hero">
          {data.album.cover_url && (
            <img
              className="tb-hero-cover"
              src={data.album.cover_url}
              alt={data.album.name}
            />
          )}
          <div className="tb-hero-info">
            <h1 className="tb-hero-name">{data.album.name}</h1>
            <p className="tb-hero-artist">{data.album.artist}</p>
            <p className="tb-hero-meta">
              {data.album.release_date
                ? data.album.release_date.slice(0, 4)
                : ""}
              {data.album.release_date && data.album.total_tracks ? " · " : ""}
              {data.album.total_tracks
                ? `${data.album.total_tracks} tracks`
                : ""}
              {data.album.label ? ` · ${data.album.label}` : ""}
            </p>
            <button className="tb-play-all" onClick={playAlbum}>
              ▶ Play Album
            </button>
          </div>
        </div>
      )}

      {loading && (
        <div className="tb-loading">
          <div className="tb-spinner" />
          <span>Loading tracks…</span>
        </div>
      )}
      {error && <p className="tb-error">Error: {error}</p>}

      {!loading && data?.tracks && (
        <ul className="tb-tracklist">
          {data.tracks.map((track, i) => {
            const isFeedback = feedback?.index === i;
            return (
              <li
                key={`${track.id}-${i}`}
                className={`tb-track${isFeedback ? " tb-track--feedback" : ""}`}
              >
                <span className="tb-track-num">{track.track_number ?? i + 1}</span>

                <div className="tb-track-info">
                  <span className="tb-track-name">{track.name}</span>
                  {track.artist !== data.album.artist && (
                    <span className="tb-track-artist">{track.artist}</span>
                  )}
                </div>

                <span className="tb-track-duration">{fmt(track.duration_ms)}</span>

                <div className="tb-track-actions">
                  {isFeedback ? (
                    <span className="tb-track-feedback">
                      {feedback.type === "play" ? "▶ Playing" : "+ Queued"}
                    </span>
                  ) : (
                    <>
                      <button
                        className="tb-btn"
                        onClick={() => playTrack(track.uri, i)}
                        title="Play now"
                      >
                        ▶
                      </button>
                      <button
                        className="tb-btn"
                        onClick={() => queueTrack(track.uri, i)}
                        title="Add to queue"
                      >
                        +
                        </button>
                      </>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
    </div>
  );
}

export default AlbumTracks;

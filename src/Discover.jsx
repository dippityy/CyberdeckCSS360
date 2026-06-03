import { useEffect, useState } from "react";
import TrackCard from "./TrackCard";
import "./Discover.css";

function Discover() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const [pickerOpen, setPickerOpen] = useState(false);
  const [pickerTrackUri, setPickerTrackUri] = useState(null);
  const [playlists, setPlaylists] = useState(null);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetch("/api/discover", { credentials: "include" })
      .then((res) => res.json())
      .then((d) => {
        if (!cancelled) {
          setData(d);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [retryCount]);

  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(id);
  }, [toast]);

  useEffect(() => {
    if (!pickerOpen) return;
    const onKey = (e) => {
      if (e.key === "Escape") setPickerOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [pickerOpen]);

  const showToast = (text, type = "success") => setToast({ text, type });

  const playNow = async (uri) => {
    try {
      const res = await fetch("/api/play-track", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uri }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        showToast(body.error || "Couldn't play track", "error");
        return;
      }
      showToast("Playing");
    } catch {
      showToast("Network error, try again", "error");
    }
  };

  const addQueue = async (uri) => {
    try {
      const res = await fetch("/api/queue", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uri }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        showToast(body.error || "Couldn't add to queue", "error");
        return;
      }
      showToast("Added to queue");
    } catch {
      showToast("Network error, try again", "error");
    }
  };

  const openPicker = async (uri) => {
    setPickerTrackUri(uri);
    setPickerOpen(true);
    if (playlists) return;
    try {
      const res = await fetch("/api/playlists", { credentials: "include" });
      const body = await res.json();
      setPlaylists(body.playlists || []);
    } catch {
      showToast("Couldn't load playlists", "error");
    }
  };

  const addToPlaylist = async (playlistId, playlistName) => {
    try {
      const res = await fetch(`/api/playlists/${playlistId}/add`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uri: pickerTrackUri }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        showToast(body.error || "Couldn't add to playlist", "error");
        return;
      }
      setPickerOpen(false);
      showToast(`Added to ${playlistName}`);
    } catch {
      showToast("Network error, try again", "error");
    }
  };

  if (loading && !data) {
    return (
      <div className="discover">
        <div className="discover-state">Loading…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="discover">
        <div className="discover-state">
          <p>Couldn’t load suggestions.</p>
          <button onClick={() => setRetryCount((c) => c + 1)}>Try again</button>
        </div>
      </div>
    );
  }

  if (data?.auth_required) {
    return (
      <div className="discover">
        <div className="discover-state">
          <a href={data.auth_url}>Sign in with Spotify</a>
        </div>
      </div>
    );
  }

  const allEmpty = !data?.suggestions?.length;

  if (allEmpty) {
    return (
      <div className="discover">
        <div className="discover-state">
          Couldn’t load suggestions yet, play some music on Spotify first.
        </div>
      </div>
    );
  }

  const sections = [
    {
      key: "suggestions",
      title: "Suggested for You",
      items: data.suggestions,
      renderItem: (t) => (
        <div key={t.id} className="discover-row">
          <TrackCard
            cover_url={t.cover_url}
            name={t.name}
            subtitle={t.artist}
          />
          <div className="track-actions">
            <button
              className="track-action"
              title="Play now"
              onClick={() => playNow(t.uri)}
            >
              ▶
            </button>
            <button
              className="track-action"
              title="Add to queue"
              onClick={() => addQueue(t.uri)}
            >
              +
            </button>
            <button
              className="track-action"
              title="Add to playlist"
              onClick={() => openPicker(t.uri)}
            >
              ☰
            </button>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="discover">
      <h1 className="discover-title">Discover</h1>
      {sections.map((section) =>
        section.items?.length ? (
          <section key={section.key} className="discover-section">
            <h2 className="discover-section-title">{section.title}</h2>
            <div className="discover-section-items">
              {section.items.map(section.renderItem)}
            </div>
          </section>
        ) : null
      )}
      {pickerOpen && (
        <div
          className="picker-backdrop"
          onClick={() => setPickerOpen(false)}
        >
          <div
            className="picker-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="picker-header">
              <h2>Add to playlist</h2>
              <button
                className="picker-close"
                onClick={() => setPickerOpen(false)}
                aria-label="Close"
              >
                ×
              </button>
            </div>
            <div className="picker-list">
              {!playlists && <div className="picker-empty">Loading…</div>}
              {playlists && playlists.length === 0 && (
                <div className="picker-empty">No playlists found.</div>
              )}
              {playlists &&
                playlists.map((p) => (
                  <button
                    key={p.id}
                    className="picker-item"
                    onClick={() => addToPlaylist(p.id, p.name)}
                  >
                    {p.cover_url ? (
                      <img src={p.cover_url} alt="" className="picker-cover" />
                    ) : (
                      <div className="picker-cover picker-cover-placeholder" />
                    )}
                    <div className="picker-item-text">
                      <div className="picker-item-name">{p.name}</div>
                      <div className="picker-item-owner">{p.owner}</div>
                    </div>
                  </button>
                ))}
            </div>
          </div>
        </div>
      )}

      {toast && (
        <div className={`toast toast-${toast.type}`} role="status">
          {toast.text}
        </div>
      )}
    </div>
  );
}

export default Discover;

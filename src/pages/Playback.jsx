import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import previousButton from "../assets/previous.png";
import playButton from "../assets/play.png";
import pauseButton from "../assets/pause.png";
import nextButton from "../assets/next.png";
import browseButton from "../assets/browse.png";

const fmt = (ms) => {
  const s = Math.max(0, Math.floor(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
};

function Playback() {
  const navigate = useNavigate();
  const [currentPlayback, setPlayback] = useState(null);

  useEffect(() => {
    const fetchPlayback = () => {
      fetch("/api/playback", { credentials: "include" })
        .then((res) => res.json())
        .then((data) => setPlayback(data))
        .catch((error) =>
          console.error("Error fetching playback data:", error),
        );
    };

    fetchPlayback();
    const interval = setInterval(fetchPlayback, 1000);
    return () => clearInterval(interval);
  }, []);

  if (currentPlayback?.auth_required) {
    return (
      <div className="now-playing">
        <div className="login">
          <a href={currentPlayback.auth_url}>Sign in with Spotify</a>
        </div>
      </div>
    );
  }

  if (!currentPlayback?.track_name) {
    return (
      <div className="now-playing">
        <div className="idle">
          <h1 className="title">{currentPlayback?.message}</h1>
        </div>
      </div>
    );
  }

  const pct = Math.min(
    100,
    (currentPlayback.progress_ms / Math.max(1, currentPlayback.duration_ms)) *
      100,
  );

  const togglePlayback = async () => {
    await fetch("/api/playpause", {
      credentials: "include",
      method: "POST",
    });
  };

  const skipNext = async () => {
    await fetch("/api/next", {
      credentials: "include",
      method: "POST",
    });
  };

  const skipPrevious = async () => {
    await fetch("/api/previous", {
      credentials: "include",
      method: "POST",
    });
  };

  return (
    <div className="now-playing">
      <div className="device">
        <div className="cover">
          <img src={currentPlayback.cover_URL} alt="album cover" />
        </div>

        <div className="meta">
          <h1 className="title">{currentPlayback.track_name}</h1>
          <div className="artist">{currentPlayback.artist_name}</div>
        </div>

        <div className="progress">
          <div className="bar">
            <div className="fill" style={{ width: `${pct}%` }} />
          </div>
          <div className="times">
            <span className="left">{fmt(currentPlayback.progress_ms)}</span>
            <span className="status">
              {currentPlayback.is_playing ? "PLAYING" : "PAUSED"}
            </span>
            <span className="right">{fmt(currentPlayback.duration_ms)}</span>
          </div>
        </div>

        <div className="controls">
          <div id="playback-controls">
            <button className="btn-skip" onClick={skipPrevious}>
              <img src={previousButton} alt="Previous" />
            </button>

            <button className="btn-play" onClick={togglePlayback}>
              <img
                src={currentPlayback.is_playing ? pauseButton : playButton}
                alt={currentPlayback.is_playing ? "pause" : "play"}
              />
            </button>

            <button className="btn-skip" onClick={skipNext}>
              <img src={nextButton} alt="Next" />
            </button>
          </div>
        </div>

        <div id="browse">
          <button onClick={() => navigate("/browse")}>
            <img src={browseButton} alt="Browse" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default Playback;

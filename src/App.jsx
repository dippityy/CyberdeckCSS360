import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [currentPlayback, setPlayback] = useState(null);

  useEffect(() => {
    const fetchPlayback = () => {
      console.log("Fetching playback...");
      fetch("/api/playback", {
        credentials: "include",
      })
        .then((res) => {
          console.log("Response status:", res.status);
          return res.json();
        })
        .then((data) => {
          console.log("Received data:", data);
          setPlayback(data);
        })
        .catch((error) => {
          console.error("Error fetching playback data:", error);
        });
    };

    fetchPlayback();

    const interval = setInterval(fetchPlayback, 1000);

    return () => clearInterval(interval);
  }, []);

  console.log("Rendering App, currentPlayback:", currentPlayback);

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
    <>
      {currentPlayback?.auth_required && (
        <a href={currentPlayback.auth_url}>Login with Spotify</a>
      )}

      {currentPlayback && !currentPlayback.auth_required && (
        <div>
          {currentPlayback.message ? (
            <p>{currentPlayback.message}</p>
          ) : (
            <>
              <img
                src={currentPlayback.cover_URL}
                className="cover"
                alt="album cover"
              />
              <p>{currentPlayback.track_name}</p>
              <p>Artist: {currentPlayback.artist_name}</p>
              <p>
                Progress: {Math.floor(currentPlayback.progress_ms / 60000)}:
                {String(
                  Math.floor((currentPlayback.progress_ms % 60000) / 1000),
                ).padStart(2, "0")}
              </p>
              <p>Status: {currentPlayback.is_playing ? "Playing" : "Paused"}</p>
              <div id="playback-controls">
                <button onClick={skipPrevious}>
                  <img
                    src={previousButton}
                    height="27"
                    width="27"
                    alt="Previous"
                  />
                </button>

                <button onClick={togglePlayback}>
                  <img
                    src={currentPlayback.is_playing ? pauseButton : playButton}
                    height="62.5"
                    width="62.5"
                    alt={currentPlayback.is_playing ? "pause" : "play"}
                  />
                </button>

                <button onClick={skipNext}>
                  <img src={nextButton} height="27" width="27" alt="Next" />
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
}

export default App;

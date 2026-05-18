import { Routes, Route } from "react-router-dom";
import Playback from "./pages/Playback";
import PlaylistBrowser from "./pages/PlaylistBrowser";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Playback />} />
      <Route path="/browse" element={<PlaylistBrowser />} />
    </Routes>
  );
}

export default App;

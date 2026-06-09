## Running on Raspberry Pi

### First Time Setup

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/CyberdeckCSS360.git
cd CyberdeckCSS360
```

**2. Install system dependencies**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nodejs npm
```

**3. Set up Python**
```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
```

**4. Add your Spotify credentials**
```bash
nano api/.env
FLASK_APP=api.py
FLASK_ENV=development
SPOTIPY_CLIENT_ID= your_client_id
SPOTIPY_CLIENT_SECRET= your_secret
SPOTIPY_REDIRECT_URI=http://localhost:5000/callback
```

**5. Build the frontend**
```bash
npm install
npm run build
```

**6. Make start script executable**
```bash
chmod +x start.sh
```

**7. Set up Flask to run on boot**
```bash
sudo cp myapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
```

**8. Set up Chromium to open on boot**
```bash
mkdir -p /home/pi/.config/autostart
cp cyberdeck.desktop /home/pi/.config/autostart/
```

**9. Reboot**
```bash
sudo reboot
```

The app will launch automatically on every boot.

**Running on Desktop**

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/CyberdeckCSS360.git
cd CyberdeckCSS360
```
**2. Build the frontend**
```bash
npm install
npm run build
```

**3. Add your Spotify credentials**
```bash
nano api/.env
FLASK_APP=api.py
FLASK_ENV=development
SPOTIPY_CLIENT_ID= your_client_id
SPOTIPY_CLIENT_SECRET= your_secret
SPOTIPY_REDIRECT_URI=http://localhost:5000/callback
```

**4. Set up Python**
```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 api.py
```

Open http://127.0.0.1:5000 in browser


### Spotify Setup
Make sure `http://127.0.0.1:5000/callback` is added as a redirect URI in your 
[Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

On first boot you'll be prompted to log in to Spotify — this only happens once.
The token is cached and reused on every subsequent boot.

### Clearing Spotify cache for new user
'''bash
rm /home/pi/CyberdeckCSS360/.spotify_cache
sudo systemctl restart myapp
'''

### Updating
When pushing new code
```bash
cd CyberdeckCSS360
git pull
npm run build
sudo systemctl restart myapp
```

### Useful Commands
```bash
sudo systemctl status myapp     # check if Flask is running
sudo systemctl restart myapp    # restart after changes
journalctl -u myapp -f          # live logs
```

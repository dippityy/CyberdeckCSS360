# CyberdeckCSS360

Have to add .env file in api folder containing:
FLASK_APP=api.py
FLASK_ENV=development
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:5000/callback
REACT_URL=http://localhost:5173

1. git clone https://github.com/dippityy/CyberdeckCSS360
2. cd CyberdeckCSS360
3. cd api
4. python -m venv venv
5. source venv/bin/activate
6. pip install -r requirements
7. python api.py
8. open new terminal
9. cd CyberdeckCSS360
10. npm install
11. npm run dev

o + enter to open localhost

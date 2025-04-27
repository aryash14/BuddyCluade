import requests
import urllib.parse
import webbrowser
import threading
import time
import json
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# ==== YOUR CREDENTIALS ====
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

# ==== GOOGLE ENDPOINTS ====
AUTH_URL = os.environ.get("AUTH_URL")
TOKEN_URL = os.environ.get("TOKEN_URL")

# ==== SCOPES ====
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

# ==== GLOBAL TOKEN STORAGE ====
access_token = None
refresh_token = None
token_expiry_time = None
auth_complete = threading.Event()

# ==== TOKEN FILE PATH ====
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'google_tokens.json')

# ==== FLASK APP ====
app = Flask(__name__)

# ==== FUNCTIONS ====

def save_tokens_to_file():
    global access_token, refresh_token, token_expiry_time
    if not all([access_token, token_expiry_time]):
        return False
    token_data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_expiry_time': token_expiry_time
    }
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f)
        return True
    except Exception as e:
        print(f"Error saving tokens: {e}")
        return False

def load_tokens_from_file():
    global access_token, refresh_token, token_expiry_time
    if not os.path.exists(TOKEN_FILE):
        return False
    try:
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        token_expiry_time = token_data.get('token_expiry_time')
        return access_token is not None
    except Exception as e:
        print(f"Error loading tokens: {e}")
        return False

def generate_auth_url():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

def refresh_access_token():
    global access_token, token_expiry_time
    if not refresh_token:
        raise Exception("No refresh token available.")
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    tokens = response.json()
    access_token = tokens['access_token']
    expires_in = tokens.get('expires_in', 3600)
    token_expiry_time = time.time() + expires_in - 60
    save_tokens_to_file()
    print("Access token refreshed successfully.")

def get_valid_access_token():
    global access_token, token_expiry_time
    if access_token is None and load_tokens_from_file():
        print("Loaded tokens from file.")
    if access_token is None or (token_expiry_time and time.time() > token_expiry_time):
        print("Access token expired or missing. Refreshing...")
        refresh_access_token()
    return access_token

# ==== FLASK ROUTES ====

@app.route('/callback')
def callback():
    global access_token, refresh_token, token_expiry_time
    auth_code = request.args.get('code')
    if not auth_code:
        return "No code provided", 400
    data = {
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    tokens = response.json()
    access_token = tokens['access_token']
    refresh_token = tokens.get('refresh_token')
    expires_in = tokens.get('expires_in', 3600)
    token_expiry_time = time.time() + expires_in - 60
    save_tokens_to_file()
    auth_complete.set()

    # Pretty closing page with immediate close
    return """
    <html>
    <head>
        <title>Authentication Successful</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding-top: 50px; }
            .success { color: green; font-size: 24px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="success">Authentication successful!</div>
        <p>Closing window...</p>
        <script>
            // Close the window immediately
            window.close();
            // Fallback if window.close() is blocked by the browser
            setTimeout(function() {
                document.body.innerHTML += '<p>If this window did not close automatically, you can close it now.</p>';
            }, 1000);
        </script>
    </body>
    </html>
    """

@app.route('/token')
def token():
    try:
        token = get_valid_access_token()
        return jsonify({'access_token': token})
    except Exception as e:
        print(f"Error providing token: {e}")
        return jsonify({'error': 'Unable to get token'}), 500

def start_flask_app():
    app.run(port=5100, debug=False)

# ==== MAIN PROGRAM ====

def main():
    if load_tokens_from_file() and token_expiry_time and time.time() < token_expiry_time:
        print("Using existing valid tokens.")
    else:
        print("Need to authenticate. Starting local server at http://localhost:5000/")
        auth_complete.clear()
        server_thread = threading.Thread(target=start_flask_app, daemon=True)
        server_thread.start()
        time.sleep(1)
        auth_url = generate_auth_url()
        print(f"Opening browser to authenticate...")
        webbrowser.open(auth_url, new=1)
        print("Waiting for login to complete...")
        auth_successful = auth_complete.wait(timeout=300)
        if not auth_successful:
            print("Authentication timed out after 5 minutes.")
            return
        print("Authentication completed successfully.")

    # Keep server running for Claude MCP
    print("MCP server running, ready to provide tokens to Claude...")
    app.run(port=5100, debug=False)

if __name__ == '__main__':
    main()
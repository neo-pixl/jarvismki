from flask import Flask, request, send_file, render_template
import requests
import os
import subprocess

app = Flask(__name__)

API_KEY = os.getenv("ELEVENLABS_API_KEY")
CHUNK_SIZE = 1024
AUDIO_FILE = "output.mp3"

def get_audio_from_text(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/usgDTGR8FQgLwaxY5KN6"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 1,
            "similarity_boost": 0.69
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        with open(AUDIO_FILE, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        return AUDIO_FILE
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text')
    if not text:
        return {"error": "No text provided"}, 400
    print(f"Received text: {text}")
    audio_file = get_audio_from_text(text)
    if audio_file:
        print("Sending audio file to client.")
        return send_file(audio_file, mimetype='audio/mpeg')
    else:
        print("Failed to generate audio.")
        return {"error": "Failed to generate audio"}, 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

import requests
import os
import pygame
from api_keys import elevenlabs_api

pygame.mixer.init()

def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait for the music to finish playing
        pygame.time.Clock().tick(10)

def get_audio_from_text(text):
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/usgDTGR8FQgLwaxY5KN6"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_api
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 1,
            "similarity_boost": 0.69
        }
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open('output.mp3', 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
    else:
        print(f"Error: {response.status_code}, {response.text}")

def speak(text):
    get_audio_from_text(text)
    play_sound('output.mp3')
    pygame.mixer.music.unload()
    os.remove("output.mp3")

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette, QFontDatabase, QFont
import requests
from groq import Groq
from PIL import ImageGrab, Image
import cv2
import pyperclip
import google.generativeai as genai
import os
from pyHS100 import SmartBulb, SmartPlug
import mss
import datetime
import pyautogui
from keyboard import volumeup, volumedown
import subprocess
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from termcolor import colored
from elevenlabs import play_sound
from faster_whisper import WhisperModel
import re
from pydub import AudioSegment
from pydub.silence import split_on_silence
from elevenlabs import speak
from api_keys import SERPAPI_API_KEY, groq_api, genai_api, weather_api

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

groq_client = Groq(api_key=groq_api)

sys_msg = (
    'You are a multi-modal AI voice assistant named Jarvis. '
    'Generate the most useful and '
    'factual response possible, carefully considering all previous generated text in your response before '
    'adding new tokens to the response. Do not expect or request images, just use the context if added. '
    'Use all of the context of this conversation so your response is relevant to the conversation. Make '
    'your responses clear and concise, avoiding any verbosity. '
    'Emulate Jarvis from the Ironman films, blending intelligence, efficiency, and a touch of wit. '
    'Keep responses to no more than thirty words. You are already well-acquainted with the user. '
    'Don\'t ask questions right away when it comes to small talk. Also don\'t complex words talk normal but also sound a little like Jarvis.'
)

convo = [{'role': 'system', 'content': sys_msg}]

def groq_prompt(prompt):
    prompt = f'USER CONTENT: {prompt}'
    convo.append({'role': 'user', 'content': prompt})
    chat_completion = groq_client.chat.completions.create(messages=convo, model='llama3-70b-8192')
    response = chat_completion.choices[0].message
    convo.append(response)

    return response.content

def function_call(prompt):
    sys_msg = (
        'You are an AI function calling model. You will determine whether '
        'performing an internet search, '
        'checking the time, checking the date, pausing media, playing media, '
        'escaping mode, entering fullscreen, checking the temperature, increasing volume, decreasing volume, opening youtube, opening netflix, '
        'entering chat mode, or calling no functions is best for a voice assistant '
        'to respond to the users prompt. The webcam can be assumed to be a normal laptop webcam facing the user. '
        'You will respond with only one selection from this list: '
        '["internet search", "check time", '
        '"pause media", "play media", "escape mode", "enter fullscreen", "increase volume", "decrease volume", '
        '"open netflix", "open youtube", "check date", "check temperature", "Chat mode","None"]. '
        'Do not respond with anything but the most logical selection from that list with no explanations. Side note, only enter chat mode when it\'s specifically asked for.'
        'When providing information not related to any other commands, always perform an internet search to get the most accurate answers.'
    )


    function_convo = [{'role': 'system', 'content': sys_msg},
                      {'role': 'user', 'content': prompt}]
    
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    response = chat_completion.choices[0].message

    return response.content

def take_screenshot():
    path = (r'C:\\Users\\Moham\\OneDrive\\Desktop\\MK V\\screenshot.jpg')
    with mss.mss() as sct:
            # The screen part to capture
            monitor_number = 1  # Indexing starts at 1
            monitor = sct.monitors[monitor_number]  # Use the second monitor

            sct_img = sct.shot(mon=monitor_number, output=path)

def internet_search(query):
    url = f'https://serpapi.com/search.json?q={query}&api_key={SERPAPI_API_KEY}'
    response = requests.get(url)
    results = response.json()
    search_results = []
    if 'organic_results' in results:
        for item in results['organic_results']:
            search_results.append(f"{item['title']}: {item['link']}")
    return "\n".join(search_results)

def check_time(action):
    if action == "check time":
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"It's {current_time}"
    
def check_date(action):
    if action == "check date":
        current_date = datetime.datetime.now().strftime("%A, %B %dth")
        return f"Today is {current_date}"
    
def check_weather(action):
    if action == "check temperature":
        city = "(city)"
        country = "(country)"
        weather_api_key = weather_api
        weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city},{country}&units=imperial&appid={weather_api_key}'
        weather_response = requests.get(weather_url)
        
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            if 'main' in weather_data:
                temperature = round(weather_data['main']['temp'])
            else:
                temperature = "unavailable"
                return "Error: 'main' key not found in the weather response. Response data:", weather_data
        else:
            temperature = "unavailable"
            return f"Error: Failed to retrieve weather data. HTTP Status code: {weather_response.status_code}"
        return f"The temperature in {city} is {temperature} degrees."

def pause_media(action):
    if action == "pause media":
        pyautogui.press("space")
        return None

def play_media(action):
    if action == "play media":
        pyautogui.press("space")
        return None

def escape_mode(action):
    if action == "escape mode":
        pyautogui.press("esc")
        return None

def enter_fullscreen(action):
    if action == "enter fullscreen":
        pyautogui.press("f")
        return None

def increase_volume(action):
    if action == "increase volume":
        volumeup()
        return None

def decrease_volume(action):
    if action == "decrease volume":
        volumedown()
        return None

def website(url):
    webbrowser.get().open(url)

def open_youtube(action):
    if action == "open youtube":
        website('https://www.youtube.com/')
        return None

def open_netflix(action):
    if action == "open netflix":
        website('https://www.netflix.com/browse')
        return None

class ChatUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chat Mode")
        
        self.setGeometry(100, 100, 500, 600)

        # Load custom font
        self.font_id = QFontDatabase.addApplicationFont("exo-semibold.ttf")
        self.font_family = QFontDatabase.applicationFontFamilies(self.font_id)[0]

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout(self.central_widget)

        # Chat display
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #2b2b2b; color: #ffffff; font-size: 17px; padding: 10px; border: none;")
        self.layout.addWidget(self.chat_display)

        # Input field
        self.input_field = QLineEdit(self)
        self.input_field.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-size: 16px; padding: 10px; border: none;")
        self.input_field.returnPressed.connect(self.send_message)  # Connect Enter key to send_message
        self.layout.addWidget(self.input_field)

        # Apply a dark theme to the entire app
        self.apply_dark_theme()

    def send_message(self):
        message = self.input_field.text()
        if message:
            self.chat_display.append(f"<b style='color: #e5e5e5; font-family: {self.font_family}; font-size: 18px;'>USER:</b> {message}")
            self.input_field.clear()

            # Process the response from the assistant
            response = self.handle_prompt(message)
            assistant_text = f"<b style='color: #0096FF; font-family: {self.font_family}; font-size: 18px;'>NOVA:</b> {response}"
            self.chat_display.append(assistant_text)

    def handle_prompt(self, clean_prompt):
        call = function_call(clean_prompt)

        action_response = None
        final_response = None
        
        if call == "internet search":
            search_results = internet_search(clean_prompt)
            clean_prompt = f'{clean_prompt}\n\n INTERNET SEARCH RESULTS: {search_results}'
            

        elif call == "check time":
            action_response = check_time(call)
            if action_response is None:
                action_response = "An unexpected error occurred while controlling the strips."
            
            

        elif call == "check date":
            action_response = check_date(call)
            if action_response is None:
                action_response = "An unexpected error occurred while controlling the strips."
            
            
        elif call == "check temperature":
            action_response = check_weather(call)
            if action_response is None:
                action_response = "An unexpected error occurred while controlling the strips."
            
            

        elif call == "increase volume":
            action_response = increase_volume(call)
            

        elif call == "decrease volume":
            action_response = decrease_volume(call)
            

        elif call == "pause media":
            action_response = pause_media(call)
        

        elif call == "play media":
            action_response = play_media(call)
            

        elif call == "escape mode":
            action_response = escape_mode(call)
            

        elif call == "enter fullscreen":
            action_response = enter_fullscreen(call)
            

        elif call == "open youtube":
            action_response = open_youtube(call)
        

        elif call == "open netflix":
            action_response = open_netflix(call)

            
        if action_response:
                final_response = action_response
        else:
            response_content = groq_prompt(prompt=clean_prompt)    
            final_response = response_content    
        
        speak(final_response)
        return final_response
        

    def apply_dark_theme(self):
        dark_palette = QPalette()

        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(15, 15, 15))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        self.setPalette(dark_palette)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QTextEdit {
                border: 1px solid #444444;
                border-radius: 5px;
            }
            QLineEdit {
                border: 1px solid #444444;
                border-radius: 5px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chat_ui = ChatUI()
    chat_ui.show()
    sys.exit(app.exec_())

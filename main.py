import requests
from elevenlabs import speak
from groq import Groq
from PIL import ImageGrab, Image
import cv2
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
import speech_recognition as sr
import time
import re
from pydub import AudioSegment
from pydub.silence import split_on_silence
import logging
import pyaudio
from vosk import Model, KaldiRecognizer
from api_keys import SERPAPI_API_KEY, groq_api, genai_api, weather_api

logging.basicConfig(level=logging.INFO)
model_path = "DataBase\\vosk-model-en-us-0.42-gigaspeech"
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)


os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

log = logging.info

log(colored("""    
             $$$      $$$      $$$$$$$$   $$$       $$$ $$$    $$$$$$         
             $$$     $$$$$     $$$$$$$$$$  $$$     $$$$ $$$  $$$$  $$$$       
             $$$     $$ $$     $$$     $$$ $$$$    $$$  $$$  $$$     $$$      
             $$$    $$$ $$$    $$$    $$$$  $$$   $$$   $$$  $$$$$B           
             $$$   $$$   $$$   $$$$$$$$$     $$$  $$$   $$$     $$$$$$        
             $$$  $$$$$$$$$$$  $$$  $$$$     $$$  $$    $$$         $$$$      
      $$$    $$$ $$$$$$$$$$$$  $$$   $$$$     $$$$$$    $$$ $$$$    z$$$      
       $$$$$$$$  $$$       $$$ $$$    $$$$     $$$$     $$$  1$$$$$$$$$                                          
""", 'cyan'))

play_sound('sound effects\\startup.mp3')
edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
url = 'http://localhost:5000/'
subprocess.Popen([edge_path, '--app=' + url])
log("Initialization complete.")

wake_word = 'jarvis'
groq_client = Groq(api_key=groq_api)
genai.configure(api_key=genai_api)

sys_msg = (
    'You are a multi-modal AI voice assistant named Jarvis. Your user may or may not have attached a photo for context '
    '(either a screenshot or a webcam capture). Any photo has already been processed into a highly detailed '
    'text prompt that will be attached to their transcribed voice prompt. Generate the most useful and '
    'factual response possible, carefully considering all previous generated text in your response before '
    'adding new tokens to the response. Do not expect or request images, just use the context if added. '
    'Use all of the context of this conversation so your response is relevant to the conversation. Make '
    'your responses clear and concise, avoiding any verbosity. '
    'Emulate Jarvis from the Ironman films, blending intelligence, efficiency, and a touch of wit. '
    'Keep responses to no more than thirty words. You are already well-acquainted with the user. '
    'Don\'t ask questions right away when it comes to small talk. Also don\'t complex words talk normal but also sound a little like Jarvis.'
)

convo = [{'role': 'system', 'content': sys_msg}]

generation_config = {
    'temperature': 0.7,
    'top_p': 1,
    'top_k': 1,
    'max_output_tokens': 100
}

model = genai.GenerativeModel('gemini-1.5-flash-latest', generation_config=generation_config)

r = sr.Recognizer()
source = sr.Microphone()

def groq_prompt(prompt, img_context):
    if img_context:
        prompt = f'USER CONTENT: {prompt}\n\n   IMAGE CONTEXT: {img_context}'
    convo.append({'role': 'user', 'content': prompt})
    chat_completion = groq_client.chat.completions.create(messages=convo, model='llama3-70b-8192')
    response = chat_completion.choices[0].message
    convo.append(response)

    return response.content

def function_call(prompt):
    sys_msg = (
        'You are an AI function calling model. You will determine whether '
        'taking a screenshot, performing an internet search, '
        'checking the time, checking the date, creating a list, showing a list, pausing media, playing media, '
        'escaping mode, entering fullscreen, checking the temperature, increasing volume, decreasing volume, fetching images, opening youtube, opening netflix, '
        'entering chat mode, or calling no functions is best for a voice assistant '
        'to respond to the users prompt. '
        'You will respond with only one selection from this list: '
        '["take screenshot", '
        '"internet search", "check time", "create list", "show list, '
        '"pause media", "play media", "escape mode", "enter fullscreen", "increase volume", "decrease volume", '
        '"fetch images", "open netflix", "open youtube", "check date", "check temperature", "Chat mode", "None"]. '
        'Do not respond with anything but the most logical selection from that list with no explanations. Side note, only enter chat mode when it\'s specifically asked for and never anytime else.'
        'When providing information not related to any other commands or small talk, always perform an internet search to get the most accurate answers.'
    )

    function_convo = [{'role': 'system', 'content': sys_msg},
                      {'role': 'user', 'content': prompt}]
    
    chat_completion = groq_client.chat.completions.create(messages=function_convo, model='llama3-70b-8192')
    response = chat_completion.choices[0].message

    return response.content

def take_screenshot():
    path = (r'screenshot.jpg')
    with mss.mss() as sct:
            # The screen part to capture
            monitor_number = 1  # Indexing starts at 1
            monitor = sct.monitors[monitor_number]  # Use the second monitor

            sct_img = sct.shot(mon=monitor_number, output=path)

def vision_prompt(prompt, photo_path):
    img = Image.open(photo_path)
    prompt = (
        'You are the vision analysis AI that provides semantic meaning from images to provide context '
        'to send to another AI that will create a response to the user. Do not respond as the AI assistant '
        'to the user. Instead take the user prompt input and try to extract all the meaning from the photo '
        'relevant to the user prompt. Then generate as much objective data about the image for the AI '
        f'assistant who will respond to the user. \nUSER PROMPT: {prompt}'
    )
    response = model.generate_content([prompt, img])
    return response.text

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
                log("Error: 'main' key not found in the weather response. Response data:", weather_data)
        else:
            temperature = "unavailable"
            log(f"Error: Failed to retrieve weather data. HTTP Status code: {weather_response.status_code}")
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

def fetch_images(query):
    try:
        url = f"https://www.google.com/search?tbm=isch&q={query}"
        webbrowser.open(url)
        return f"Bringing up images of {query}."
    except Exception as e:
        return "Sir, something went wrong while trying to fetch images."

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

def create_list():
    list_name = input("What do want to name the list, Sir? ")
    items = []
    while True:
        item = input("What item would you like to add? ")
        if item.lower() == 'finish list':
            break
        items.append(item)
    list_content = f"\n".join(items)
    
    
    directory = "lists"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, f"{list_name}.txt")
    with open(file_path, 'w') as file:
        file.write(list_content)
    return f"List '{list_name}' has been created and saved to {file_path}, Sir."

def read_list():
    list_name = input("Which list would you like to read, Sir?")
    list_file = f"C:\\Users\\Moham\\OneDrive\\Desktop\\MK V\\lists\\{list_name}.txt"
    if os.path.exists(list_file):
        os.startfile(list_file)
    else:
        speak(f"Sir, {list_name} does not exist.")

def chat_mode():
    subprocess.Popen(['python', 'chat_mode.py'])
    return "Entering chat mode, Sir."

def listen_and_respond():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = eval(result)['text']
            log(f"Recognized: {text}")

            if "jarvis" in text.lower():
                clean_prompt = text.lower().replace("jarvis", "").strip()
                handle_prompt(clean_prompt)

def handle_prompt(clean_prompt):

    log(f'USER: {clean_prompt}')
    call = function_call(clean_prompt)

    vision_context = None
    action_response = None
    final_response = None

    if call == "take screenshot":
        log('Taking screenshot')
        take_screenshot()
        vision_context = vision_prompt(prompt=clean_prompt, photo_path=(r'screenshot.jpg'))
        os.remove(r'screenshot.jpg')
    
    elif call == "internet search":
        log('Performing internet search')
        search_results = internet_search(clean_prompt)
        clean_prompt = f'{clean_prompt}\n\n INTERNET SEARCH RESULTS: {search_results}'
        

    elif call == "check time":
        log('Checking time')
        action_response = check_time(call)
        if action_response is None:
            action_response = "An unexpected error occurred while controlling the strips."
        
        

    elif call == "check date":
        log('Checking date')
        action_response = check_date(call)
        if action_response is None:
            action_response = "An unexpected error occurred while controlling the strips."
        
        
    elif call == "check temperature":
        log('Checking temperature')
        action_response = check_weather(call)
        if action_response is None:
            action_response = "An unexpected error occurred while controlling the strips."
        
    elif call == "Chat mode":
        log('Entering chat mode')
        action_response = chat_mode()

    elif call == "increase volume":
        log('Increasing volume')
        action_response = increase_volume(call)
        

    elif call == "decrease volume":
        log('Decreasing volume')
        action_response = decrease_volume(call)
        

    elif call == "pause media":
        log('Pausing')
        action_response = pause_media(call)
    

    elif call == "play media":
        log('Playing')
        action_response = play_media(call)
        

    elif call == "escape mode":
        log('Escaping')
        action_response = escape_mode(call)
        

    elif call == "enter fullscreen":
        log('Entering fullscreen')
        action_response = enter_fullscreen(call)
        

    elif call == "open youtube":
        log('Opening youtube')
        action_response = open_youtube(call)
    

    elif call == "open netflix":
        log('Opening netflix')
        action_response = open_netflix(call)
        

    elif call == "fetch images":
        log('Fetching images')
        action_response = fetch_images(clean_prompt.split('show me an image of')[1].strip())
        
        

    elif call == "create list":
        log('Creating list')
        action_response = create_list()
        
        

    elif call == "show list":
        log('Opening list')
        action_response = read_list()
        
    
        
        
    if action_response:
        final_response = action_response
        log(f'JARVIS: {final_response}')
        speak(str(final_response))
    else:
        response_content = groq_prompt(prompt=clean_prompt, img_context=vision_context)    
        final_response = response_content    
        log(f'JARVIS: {final_response}')
        speak(str(final_response))
        
    

def extract_prompt(transcribed_text, wake_word):
    pattern = rf'\b{re.escape(wake_word)}[\s,.?!]*([A-Za-z0-9].*)'
    match = re.search(pattern, transcribed_text, re.IGNORECASE)

    if match:
        prompt = match.group(1).strip()
        return prompt
    else:
        return None

listen_and_respond()
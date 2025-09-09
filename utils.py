import os
import io
import time
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import json
import csv
from datetime import datetime

# TTS function
def speak_text_in_memory(text):
    """Generates and plays speech in memory without saving a file."""
    mp3_fp = io.BytesIO()
    tts = gTTS(text=text, lang="en", tld="co.uk")
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio = AudioSegment.from_file(mp3_fp, format="mp3")
    play(audio)

# Speech-to-text function
def transcribe_audio_input():
    """Listens for and transcribes audio input from the user."""
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        silence_start = None

        while True:
            audio = r.listen(source, timeout=None, phrase_time_limit=None)
            try:
                text = r.recognize_google(audio)
                print("Heard:", text)
                silence_start = None
                return text
            except sr.UnknownValueError:
                if silence_start is None:
                    silence_start = time.time()
                else:
                    if time.time() - silence_start > 3:
                        print(">>> Silence detected for more than 3s, TRIGGER <<<")
                        return None
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return None

# JSON output function
def json_output_responses(responses, json_chain, filename="interview_responses.json"):
    transcript = "\n".join([f"{q}\n{a}" for q, a in responses.items()])
    result = json_chain.invoke({"transcript": transcript})
    summary_text = result.get("text", "").strip()

    summary_text = summary_text.replace("```json", "").replace("```", "").strip()

    try:
        structured_data = json.loads(summary_text)
    except json.JSONDecodeError:
        structured_data = {"error": "Could not parse JSON", "raw_output": summary_text}

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

# CSV output function
def csv_log_responses(text, speaker, filename="interview_session.csv"):
    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["Time", "Speaker", "Text"])

        current_time = datetime.now().strftime("%H:%M:%S")
        writer.writerow([current_time, speaker, text])

# CSV speaker name overwrite function
def overwrite_csv(filename="interview_session.csv"):
    if not os.path.exists('interview_responses.json'):
        print("interview_responses.json not found. Cannot overwrite CSV.")
        return

    with open('interview_responses.json', 'r') as f:
        data = json.load(f)

    name = data.get("Name", "User")
    rows = []

    with open(filename, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Speaker"] == "User":
                row["Speaker"] = name
            rows.append(row)

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Time", "Speaker", "Text"])
        writer.writeheader()
        writer.writerows(rows)
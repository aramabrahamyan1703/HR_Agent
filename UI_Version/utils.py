import os
import io
import time
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import sounddevice as sd
import vosk
import json
import csv
from datetime import datetime
from global_control import event_queue

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
import vosk
import sounddevice as sd
import json
import threading

def transcribe_audio_input():
    model_path = "vosk-model-small-en-us-0.15"
    full_transcription = ""
    stop_flag = {"stop": False}

    try:
        model = vosk.Model(model_path)
    except Exception as e:
        print(f"Failed to load Vosk model: {e}")
        return ""

    samplerate = 16000
    try:
        device_info = sd.query_devices(None, 'input')
        device_id = device_info['index']
    except Exception as e:
        print(f"Audio input device error: {e}")
        return ""

    # ✅ CHANGE: Instead of waiting for raw Enter, we check queue
    def wait_for_enter():
        while True:
            event = event_queue.get()  # blocking wait
            if event == "enter":
                stop_flag["stop"] = True
                break

    threading.Thread(target=wait_for_enter, daemon=True).start()

    recognizer = vosk.KaldiRecognizer(model, samplerate)
    print("Listening for continuous speech...")

    try:
        with sd.RawInputStream(
            samplerate=samplerate, blocksize=2000,
            device=device_id, dtype='int16', channels=1
        ) as stream:
            while not stop_flag["stop"]:
                data, overflow = stream.read(stream.blocksize)
                if overflow:
                    print("Audio buffer overflow detected.")

                wav_data = bytes(data)

                if recognizer.AcceptWaveform(wav_data):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '')
                    if text:
                        full_transcription += " " + text
                else:
                    partial_result = json.loads(recognizer.PartialResult())
                    _ = partial_result.get('partial', '')

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        final_result = json.loads(recognizer.FinalResult())
        text = final_result.get('text', '')
        if text:
            full_transcription += " " + text

        return full_transcription.strip()


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
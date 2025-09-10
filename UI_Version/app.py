from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import os, signal

# Import your main interview logic
import main
from main import speak_text_in_memory

from global_control import event_queue
import main
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def index():
    return render_template("index.html")


# ✅ CHANGE: Replace speak_text_in_memory with socket emit wrapper
def speak_and_emit(text):
    socketio.emit("bot_speaking", {"text": text})
    speak_text_in_memory(text)


# Patch
import main
main.speak_text_in_memory = speak_and_emit


def run_interview_thread():
    main.run_interview()


@socketio.on("start_interview")
def handle_start(_data):
    thread = threading.Thread(target=run_interview_thread)
    thread.start()


# ✅ CHANGE: user_end_turn now simulates Enter
@socketio.on("user_end_turn")
def handle_user_end_turn(_data):
    """When user clicks End Turn, simulate Enter"""
    # Instead of calling transcribe immediately,
    # we just signal Enter to stop recording
    event_queue.put("enter")
    socketio.emit("user_speaking", {"text": "⏎ Enter pressed"})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)

from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import os
import signal
import sys
from global_control import event_queue
import main
from main import speak_text_in_memory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Keep a reference to the interview thread
interview_thread = None

@app.route("/")
def index():
    return render_template("index.html")


# Patch speak_text_in_memory to emit to frontend
original_speak = speak_text_in_memory
def speak_and_emit(text):
    socketio.emit("bot_speaking", {"text": text})
    original_speak(text)

main.speak_text_in_memory = speak_and_emit


def run_interview_thread():
    main.run_interview()


@socketio.on("start_interview")
def handle_start(_data):
    global interview_thread
    if interview_thread is None or not interview_thread.is_alive():
        interview_thread = threading.Thread(target=run_interview_thread)
        interview_thread.start()


@socketio.on("user_end_turn")
def handle_user_end_turn(_data):
    """Simulate pressing Enter for user"""
    event_queue.put("enter")
    socketio.emit("user_speaking", {"text": "⏎ Enter pressed"})


@socketio.on("end_call")
def handle_end_call(_data):
    """Safely terminate the interview and stop the server"""
    # Attempt to stop interview thread if running
    if interview_thread and interview_thread.is_alive():
        os.kill(os.getpid(), signal.SIGINT)  # raises KeyboardInterrupt in main thread

    # Emit a message to clients (optional)
    socketio.emit("call_ended", {"text": "Call has ended."})

    # Exit the process after short delay
    threading.Timer(1.0, lambda: sys.exit(0)).start()


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)

# 🎤 HR Interview Agent

This project is a **real-time HR Interview Agent** whihch simulates an **AI interviewer** that asks questions out lod, hears the responses, validates it, provides further clarification if required and handles a basic Q&A at the end using **pre-provided FAQ document**.

## 🚀 Features
- 🗣️ **Bot asks interview questions**.
- 🎧 **Audio playback** of bot responses.
- 📝 **Live transcription and validation of interviewee speech**.
- 👤 **User can hold Q&A with the agnet**.
- 🔴 **Summary, transcription and a JSON of key points** is generated.


## ⚙️ Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/HR_Agent.git
   cd hr-interview-agent

2. **Create virtual environment**
   ```bash
    python3 -m venv venv
    source venv/bin/activate   # On macOS/Linux
    venv\Scripts\activate      # On Windows
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

## ▶️ Running the UI Version

1. **Start Flask server**
   ```bash
   python app.py
2. **Open your browser at:**
   ```
   http://localhost:5001
3. **Workflow:**\
Click Start Interview → bot begins speaking and subtitles appear.\
Click End Turn → signals you are done answering.\
Click End Call → gracefully exit.

## ▶️ Running the CLI Version
1. **Run**
   ```bash
   pyhton main.py


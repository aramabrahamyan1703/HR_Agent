from itertools import tee
import os
import io
import time
from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import json
import csv
from datetime import datetime

# LangChain + LLM imports
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_anthropic import ChatAnthropic


# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

llm = None

# ----------------------------
# CLAUDE
# ----------------------------
if ANTHROPIC_API_KEY:
    print("Using Claude (Anthropic API)")
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",  # use any model, just claude is free
        temperature=0,
        anthropic_api_key=ANTHROPIC_API_KEY,
    )


# ----------------------------
# Prompt for validation
# ----------------------------
validation_prompt = PromptTemplate.from_template(
    "You are a senior recruiter in an IT office. "
    "Your task is to determine if the user's answer directly addresses the specific question encrypted between tripple backticks. "
    "If it does, respond with 'yes'. If it does not, respond with 'no' and rephrase the question to sound clearer to the interviewee using personal pronouns without redundant symbols, just a plain text. "
    "Question: ```{question}``` "
    "Answer: {answer}"
)
validation_chain = LLMChain(llm=llm, prompt=validation_prompt)

# ----------------------------
# Prompt for JSON creation
# ----------------------------
json_prompt = PromptTemplate.from_template(
    """You are an HR assistant.
    Summarize the following interview transcript and output ONLY a valid JSON object.
    
    Required fields:
    - Name
    - Interest Level for joining the team (High, Medium, Low)
    - Notice period (Ready now, Needs some time (mention the time), Not ready)
    - Background (short description)
    
    Transcript:
    ```{transcript}```

    Respond with JSON only, no explanations, no markdown, no text outside the JSON.
    """
)
json_chain = LLMChain(llm=llm, prompt=json_prompt)


# ----------------------------
# Summary Prompt
# ----------------------------
summary_prompt = PromptTemplate.from_template(
    """You are an HR assistant.
    Summarize the following interview transcript in a concise manner.

    Transcript:
    ```{transcript}```

    Provide a brief summary of the candidate's responses.
    Do NOT include any headers, lists, or bullet points.
    Use ONLY plain text of the summary.
    DO NOT use any addition symbols like asterisk.
    """
)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
FAQ_DOCUMENT = None # Placeholder for FAQ document content

# ----------------------------
# Q&A Prompt
# ----------------------------
qa_prompt = PromptTemplate.from_template(
    """You are an HR assistant.
    Answer the following question based on the provided FAQ document.

    FAQ:
    ```{FAQ_DOCUMENT}```

    Question:
    ```{question}```

    Provide a concise and relevant answer based on the context.
    Do not make up answers if the information is not available in the FAQ document, just tell that you do not know.
    Do not use any addition symbols like asterisk.
    """
)
qa_chain = LLMChain(llm=llm, prompt=qa_prompt)

# ----------------------------
# Question/No Question Prompt
# ----------------------------
no_question_prompt = PromptTemplate.from_template( """You are a helpful assistant.
    Decide if the following user input means they have no questions.

    User input:
    "{user_input}"

    Answer with ONLY one word:
    - "no_question" if the user indicates they do not have any questions.
    - "has_question" if the user is actually asking something.
    """)
no_question_chain = LLMChain(llm=llm, prompt=no_question_prompt)


# ----------------------------
# Interview questions
# ----------------------------
interview_questions = [
    "What is your full name and background?",
    "Why are you interested in joining the program?",
    "What's your experience with data science or AI?",
    "What are your short-term and long-term goals?",
    "Are you ready to start immediately? If not, when?",
]


# ----------------------------
# TTS function
# ----------------------------
def speak_text_in_memory(text):
    """Generates and plays speech in memory without saving a file."""
    mp3_fp = io.BytesIO()
    tts = gTTS(text=text, lang="en", tld="co.uk")
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio = AudioSegment.from_file(mp3_fp, format="mp3")
    play(audio)


# ----------------------------
# Speech-to-text function
# ----------------------------
def transcribe_audio_input():
    """Listens for and transcribes audio input from the user."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak_text_in_memory("You can start answering right now...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10)
            text = recognizer.recognize_google(audio)
            return text
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return None
        

# ----------------------------
# JSON output function
# ----------------------------
def json_output_responses(responses, filename="interview_responses.json"):
    transcript = "\n".join([f"{q}\n{a}" for q, a in responses.items()])
    result = json_chain.invoke({"transcript": transcript})
    summary_text = result.get("text", "").strip()

    # Remove accidental markdown fences
    summary_text = summary_text.replace("```json", "").replace("```", "").strip()

    try:
        structured_data = json.loads(summary_text)
    except json.JSONDecodeError:
        structured_data = {"error": "Could not parse JSON", "raw_output": summary_text}

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)




# ----------------------------
# CSV output function
# ----------------------------
def csv_log_responses(text, speaker, filename="interview_session.csv"):
    with open(filename, mode="a", newline="", encoding="utf-8") as f: #use mode="a" to append, mode='w' creates new file
        writer = csv.writer(f)

        # Write header only if file is empty
        if f.tell() == 0:
            writer.writerow(["Time", "Speaker", "Text"])

        current_time = datetime.now().strftime("%H:%M:%S")  # only h:m:s, can be changed to %Y-%m-%d %H:%M:%S for full timestamp
        writer.writerow([current_time, speaker, text])

# ----------------------------
# CSV speaker name overwrite function
# ----------------------------

def overwrite_csv(filename="interview_session.csv"):
    with open('interview_responses.json', 'r') as f:
        data = json.load(f)
    
    name = data.get("Name", "User")
    rows = []

    with open(filename, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Speaker"] == "User":
                row["Speaker"] = name  # new value
            rows.append(row)

    # Write back to the same CSV
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Time", "Speaker", "Text"])
        writer.writeheader()
        writer.writerows(rows)
        

# ----------------------------
# Interview loop
# ----------------------------
user_responses = {}
import subprocess
speak_text_in_memory("Hello! Welcome to the program interview.")

if os.path.exists("interview_session.csv"):
    subprocess.call(['rm', '-rf', 'interview_session.csv'])  # Remove existing CSV file for fresh logging

for question in interview_questions:
    csv_log_responses(question, speaker="Bot")
    speak_text_in_memory(question)
    time.sleep(1)

    transcription = None
    is_valid = False
    validation_attempts = 0

    while not is_valid and validation_attempts < 4:
        transcription = input('Answer:')  # Use input() for local testing without voice
        if transcription:
            # Validate with LLM
            validation_response = validation_chain.invoke(
                {"question": question, "answer": transcription}
            )["text"]

            if validation_response.strip().lower().startswith("yes"):
                is_valid = True
            else:
                # Remove the leading "no" for cleaner feedback
                feedback = validation_response.lstrip("no").strip()
                speak_text_in_memory(
                    f"That doesn't quite answer the question. {feedback} Please give more detailed answer."
                )
                validation_attempts += 1
        else:
            speak_text_in_memory("I didn't hear a response. Please try again.")
            validation_attempts += 1

    if is_valid:
        csv_log_responses(transcription, speaker="User")
        user_responses[question] = transcription
    else:
        user_responses[question] = (
            f"No valid response after {validation_attempts} attempts: {transcription}"
        )
    print("-" * 50)


# ----------------------------
# Q&A
# ----------------------------
speak_text_in_memory("If you have any questions for me, feel free to ask now. If not, you can say 'no questions' to proceed.")
csv_log_responses("If you have any questions for me, feel free to ask now. If not, you can say 'no questions' to proceed.", speaker="Bot")
while True:
    user_question = input("Your question (or type 'no questions' to finish): ")  # Use input() for local testing without voice
    csv_log_responses(user_question, speaker="User")
    intent = no_question_chain.invoke({"user_input": user_question})["text"].strip().lower()
    if intent == "no_question":
        break
    if FAQ_DOCUMENT:
        answer = qa_chain.invoke({"FAQ_DOCUMENT": FAQ_DOCUMENT, "question": user_question})["text"]
        speak_text_in_memory(answer)
        csv_log_responses(user_question, speaker="User")
        csv_log_responses(answer, speaker="Bot")
    else:
        speak_text_in_memory("Sorry, I don't have any information to answer your question. We will check it later and let you know.")
        csv_log_responses(user_question, speaker="User")
        csv_log_responses("No information available to answer the question.", speaker="Bot")


# ----------------------------
# Summary
# ----------------------------
speak_text_in_memory("Thank you for completing the interview! Here is the transcript of the interview:")

for question, response in user_responses.items():
    print(f"- {question}")
    print(f"  Response: {response}\n")

summary = summary_chain.invoke({"transcript": "\n".join([f"{q}\n{a}" for q, a in user_responses.items()])})["text"]

with open("interview_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)

json_output_responses(user_responses)
overwrite_csv()

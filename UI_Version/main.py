import os
import subprocess
import time
from itertools import tee
from global_control import event_queue

# Import everything from other files
from config import interview_questions, FAQ_DOCUMENT
from prompts import (
    validation_chain,
    json_chain,
    summary_chain,
    qa_chain,
    no_question_chain,
)
from utils import (
    speak_text_in_memory,
    transcribe_audio_input,
    json_output_responses,
    csv_log_responses,
    overwrite_csv,
)

def run_interview():
    """Main function to run the interview process."""
    user_responses = {}
    speak_text_in_memory("Hello! Welcome to the program interview.")

    if os.path.exists("interview_session.csv"):
        subprocess.call(['rm', '-rf', 'interview_session.csv'])

    for question in interview_questions:
        csv_log_responses(question, speaker="Bot")
        speak_text_in_memory(question)
        time.sleep(1)

        transcription = None
        is_valid = False
        validation_attempts = 0

        while not is_valid and validation_attempts < 4:
            transcription = transcribe_audio_input()
            if transcription:
                validation_response = validation_chain.invoke(
                    {"question": question, "answer": transcription}
                )["text"]

                if validation_response.strip().lower().startswith("yes"):
                    is_valid = True
                else:
                    feedback = validation_response.lstrip("no").strip()
                    speak_text_in_memory(f"{feedback}.")
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

    # Q&A Section
    speak_text_in_memory("If you have any questions for me, feel free to ask now. If not, you can say 'no questions' to proceed.")
    csv_log_responses("If you have any questions for me, feel free to ask now. If not, you can say 'no questions' to proceed.", speaker="Bot")
    while True:
        user_question = transcribe_audio_input()
        csv_log_responses(user_question, speaker="User")
        intent = no_question_chain.invoke({"user_input": user_question})["text"].strip().lower()
        if intent == "no_question":
            break
        if FAQ_DOCUMENT:
            answer = qa_chain.invoke({"FAQ_DOCUMENT": FAQ_DOCUMENT, "question": user_question})["text"]
            speak_text_in_memory(answer)
            csv_log_responses(answer, speaker="Bot")
        else:
            speak_text_in_memory("Sorry, I don't have any information to answer your question. We will check it later and let you know.")
            csv_log_responses("No information available to answer the question.", speaker="Bot")

    # Final summary and output
    speak_text_in_memory("Thank you for completing the interview! Here is the transcript of the interview:")

    for question, response in user_responses.items():
        print(f"- {question}")
        print(f"  Response: {response}\n")

    summary = summary_chain.invoke({"transcript": "\n".join([f"{q}\n{a}" for q, a in user_responses.items()])})["text"]

    with open("interview_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)

    json_output_responses(user_responses, json_chain)
    overwrite_csv()

if __name__ == "__main__":
    run_interview()
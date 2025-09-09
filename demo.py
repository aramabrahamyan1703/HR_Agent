import gradio as gr
from utils import transcribe_audio_input, speak_text_in_memory
from config import interview_questions, FAQ_DOCUMENT
from prompts import validation_chain, summary_chain, json_chain, qa_chain, no_question_chain

# Initialize interview state
interview_state = {
    "current_question": 0,
    "user_responses": {},
    "finished": False
}

def interview_step(audio_file):
    """
    audio_file: user-recorded audio from Gradio microphone
    Returns:
      - Bot's response text
      - Audio output for TTS
    """
    state = interview_state
    outputs = []

    # Step 1: Transcribe user audio
    if audio_file is not None:
        user_response = transcribe_audio_input(audio_file)
    else:
        user_response = None

    question_index = state["current_question"]

    # Step 2: Validate response
    if user_response:
        validation_response = validation_chain.invoke(
            {"question": interview_questions[question_index], "answer": user_response}
        )["text"]

        if validation_response.strip().lower().startswith("yes"):
            # Accept response
            state["user_responses"][interview_questions[question_index]] = user_response
            bot_text = "Response accepted ✅"
            audio_output = speak_text_in_memory(bot_text)
            state["current_question"] += 1
        else:
            feedback = validation_response.lstrip("no").strip()
            bot_text = f"Feedback: {feedback}"
            audio_output = speak_text_in_memory(bot_text)
    else:
        bot_text = "I didn't hear a response. Please try again."
        audio_output = speak_text_in_memory(bot_text)

    # Step 3: Check if finished
    if state["current_question"] >= len(interview_questions):
        state["finished"] = True
        bot_text += "\nInterview completed! Generating summary..."
        summary_text = summary_chain.invoke(
            {"transcript": "\n".join([f"{q}\n{a}" for q, a in state["user_responses"].items()])}
        )["text"]
        bot_text += f"\n\nSummary:\n{summary_text}"
        audio_output = speak_text_in_memory(bot_text)

    return bot_text, audio_output

# Gradio Interface
demo = gr.Interface(
    fn=interview_step,
    inputs=gr.Audio(source="microphone", type="filepath"),
    outputs=[gr.Textbox(label="Bot Response"), gr.Audio(type="numpy", label="Bot Audio")],
    live=False,
    title="Voice-Based Interview Prototype",
    description="Answer the interview questions using your microphone. The bot will respond with TTS."
)

if __name__ == "__main__":
    demo.launch()

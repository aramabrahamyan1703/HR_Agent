# config.py
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# Load environment variables from .env file
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

llm = None
if ANTHROPIC_API_KEY:
    print("Using Claude (Anthropic API)")
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=0,
        anthropic_api_key=ANTHROPIC_API_KEY,
    )
else:
    print("ANTHROPIC_API_KEY not found. LLM functionality will be disabled.")

# Interview questions
interview_questions = [
    "What is your full name and background?",
    "Why are you interested in joining the program?",
    "What's your experience with data science or AI?",
    "What are your short-term and long-term goals?",
    "Are you ready to start immediately? If not, when?",
]

# FAQ document placeholder
FAQ_DOCUMENT = None
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import llm

# Check if LLM is initialized before creating chains
if llm is None:
    raise ValueError("LLM not initialized. Please set ANTHROPIC_API_KEY.")

# Prompt for validation
validation_prompt = PromptTemplate.from_template(
    "You are a senior recruiter in an IT office. "
    "Your task is to determine if the user's answer directly addresses the specific question encrypted between tripple backticks. "
    "If it does, respond with 'yes'. If it does not, respond with 'no' and rephrase the question to sound clearer to the interviewee using personal pronouns without redundant symbols, just a plain text. "
    "Question: ```{question}``` "
    "Answer: {answer}"
)
validation_chain = LLMChain(llm=llm, prompt=validation_prompt)

# Prompt for JSON creation
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

# Summary Prompt
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

# Q&A Prompt
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

# Question/No Question Prompt
no_question_prompt = PromptTemplate.from_template( """You are a helpful assistant.
    Decide if the following user input means they have no questions.

    User input:
    "{user_input}"

    Answer with ONLY one word:
    - "no_question" if the user indicates they do not have any questions.
    - "has_question" if the user is actually asking something.
    """)
no_question_chain = LLMChain(llm=llm, prompt=no_question_prompt)
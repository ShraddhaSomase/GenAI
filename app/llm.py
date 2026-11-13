import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env file")

# Create Groq client
client = Groq(api_key=api_key)


def get_llm_response(user_message):

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant for a Loan Record "
                    "Management System. Answer questions about loans, "
                    "loan records, income, credit scores and loan status "
                    "in simple language. Do not invent loan record data."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0.5,
        max_tokens=500
    )

    return response.choices[0].message.content

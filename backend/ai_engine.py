import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def study_buddy(text: str, mode: str):
    response = client.chat.completions.create(
       model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are an AI Study Buddy that explains topics clearly."
            },
            {
                "role": "user",
                "content": f"{mode}: {text}"
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content




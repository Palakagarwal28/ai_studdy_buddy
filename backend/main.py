from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
import io
import os
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel
import json
class StudyRequest(BaseModel):
    text: str


# Load environment variables
load_dotenv()

# Explicit Tesseract path (Windows fix)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize FastAPI
app = FastAPI()

# Enable CORS (frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/")
def root():
    return {"message": "AI Study Buddy Backend Running"}

@app.post("/study/image")
async def study_from_image(file: UploadFile = File(...)):
    # Read image
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    # OCR
    extracted_text = pytesseract.image_to_string(image)

    if not extracted_text.strip():
        return {"error": "No text detected in image"}

    # Send to Groq LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are an AI study assistant. Explain concepts simply."
            },
            {
                "role": "user",
                "content": extracted_text
            }
        ]
    )

    explanation = response.choices[0].message.content

    return {
        "extracted_text": extracted_text,
        "explanation": explanation
    }
@app.post("/study/summary")
async def generate_summary(request: StudyRequest):
    text = request.text

    summary_prompt = f"""
Summarize the following study text clearly and concisely.

Rules:
- Use simple student-friendly language
- Do NOT ask questions
- Do NOT add examples unless necessary
- Focus only on key points
- Use bullet points
- Limit to 5–7 bullets

Text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": summary_prompt}
        ],
    )

    return {"summary": response.choices[0].message.content}

import json

@app.post("/study/quiz")
async def generate_quiz(request: StudyRequest):
    text = request.text

    quiz_prompt = f"""
Create exactly 5 multiple-choice questions from the text below.

Rules:
- Each question must have exactly 4 options
- Only one correct answer
- Return ONLY valid JSON
- Do not add explanations or markdown

JSON format:
{{
  "quiz": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": 0
    }}
  ]
}}

Text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": quiz_prompt}
        ],
    )

    return json.loads(response.choices[0].message.content)

@app.post("/study/flashcards")
async def generate_flashcards(request: StudyRequest):
    text = request.text
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "Create flashcards (Question - Answer format) from the text."
            },
            {"role": "user", "content": text}
        ]
    )
    return {"flashcards": response.choices[0].message.content}



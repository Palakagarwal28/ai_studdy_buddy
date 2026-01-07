import streamlit as st
import os
import json
from groq import Groq
from PIL import Image
import pytesseract
from dotenv import load_dotenv

# ---------- CONFIG ----------
load_dotenv()
st.set_page_config(page_title="AI Study Buddy", layout="centered")

# Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------- UI ----------
st.title("📚 AI Study Buddy")
st.write("An AI-powered study assistant for summaries, quizzes, flashcards, and image-based learning.")

text = st.text_area("✍️ Enter study text", height=180)

tab1, tab2, tab3, tab4 = st.tabs(
    ["📘 Summary", "📝 Quiz", "🗂️ Flashcards", "🖼️ Image Explain"]
)

# ---------- SUMMARY ----------
with tab1:
    if st.button("Generate Summary"):
        if not text.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Generating summary..."):
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Summarize the content in clear bullet points "
                                "using simple student-friendly language."
                            )
                        },
                        {"role": "user", "content": text}
                    ]
                )
                st.markdown(response.choices[0].message.content)

# ---------- QUIZ ----------
with tab2:
    if "quiz" not in st.session_state:
        st.session_state.quiz = []
        st.session_state.answers = {}

    if st.button("Generate Quiz"):
        if not text.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Generating quiz..."):
                quiz_prompt = f"""
Create exactly 5 multiple-choice questions from the text below.

Rules:
- Each question must have 4 options
- Only one correct answer
- Return ONLY valid JSON

JSON format:
{{
  "quiz": [
    {{
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "answer": 0
    }}
  ]
}}

Text:
{text}
"""
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": quiz_prompt}]
                )
                data = json.loads(response.choices[0].message.content)
                st.session_state.quiz = data["quiz"]
                st.session_state.answers = {}

    if st.session_state.quiz:
        score = 0
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"**{i+1}. {q['question']}**")
            choice = st.radio(
                "",
                q["options"],
                key=f"q{i}"
            )
            st.session_state.answers[i] = q["options"].index(choice)

        if st.button("Submit Quiz"):
            for i, q in enumerate(st.session_state.quiz):
                if st.session_state.answers.get(i) == q["answer"]:
                    score += 1
            st.success(f"🎉 Score: {score} / {len(st.session_state.quiz)}")

# ---------- FLASHCARDS ----------
with tab3:
    if st.button("Generate Flashcards"):
        if not text.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Generating flashcards..."):
                flash_prompt = f"""
Create 5 flashcards from the text below.

Rules:
- Return ONLY valid JSON
- Each flashcard must have a question and answer

JSON format:
{{
  "flashcards": [
    {{
      "question": "Question",
      "answer": "Answer"
    }}
  ]
}}

Text:
{text}
"""
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": flash_prompt}]
                )
                data = json.loads(response.choices[0].message.content)

                for card in data["flashcards"]:
                    with st.expander(card["question"]):
                        st.write(card["answer"])

# ---------- IMAGE ----------
with tab4:
    uploaded_file = st.file_uploader(
        "Upload an image (notes, textbook, diagram)",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        with st.spinner("Extracting text..."):
            extracted_text = pytesseract.image_to_string(image)

        if extracted_text.strip():
            st.markdown("### 📄 Extracted Text")
            st.write(extracted_text)

            with st.spinner("Explaining image content..."):
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": "Explain the extracted text in simple terms for a student."
                        },
                        {"role": "user", "content": extracted_text}
                    ]
                )
                st.markdown("### 🧠 Explanation")
                st.write(response.choices[0].message.content)
        else:
            st.warning("No readable text detected in the image.")

import React, { useState } from "react";

function App() {
  const backendURL = "http://127.0.0.1:8000";
  const [mode, setMode] = useState("");

  // Shared text input
  const [text, setText] = useState("");

  // SUMMARY
  const [summary, setSummary] = useState("");

  // QUIZ
  const [quiz, setQuiz] = useState([]);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  // FLASHCARDS
  const [flashcards, setFlashcards] = useState([]);

  // IMAGE
  const [file, setFile] = useState(null);
  const [imageResult, setImageResult] = useState("");

  // ---------- TEXT REQUEST ----------
  const sendText = async (endpoint) => {
    const response = await fetch(`${backendURL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const data = await response.json();

    if (endpoint === "/study/summary") {
      setSummary(data.summary);
    }

    if (endpoint === "/study/quiz") {
      setQuiz(data.quiz);
      setAnswers({});
      setSubmitted(false);
      setScore(0);
    }

    if (endpoint === "/study/flashcards") {
      // backend returns string → convert to array
      setFlashcards(data.flashcards.split("\n").filter(Boolean));
    }
  };

  // ---------- IMAGE REQUEST ----------
  const sendImage = async () => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${backendURL}/study/image`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    setImageResult(data.explanation || data.error);
  };

  // ---------- SUBMIT QUIZ ----------
  const submitQuiz = () => {
    let sc = 0;
    quiz.forEach((q, index) => {
      if (answers[index] === q.answer) sc++;
    });
    setScore(sc);
    setSubmitted(true);
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>AI Study Buddy</h1>

      {/* TEXT INPUT */}
      <textarea
        rows="6"
        cols="60"
        placeholder="Paste study text here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <br /><br />

      {/* BUTTONS */}
     <div className="button-row">

  <button
    onClick={() => {
      setMode("summary");
      sendText("/study/summary");
    }}
  >
    Generate Summary
  </button>

  <button
    onClick={() => {
      setMode("quiz");
      sendText("/study/quiz");
    }}
  >
    Generate Quiz
  </button>

  <button
    onClick={() => {
      setMode("flashcards");
      sendText("/study/flashcards");
    }}
  >
    Generate Flashcards
  </button>

  <button onClick={() => setMode("image")}>
    Explain Image
  </button>
</div>


      <hr />

{mode === "summary" && (
  <div className="card">
    <h2>Summary</h2>
    <p>{summary}</p>
  </div>
)}

{mode === "quiz" && (
  <div className="card">
    <h2>Quiz</h2>

    {quiz.map((q, qIndex) => (
      <div key={qIndex} style={{ marginBottom: "15px" }}>
        <strong>{qIndex + 1}. {q.question}</strong>

        {q.options.map((opt, i) => (
          <div key={i} className="quiz-option">

            <label>
              <input
                type="radio"
                name={`q-${qIndex}`}
                onChange={() =>
                  setAnswers(prev => ({ ...prev, [qIndex]: i }))
                }
              />
              {" "}{opt}
            </label>
          </div>
        ))}
      </div>
    ))}

    <button onClick={submitQuiz}>Submit Quiz</button>

    {submitted && (
     <p className="score">
  Score: {score} / {quiz.length}
</p>

    )}
  </div>
)}

{mode === "flashcards" && (
  <div className="card">
    <h2>Flashcards</h2>

    {flashcards.map((card, i) => (
  <div key={i} style={{ marginBottom: "10px" }}>
    {card}
  </div>
))}

    
  </div>
)}

{mode === "image" && (
  <div className="card">
    <h2>Explain Image</h2>

    <input
      type="file"
      accept="image/*"
      onChange={(e) => setFile(e.target.files[0])}
    />

    <br /><br />

    <button onClick={sendImage}>Explain Image</button>

    {imageResult && <p>{imageResult}</p>}
  </div>
)}

</div>
);

}
         
export default App;




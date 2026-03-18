# Art Prompt Enhancer

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=flat&logo=google&logoColor=white)
![Deployed on Vercel](https://img.shields.io/badge/Frontend-Vercel-black?style=flat&logo=vercel)
![Deployed on Render](https://img.shields.io/badge/Backend-Render-46E3B7?style=flat&logo=render&logoColor=white)

Most beginner artists know what image they want to create — but struggle to communicate it to Stable Diffusion. Art Prompt Enhancer takes a rough idea like `"girl with sword"` and rewrites it into a detailed, model-specific prompt that actually produces great results.

🔗 **Live Demo:** https://art-prompt-enhancer.vercel.app/

---

## Features

- **Text-to-enhanced prompt** — paste a rough idea, get a fully structured SD prompt with subject, style, lighting, composition, and quality boosters
- **Model-specific output** — prompts are tailored to the syntax of SD 1.5, SDXL, SD3, Flux, or Midjourney (each model responds differently to prompt structure)
- **Image-to-prompt extraction** — upload a reference image and get a prompt that recreates its visual style
- **Click-to-copy** — tap any prompt to copy it instantly to your clipboard
- **Positive and negative prompts** — both are generated together, so you can paste directly into your diffusion tool

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **FastAPI** | Lightweight Python backend — minimal boilerplate, automatic validation, async-ready |
| **React + Vite** | Fast frontend with hot reload — component state manages the full UI lifecycle |
| **Gemini 2.5 Flash** | Multimodal LLM — handles both text and image input in a single API, free tier sufficient for this use case |
| **Pydantic** | Request body validation — rejects malformed input before it reaches business logic |
| **Render** | Backend hosting — persistent server, no cold-start constraints on file upload size |
| **Vercel** | Frontend hosting — instant deploys from Git, environment variable support for API URL |

---

## Getting Started

### Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- A Gemini API key — get one free at [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/Evastrings/art-prompt-enhancer.git
cd art-prompt-enhancer
```

**2. Set up the backend**
```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

**3. Configure backend environment**
```bash
touch .env
```
Add this to the `.env` file:
```
GOOGLE_API_KEY=your_api_key_here
```

**4. Run the backend**
```bash
uvicorn main:app --reload
```
Backend will be available at `http://127.0.0.1:8000`

**5. Set up the frontend** (new terminal)
```bash
cd frontend
```
Create a `.env` file in the frontend folder:
```
VITE_API_URL=http://127.0.0.1:8000
```
Then install and run:
```bash
npm install
npm run dev
```
Frontend will be available at `http://localhost:5173`

---

## Architecture

```
frontend/src/App.jsx   ←→   backend/main.py   ←→   Gemini 2.5 Flash API
```

**Two endpoints handle all functionality:**

`POST /enhance` — accepts a JSON body `{ prompt, model }`, validated with Pydantic BaseModel. Returns `{ positive_prompt, negative_prompt }`.

`POST /upload` — accepts multipart FormData `{ file, model }`. File is read as bytes and passed directly to Gemini as a `Part` object alongside a text instruction. Returns `{ positive_prompt, negative_prompt }`.

**Key design decisions:**

- `/enhance` and `/upload` are intentionally separate — they accept different content types (JSON vs multipart), use different Gemini inputs (text vs image), and keeping them separate follows single-responsibility principle
- JSON is used for text data because it is the standard for API communication between frontend and backend. FormData (multipart) is used for file uploads because binary data cannot be serialized as JSON
- The Gemini client is initialized once at module level, not inside the endpoint functions — this avoids creating a new client on every request, which would add unnecessary overhead
- Gemini occasionally wraps JSON responses in markdown code fences despite instructions not to. A sanitization step strips these before `json.loads()` is called, preventing brittle parsing failures
- The system prompt is engineered with model-conditional instructions — SD 1.5 gets tag-style comma-separated output, Flux gets natural language sentences — because each model's text encoder responds differently to prompt structure

---

## What's Next

**Character Sheet Builder** — upload a reference image of a character, generate consistent front/side/back view prompts. Built on ControlNet via Replicate API. Character consistency is one of the most requested and least solved problems for anime and concept artists — people pay for tools that do this well.

---

## Author

Built by Elijah under (https://github.com/Evastrings)

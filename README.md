# 🕉️ Offline Bhagavad Gita Avatar Assistant

A fully offline, cross-lingual AI assistant that answers questions about the Bhagavad Gita using local LLM (Qwen2.5), vector search (Vyakyarth), speech-to-text (Vosk), text-to-speech (Piper), and a talking avatar (SadTalker).

**Reference Source**: Bhagavad_Gita_As_It_Is (1972 Edition) by A.C. Bhaktivedanta Swami Prabhupada.

---

## 🚀 Features

- **Fully Offline**: Runs entirely on your local machine (no internet required after setup).
- **Multilingual**: Ask questions in English/Hindi/Sanskrit, get answers in your chosen language.
- **Voice Input/Output**: Speak your question (Vosk) and hear the answer (Piper TTS).
- **Talking Avatar**: Generates a video of a talking head (SadTalker) synchronised with the audio.
- **Semantic Search**: Finds the most relevant Gita verses using a locally hosted vector index (FAISS + Vyakyarth).

---

## 📦 Prerequisites

- **Windows OS** (Linux/Mac support can be added, but these instructions are for Windows).
- **Python 3.10 or 3.11** (64-bit) installed and added to PATH.
- **Git** installed (to clone the repository).
- **NVIDIA GPU** (optional but recommended, ~8GB VRAM for Qwen2.5-3B). CPU fallback is supported but will be slower.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/lalitm14/BhagwatGitaAssistant_1.git
cd YOUR_REPO_NAME
```
### 2. Create and Activate a Virtual Environment (Highly Recommended)
```bash
python -m venv .venv
.venv\Scripts\activate
```
### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the Required Assets
```bash
The repository contains placeholders for the large files. You must manually download and place them as follows:

Gita PDF (1972)
:   Internet Archive → `data/Bhagavad_Gita_As_It_Is_1972.pdf`

Qwen2.5-3B (LLM)
:   `huggingface-cli download Qwen/Qwen2.5-3B-Instruct --local-dir models/llm/qwen2.5-3b-instruct` → `models/llm/qwen2.5-3b-instruct/`

Vyakyarth (Embedding)
:   `git clone https://huggingface.co/krutrim-ai-labs/vyakyarth models/Vyakyarth` → `models/Vyakyarth/`

SadTalker (Avatar)
:   `git clone https://github.com/OpenTalker/SadTalker models/SadTalker` ; then `scripts/download_models.sh` → `models/SadTalker/checkpoints/`

Piper (TTS)
:   Download `en_US-lessac-medium.onnx` + `.json` → `models/piper/`

Vosk (STT)
:   Download & unzip `vosk-model-small-en-us-0.15.zip` → `models/vosk-model-small-en-us-0.15/`

Avatar Image
:   Place any `.jpg` photo → `models/avatar/user.jpg`
'''

---

## 🏃  Running the Application

### Step 1: Build the Vector Index (One-Time)
```bash
build_index.bat
```

### Step 2: Launch the Web App
```bash
run_streamlit.bat
This will open a browser window at http://localhost:8501.
Alternative: If you prefer the command line, use:
ask_once.bat "What is Karma Yoga?"
```

---
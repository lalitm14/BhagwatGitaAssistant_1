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

Gita PDF (1972) [~13MB]
:  Source - [Internet Archive (use browser and save locally) → `data/Bhagavad_Gita_As_It_Is_1972.pdf`](http://web.archive.org/web/20240611063133/https://ia903107.us.archive.org/35/items/bhagavadgitaasitisoriginal1972edition/Bhagavad-Gita%20As%20It%20Is%20(Original%201972%20Edition).pdf
:  Destinations - data/Bhagavad_Gita_As_It_Is_1972.pdf 

Qwen2.5-3B (LLM)  [~5.75GB]
:  Source (use Windows command prompt) - huggingface-cli download Qwen/Qwen2.5-3B-Instruct --local-dir models/llm/qwen2.5-3b-instruct models/llm/qwen2.5-3b-instruct/
:  Destination: models/llm/qwen2.5-3b-instruct/
:  Alternative: Download manually from Hugging Face and place the contents in the folder. [https://huggingface.co/Qwen/Qwen2.5-3B-Instruct]

Vyakyarth (Embedding) [~2GB]
:   Source (use Windows command prompt) - git clone https://huggingface.co/krutrim-ai-labs/vyakyarth models/Vyakyarth models/Vyakyarth/
:   Destination: models/Vyakyarth/

SadTalker downloads & setup (Avatar) (all commands from Windows command prompt)  [~??GB]
:  Step-1) Clone SadTalker into the Project
:  Source: git clone https://github.com/OpenTalker/SadTalker models/SadTalker --> Destination: models/SadTalker # [163MB]
:  Step-2) Create the Dedicated sadtalker_gpu_env Virtual Environment
:  cd models/SadTalker
:  python -m venv sadtalker_gpu_env
:  sadtalker_gpu_env\scripts\activate
: Step-3) Install SadTalker dependencies
:  pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113 # (GPU users)
:  pip install torch==1.12.1+cpu torchvision==0.13.1+cpu torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cpu # (CPU users)
:  pip install -r requirements.txt
: Step-4) Download the Pre-trained Model Checkpoints
: mkdir checkpoints
: Source (copy as it is) : https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar -->  Destination: models/SadTalker/checkpoints/ #[~152MB]
: Source (copy as it is) : https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar -->  Destination: models/SadTalker/checkpoints/ #[~152MB]
: Source (copy as it is) :  https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors -->  Destination: models/SadTalker/checkpoints/ #[~708MB]
: Source (copy as it is) : https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors -->  Destination: models/SadTalker/checkpoints/ #[~708MB]
: Source (copy as it is) : https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/epoch_20.pth -->  Destination: models/SadTalker/checkpoints/ #[~282MB]
: mkdir gfpgan/weights
: Source (copy as it is) : https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth -->  Destination: models/SadTalker/gfpgans/weights #[~190MB]
: Source (copy as it is) :  https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth -->  Destination: models/SadTalker/gfpgans/weights #[~107MB]
: Source (copy as it is) :  https://huggingface.co/nlightcho/gfpgan_v14/resolve/main/GFPGANv1.4.pth -->  Destination: models/SadTalker/gfpgans/weights #[~340MB]
: Source (copy as it is) : https://huggingface.co/gmk123/GFPGAN/resolve/main/parsing_parsenet.pth -->  Destination: models/SadTalker/gfpgans/weights #[~84MB]

Piper (TTS) [~60MB]
:   Source (use broswer and save/move to destination) - 
:   1) https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
:   2) https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
:   Destination - models/piper/

Vosk (STT) [~68MB]
:  Source (unzip Extract the contents so that the am, conf, and graph folders are directly inside models/vosk-model-small-en-us-0.15/) - https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
:  Destination (copy unzip directory to <app_loc>/models directory)- models/vosk-model-small-en-us-0.15/

Avatar Image
: Source - Place any .jpg or .png photo of a face you want to animate.
: Destination (make subdirectory under <app_location>) - models/avatar/user.jpg

```
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

## 📂 Project Structure

| Path                     | Type   | Purpose                                          |
|:-------------------------|:-------|:-------------------------------------------------|
| `app/`                   | Folder | Core Python application code                     |
| `app/avatar_pipeline.py` | Script | SadTalker avatar video generation                |
| `app/build_clean_gita_json.py` | Script | Extracts PDF → structured JSON             |
| `app/build_index.py`     | Script | Creates FAISS vector index                       |
| `app/config.yaml`        | Config | Main configuration (paths, models, params)       |
| `app/gpu_utils.py`       | Script | GPU/CUDA detection & configuration               |
| `app/language_utils.py`  | Script | Multilingual script/language detection           |
| `app/query_engine.py`    | Script | Core Q&A engine (Retrieval + Generation)         |
| `app/session_archive.py` | Script | Archives & resets runtime session data           |
| `app/streamlit_app.py`   | Script | Main Streamlit web application                   |
| `app/utils.py`           | Script | Helpers (file I/O, config loading)               |
| `app/vector_store.py`    | Script | FAISS/NumPy vector storage & search              |
| `app/voice_io.py`        | Script | STT (Vosk) and TTS (Piper) handlers              |
| `ask_once.bat`           | Batch  | CLI script to ask a single question              |
| `build_index.bat`        | Batch  | Script to rebuild the vector index               |
| `run_streamlit.bat`      | Batch  | Script to launch the full web app                |
| `data/`                  | folder | Holds the PDF, JSON, indexes, and answers.       |
| `data/answers`           | folder | 	Stores runtime generated files (chat logs,     |
|                          |        | audio, avatar videos, text answers).             |
---
### ⚠️ Troubleshooting

1. CUDA Out of Memory: Reduce max_new_tokens or top_k in config.yaml. Ensure use_cpu: true under the avatar section if you cannot spare 8GB VRAM.

2. Vosk Model Not Found: Ensure the folder is named exactly vosk-model-small-en-us-0.15 and contains the am, conf, graph, and ivector folders.

3. SadTalker Python Path: If your virtual environment path differs, update sadtalker_python_exe in config.yaml to the correct Python executable path inside your .venv.

4. Port 8501 Busy: Run streamlit run app/streamlit_app.py --server.port 8502 to use a different port.

---

### 📜 License
This project is for educational and non-commercial purposes. The Gita PDF is a public domain religious text. All AI models are governed by their respective licenses (Hugging Face, MIT, Apache 2.0, etc.).

---

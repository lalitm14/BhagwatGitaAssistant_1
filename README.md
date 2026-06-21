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
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
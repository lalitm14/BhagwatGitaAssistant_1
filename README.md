# Offline Bhagavad Gita Avatar Assistant - Updated Starter Package

This package is the fresh start version with the new selector features already included.

## Included selectors

The Streamlit UI now includes:
- Document language
- Query language
- Answer language

## Directory structure

```text
gita_offline_avatar_app_v2/
├── app/
│   ├── build_index.py
│   ├── config.yaml
│   ├── language_utils.py
│   ├── query_engine.py
│   ├── streamlit_app.py
│   ├── utils.py
│   └── voice_io.py
├── data/
│   └── answers/
├── models/
├── scripts/
│   ├── ask_once.bat
│   ├── build_index.bat
│   └── run_streamlit.bat
├── requirements.txt
└── README.md
```

## First setup

Create a virtual environment and install:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Put your local assets here

- Bhagavad Gita searchable PDF:
  - `data/Bhagavad_Gita_As_It_Is_1972.pdf`
- Vyakyarth model local folder if using offline local path:
  - `models/Vyakyarth`
- Nalanda model:
  - `models/nalanda-62m-multi`
- Optional Vosk model:
  - `models/vosk-model-small-en-us-0.15`
- Optional Piper voice files:
  - `models/piper/...`

## Important config edit

If you downloaded Vyakyarth locally, change this in `app/config.yaml`:

```yaml
models:
  embedding_model: models/Vyakyarth
```

## Build the vector index

```bat
scripts\build_index.bat
```

## Run the app

```bat
scripts\run_streamlit.bat
```

## One-shot question from terminal

```bat
python app\query_engine.py "What does the Gita say about detached action?" --config app\config.yaml --answer-language English --document-language Auto --query-language Auto
```

## Notes

- `faiss-cpu` is pinned to `1.13.2` for Windows-friendly installation.
- You do not need to rebuild the index just for changing language selectors.
- Rebuild only if you change the PDF, chunking logic, or embedding model.

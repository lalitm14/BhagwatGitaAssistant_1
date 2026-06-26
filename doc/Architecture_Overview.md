# Offline Gita Avatar Assistant — System Architecture

This document describes the end-to-end architecture of the **Offline Gita Avatar Assistant**, <mark> fully local, privacy-preserving Retrieval-Augmented Generation (RAG) system. It integrates document processing, semantic indexing, local LLM inference, speech I/O, and talking-head avatar generation into a single Streamlit dashboard</mark>.

<mark >style="background: #ff9999;" Take Note, in the current version the talking head avatar feature is not implemented </mark>

---

## Figure 1: Full System Architecture

*This diagram shows the complete pipeline—from raw PDF/CSV ingestion to the final user interface—with each major Python module annotated beside its data flow.*

```mermaid
flowchart TB
    subgraph Data[" "]
        A["build_clean_gita_json.py"] 
        A1[("Extracts PDF text<br>Cleans CSV source<br>Matches verses to pages<br>Outputs structured JSON")]
        A -.- A1
    end

    subgraph Index[" "]
        B["build_index.py"]
        B1[("Chunks verse data<br>Generates embeddings<br>Builds FAISS / NumPy index<br>Saves metadata (chunks.jsonl)")]
        B -.- B1
    end

    subgraph Runtime[" "]
        C["query_engine.py"]
        C1[("Embeds user question<br>Vector similarity search<br>Concept‑aware reranking<br>Local LLM (Qwen2.5) generation")]
        C -.- C1
    end

    subgraph Voice[" "]
        D["voice_io.py"]
        D1[("Vosk STT – speech‑to‑text<br>Piper TTS – text‑to‑speech")]
        D -.- D1
    end

    subgraph Avatar[" "]
        E["avatar_pipeline.py"]
        E1[("Runs SadTalker subprocess<br>Synthesises talking‑head video<br>Copies final MP4 to answers/")]
        E -.- E1
    end

    subgraph UI[" "]
        F["streamlit_app.py"]
        F1[("Chat dashboard<br>Renders answers & citations<br>Plays audio / video<br>Manages chat history")]
        F -.- F1
    end

    A --> B --> C
    C --> D --> E
    C --> F
    D --> F
    E --> F

    style A fill:#e1f5fe,stroke:#01579b
    style B fill:#e8f5e9,stroke:#2e7d32
    style C fill:#fff3e0,stroke:#e65100
    style D fill:#f3e5f5,stroke:#6a1b9a
    style E fill:#ffebee,stroke:#c62828
    style F fill:#e0f7fa,stroke:#006064
```
# Brief Description — Figure 1

The architecture is split into six distinct stages, each handled by a dedicated Python module:

- **Data Preparation** (`build_clean_gita_json.py`): Extracts text from the source PDF, cleans the CSV data, matches verses to physical PDF pages, and builds a structured JSON corpus.

- **Indexing** (`build_index.py`): Chunks the corpus, generates dense embeddings using a SentenceTransformer model, and stores them in a FAISS/NumPy vector index alongside metadata.

- **Runtime Engine** (`query_engine.py`): The core RAG orchestrator—embeds user queries, performs vector search, applies concept-aware reranking, and generates answers via the local Qwen2.5-3B LLM.

- **Voice I/O** (`voice_io.py`): Handles microphone input using Vosk STT and produces synthesized speech using Piper TTS.

- **Avatar** (`avatar_pipeline.py`): Manages the SadTalker subprocess, feeding it the TTS audio and a source image to generate a talking-head video.

- **User Interface** (`streamlit_app.py`): Provides the interactive web dashboard, rendering answers with citations, playing audio/video, and persisting chat history.

All pipelines run fully offline, ensuring data privacy and low-latency operation without external API calls.

## Figure 2: Query & RAG Internal Flow

*This diagram dives into the query_engine.py module, illustrating the step-by-step retrieval and generation logic that transforms a user question into a structured answer with supporting citations.*

```mermaid
    flowchart LR
    subgraph Retrieval["🔎 Retrieval (query_engine.py)"]
        Q["encode()"]
        Q1[("Converts question<br>to embedding vector")]
        Q -.- Q1

        S["search()"]
        S1[("FAISS / NumPy search<br>returns top_k × 4")]
        S -.- S1

        N["_is_noisy_text()"]
        N1[("Filters malformed<br>or irrelevant results")]
        N -.- N1

        R["_score_result_quality()"]
        R1[("Concept‑aware reranking<br>+bonus for karma, bhakti,<br>paramatma, key verses")]
        R -.- R1

        D["_dedupe_results()"]
        D1[("Removes near‑duplicates<br>keeps unique entries")]
        D -.- D1
    end

    subgraph Generation["📝 Generation (query_engine.py)"]
        P["build_prompt()"]
        P1[("Constructs prompt<br>with context & language")]
        P -.- P1

        G["generate()"]
        G1[("Qwen2.5‑3B inference<br>GPU / CPU fallback")]
        G -.- G1

        A_out["_assemble_final_answer()"]
        A1_out[("Parses Answer &<br>Gita perspective sections<br>Adds citations")]
        A_out -.- A1_out

        Out["Structured Answer"]
    end

    subgraph DataFiles["📂 Data Files"]
        Idx["data/index_faiss/"]
        Chk["data/chunks.jsonl"]
        Cfg["app/config.yaml"]
    end

    Q --> S --> N --> R --> D --> P --> G --> A_out --> Out
    Idx -.- S
    Chk -.- R
    Cfg -.- P

    style Retrieval fill:#e3f2fd,stroke:#0d47a1
    style Generation fill:#fce4ec,stroke:#b71c1c
    style DataFiles fill:#f5f5f5,stroke:#9e9e9e

```
# Brief Description — Figure 2

This figure breaks down the RAG loop inside `query_engine.py` into two main phases: **Retrieval** and **Generation**.

## • Retrieval Phase:

- `encode()`: Converts the user question into a dense embedding.
- `search()`: Performs an initial semantic search over the FAISS/NumPy index, fetching a broad set of candidates (top_k × 4).
- `_is_noisy_text()`: Filters out malformed, irrelevant, or low-quality results.
- `_score_result_quality()`: Applies a custom reranking function that boosts scores for passages matching key theological concepts (e.g., *karma*, *bhakti*, *paramatma*) and specific high-relevance verses (e.g., 2.47, 18.66).
- `_dedupe_results()`: Removes near-duplicate entries to ensure diverse supporting evidence.

## • Generation Phase:

- `build_prompt()`: Formats the selected context and language settings into a structured instruction prompt.
- `generate()`: Runs inference on the local Qwen2.5-3B model (with GPU/CPU fallback).
- `_assemble_final_answer()`: Parses the LLM output to extract the "Answer" and "Gita perspective" sections, then appends verse citations.
- The final output is a **Structured Answer** ready for display, TTS synthesis, and avatar generation.

The diagram also shows the supporting data files (index_faiss/, chunks.jsonl, and config.yaml) that feed into the retrieval and prompt-building stages.

---


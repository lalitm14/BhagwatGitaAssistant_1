# Offline Gita Avatar Assistant — System Architecture

This document describes the end-to-end architecture of the **Offline Gita Avatar Assistant**, a fully local, privacy-preserving Retrieval-Augmented Generation (RAG) system. It integrates document processing, semantic indexing, local LLM inference, speech I/O, and talking-head avatar generation into a single Streamlit dashboard.

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
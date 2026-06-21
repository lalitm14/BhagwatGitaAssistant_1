from __future__ import annotations

from pathlib import Path

import streamlit as st

from avatar_pipeline import AvatarPipeline
from language_utils import (
    get_supported_answer_languages,
    get_supported_document_languages,
    get_supported_query_languages,
)
from query_engine import OfflineGitaQA
from utils import ensure_dir, load_config, read_json, write_json
from voice_io import LocalSTT, LocalTTS

st.set_page_config(page_title="Offline Gita Avatar QA", layout="wide")

CONFIG_PATH = "app/config.yaml"
cfg = load_config(CONFIG_PATH)
ensure_dir(cfg["paths"]["answers_dir"])


@st.cache_resource
def get_engine() -> OfflineGitaQA:
    return OfflineGitaQA(config_path=CONFIG_PATH)


@st.cache_resource
def get_tts() -> LocalTTS:
    return LocalTTS(config_path=CONFIG_PATH)


@st.cache_resource
def get_stt() -> LocalSTT:
    return LocalSTT(config_path=CONFIG_PATH)


@st.cache_resource
def get_avatar_pipeline() -> AvatarPipeline:
    return AvatarPipeline(config_path=CONFIG_PATH)


def load_history() -> list:
    return read_json(cfg["paths"]["chat_log_json"], default=[])


def save_history(history: list) -> None:
    write_json(cfg["paths"]["chat_log_json"], history)


def clean_for_display(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\\n", "\n").replace("\\r", "\r").strip()
    text = text.replace("\nGita perspective:", "\n\nGita perspective:")
    text = text.replace("\nSupporting verses:", "\n\nSupporting verses:")
    text = text.replace("\nCitations:", "\n\nCitations:")
    text = text.replace("\nReferences:", "\n\nReferences:")
    return text


def render_answer_block(answer_text: str) -> None:
    formatted = clean_for_display(answer_text)
    st.markdown(formatted.replace("\n", "  \n"))


def try_generate_tts(tts: LocalTTS, answer_text: str, wav_path: str) -> tuple[bool, str]:
    try:
        tts.synthesize_to_wav(answer_text, wav_path)
        return True, wav_path
    except Exception as e:
        return False, str(e)


def try_record_and_transcribe(stt: LocalSTT, wav_path: str, duration_seconds: int) -> tuple[bool, str, str]:
    try:
        saved_wav, text = stt.record_and_transcribe(wav_path=wav_path, duration_seconds=duration_seconds)
        return True, saved_wav, text
    except Exception as e:
        return False, "", str(e)


def try_generate_avatar(avatar_pipeline: AvatarPipeline) -> tuple[bool, str]:
    try:
        return avatar_pipeline.run()
    except Exception as e:
        return False, str(e)


def render_supporting_verses(sources: list) -> None:
    if not sources:
        return

    with st.expander("Supporting verses", expanded=False):
        for src in sources:
            verse = src.get("verse") or "Unknown"
            sanskrit = clean_for_display(src.get("sanskrit", ""))
            english = clean_for_display(src.get("english", ""))

            block = f"**{verse}**"
            if sanskrit:
                block += f"  \n{sanskrit}"
            if english:
                block += f"  \n*{english}*"

            st.markdown(block)


def resolve_video_path(candidate: str | Path | None) -> str:
    configured_video = Path(cfg["paths"].get("lam_output_video", "data/answers/latest_avatar.mp4"))

    if candidate:
        candidate_path = Path(str(candidate))
        if candidate_path.exists() and candidate_path.suffix.lower() == ".mp4":
            return str(candidate_path)

    if configured_video.exists():
        return str(configured_video)

    return ""


def persist_avatar_to_history(video_path: str) -> None:
    if not video_path:
        return

    history = load_history()
    latest_idx = st.session_state.get("latest_history_index", None)
    if latest_idx is not None and 0 <= latest_idx < len(history):
        history[latest_idx]["avatar_video_file"] = video_path
        save_history(history)


def render_small_video(video_path: str) -> None:
    if not video_path or not Path(video_path).exists():
        return

    left, center, right = st.columns([1.2, 2.2, 1.2])
    with center:
        st.video(video_path)


engine = get_engine()
tts = get_tts()
stt_engine = get_stt()
avatar_pipeline = get_avatar_pipeline()

if "draft_question" not in st.session_state:
    st.session_state["draft_question"] = ""
if "latest_result" not in st.session_state:
    st.session_state["latest_result"] = None
if "latest_audio_path" not in st.session_state:
    st.session_state["latest_audio_path"] = ""
if "latest_avatar_video" not in st.session_state:
    st.session_state["latest_avatar_video"] = ""
if "latest_history_index" not in st.session_state:
    st.session_state["latest_history_index"] = None

st.title("Offline Bhagavad Gita Avatar Assistant")
st.caption(
    "Cross-lingual local retrieval over structured Gita data with local answer generation, "
    "STT, TTS, and SadTalker avatar generation"
)

st.markdown('<p class="stCaption" style="background-color: #ffa500; color:black; padding: 8px; border-radius: 4px; text-align: center;">Reference Source : Bhagavad_Gita_As_It_Is_1972</p>', unsafe_allow_html=True)

with st.sidebar:
    st.subheader("Runtime Status")

    runtime_device = engine.device_info.get("device", "cpu")
    device_name = engine.device_info.get("name", "CPU")
    vram = engine.device_info.get("total_vram_gb", "0.00")

    if runtime_device == "cuda":
        st.success(f"GPU active: {device_name}")
        st.caption(f"VRAM: {vram} GB")
    else:
        st.warning("CPU fallback active")

    st.caption(f"Embedding device: {engine.embedding_device}")
    st.caption(f"Generation device: {engine.device}")
    st.caption(f"Vector backend: {engine.store.backend}")
    st.caption(f"LLM backend: {engine.llm_backend}")

    st.subheader("Voice Status")
    if tts.is_ready():
        st.success("Piper TTS ready")
    else:
        st.warning("Piper TTS not ready")

    if stt_engine.is_ready():
        st.success("Vosk STT ready")
    else:
        st.warning("Vosk STT not ready")

    st.subheader("Avatar Status")
    avatar_ready, avatar_msg = avatar_pipeline.is_ready()
    if avatar_ready:
        st.success("SadTalker avatar pipeline ready")
    else:
        st.warning(avatar_msg)

    st.subheader("Language Settings")

    doc_lang_options = get_supported_document_languages()
    query_lang_options = get_supported_query_languages()
    answer_lang_options = get_supported_answer_languages()

    default_doc_lang = cfg.get("ui", {}).get("default_document_language", "Auto")
    default_query_lang = cfg.get("ui", {}).get("default_query_language", "Auto")
    default_answer_lang = cfg.get("ui", {}).get("default_answer_language", "English")

    document_language = st.selectbox(
        "Document language",
        doc_lang_options,
        index=doc_lang_options.index(default_doc_lang) if default_doc_lang in doc_lang_options else 0,
        help="Use Auto for script-based detection, or choose a manual override.",
    )

    resolved_doc_lang = engine.resolve_document_language(document_language)
    st.info(f"Resolved document language: {resolved_doc_lang}")

    query_language = st.selectbox(
        "Query language",
        query_lang_options,
        index=query_lang_options.index(default_query_lang) if default_query_lang in query_lang_options else 0,
        help="This controls how the app interprets the user question.",
    )

    answer_language = st.selectbox(
        "Answer language",
        answer_lang_options,
        index=answer_lang_options.index(default_answer_lang) if default_answer_lang in answer_lang_options else 0,
        help="This controls the language of the final generated answer.",
    )

    auto_tts = st.checkbox("Generate speech automatically", value=True)
    auto_avatar = st.checkbox("Generate avatar automatically", value=False)

    st.subheader("Speech Input")
    record_seconds = st.slider("Record duration (seconds)", min_value=3, max_value=15, value=5, step=1)

    st.subheader("Pipeline Files")
    st.write("Text file:")
    st.code(cfg["paths"]["lam_input_text"])
    st.write("Audio file:")
    st.code(cfg["paths"]["lam_input_audio"])
    st.write("Avatar video:")
    st.code(cfg["paths"].get("lam_output_video", "data/answers/latest_avatar.mp4"))


history = load_history()

for item in history:
    with st.chat_message("user"):
        st.write(item["question"])

    with st.chat_message("assistant"):
        render_answer_block(item["answer"])

        st.caption(
            f"Runtime: {item.get('runtime_device', 'cpu')} | "
            f"Embeddings: {item.get('embedding_device', 'cpu')} | "
            f"Vector backend: {item.get('vector_backend', 'unknown')} | "
            f"LLM backend: {item.get('llm_backend', 'unknown')}"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"Document language: {item.get('document_language_resolved', 'Unknown')}")
        with col2:
            st.caption(f"Query language: {item.get('query_language_resolved', 'Unknown')}")
        with col3:
            st.caption(f"Answer language: {item.get('answer_language', 'Unknown')}")

        media_col1, media_col2 = st.columns([1, 1])
        audio_path = item.get("lam_audio_file", "")
        with media_col1:
            if audio_path and Path(audio_path).exists():
                with st.expander("Speech", expanded=False):
                    st.audio(audio_path, format="audio/wav")

        avatar_video_path = item.get("avatar_video_file", "")
        with media_col2:
            if avatar_video_path and Path(avatar_video_path).exists():
                with st.expander("Avatar", expanded=False):
                    render_small_video(avatar_video_path)

        render_supporting_verses(item.get("supporting_verses", []))

with st.expander("Speak a question", expanded=False):
    col_a, col_b = st.columns([1, 2])

    with col_a:
        if st.button("Record", use_container_width=True):
            if not stt_engine.is_ready():
                st.warning("Vosk STT is not ready.")
            else:
                mic_wav_path = str(Path(cfg["paths"]["answers_dir"]) / "latest_mic_input.wav")
                with st.spinner(f"Recording for {record_seconds} seconds... speak now"):
                    ok, saved_wav, transcript_or_error = try_record_and_transcribe(
                        stt=stt_engine,
                        wav_path=mic_wav_path,
                        duration_seconds=record_seconds,
                    )

                if ok:
                    st.success(f"Recorded audio: {saved_wav}")
                    if Path(saved_wav).exists():
                        st.audio(saved_wav, format="audio/wav")
                    st.session_state["draft_question"] = transcript_or_error
                    if transcript_or_error:
                        st.success("Transcription complete.")
                    else:
                        st.warning("No speech detected in recording.")
                else:
                    st.error(f"STT failed: {transcript_or_error}")

    with col_b:
        st.text_area(
            "Transcript / editable spoken question",
            key="draft_question",
            height=80,
        )
        spoken_submit = st.button("Ask from transcript", use_container_width=True)

typed_question = st.chat_input("Ask a question about the Bhagavad Gita")

question = ""
if st.session_state.get("draft_question") is not None and 'spoken_submit' in locals() and spoken_submit:
    question = (st.session_state.get("draft_question") or "").strip()
elif typed_question:
    question = typed_question.strip()

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.spinner("Searching local verses and generating answer..."):
        result = engine.answer(
            question=question,
            answer_language=answer_language,
            document_language=document_language,
            query_language=query_language,
        )

    st.session_state["latest_result"] = result
    st.session_state["latest_audio_path"] = ""
    st.session_state["latest_avatar_video"] = ""

    audio_ok = False
    audio_info = ""
    audio_path = cfg["paths"]["lam_input_audio"]

    if auto_tts and tts.is_ready():
        with st.spinner("Generating speech..."):
            audio_ok, audio_info = try_generate_tts(
                tts,
                result.get("answer_for_tts", result["answer"]),
                audio_path,
            )
    elif auto_tts:
        audio_info = "Piper TTS not ready."

    if audio_ok:
        st.session_state["latest_audio_path"] = audio_info

    avatar_ok = False
    avatar_info = ""
    avatar_video_file = ""

    with st.chat_message("assistant"):
        render_answer_block(result["answer"])
        st.success(f"Wrote answer text: {result['lam_text_file']}")

        if auto_tts:
            with st.expander("Speech", expanded=False):
                if audio_ok:
                    st.success(f"Wrote audio: {audio_info}")
                    st.audio(audio_info, format="audio/wav")
                else:
                    st.warning(f"TTS not generated: {audio_info}")

        if auto_avatar:
            with st.spinner("Generating avatar video..."):
                avatar_ok, avatar_info = try_generate_avatar(avatar_pipeline)

            with st.expander("Avatar", expanded=True):
                if avatar_ok:
                    resolved_video = resolve_video_path(avatar_info)
                    if resolved_video:
                        avatar_video_file = resolved_video
                        st.session_state["latest_avatar_video"] = resolved_video
                        st.success(f"Wrote avatar video: {resolved_video}")
                        render_small_video(resolved_video)
                    else:
                        st.warning("Avatar generation finished, but no MP4 file was found.")
                else:
                    st.warning(f"Avatar not generated: {avatar_info}")

        st.caption(
            f"Runtime: {result.get('runtime_device', 'cpu')} | "
            f"Embeddings: {result.get('embedding_device', 'cpu')} | "
            f"Vector backend: {result.get('vector_backend', 'unknown')} | "
            f"LLM backend: {result.get('llm_backend', 'unknown')}"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"Document language: {result.get('document_language_resolved', 'Unknown')}")
        with col2:
            st.caption(f"Query language: {result.get('query_language_resolved', 'Unknown')}")
        with col3:
            st.caption(f"Answer language: {result.get('answer_language', 'Unknown')}")

        render_supporting_verses(result.get("supporting_verses", []))

    history.append(
        {
            "question": question,
            "answer": result["answer"],
            "answer_language": result["answer_language"],
            "document_language_selected": result["document_language_selected"],
            "document_language_resolved": result["document_language_resolved"],
            "query_language_selected": result["query_language_selected"],
            "query_language_resolved": result["query_language_resolved"],
            "runtime_device": result.get("runtime_device", "cpu"),
            "embedding_device": result.get("embedding_device", "cpu"),
            "vector_backend": result.get("vector_backend", "unknown"),
            "llm_backend": result.get("llm_backend", "unknown"),
            "lam_audio_file": audio_info if audio_ok else "",
            "avatar_video_file": avatar_video_file,
            "supporting_verses": result.get("supporting_verses", []),
            "citations": result.get("citations", ""),
            "sources": result["sources"],
        }
    )
    save_history(history)
    st.session_state["latest_history_index"] = len(history) - 1

latest_result = st.session_state.get("latest_result")

if latest_result and not auto_avatar:
    with st.expander("Avatar", expanded=False):
        avatar_ready, avatar_msg = avatar_pipeline.is_ready()
        if avatar_ready:
            if st.button("Generate Avatar", key="persistent_avatar_btn", use_container_width=True):
                with st.spinner("Generating avatar video..."):
                    avatar_ok, avatar_info = try_generate_avatar(avatar_pipeline)

                if avatar_ok:
                    resolved_video = resolve_video_path(avatar_info)
                    if resolved_video:
                        st.session_state["latest_avatar_video"] = resolved_video
                        persist_avatar_to_history(resolved_video)
                        st.success(f"Wrote avatar video: {resolved_video}")
                    else:
                        st.warning("Avatar generation finished, but no MP4 file was found.")
                else:
                    st.error(avatar_info)
        else:
            st.caption(avatar_msg)

        latest_video = st.session_state.get("latest_avatar_video", "")
        if latest_video and Path(latest_video).exists():
            render_small_video(latest_video)

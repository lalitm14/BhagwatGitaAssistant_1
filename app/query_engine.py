from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    from app.gpu_utils import configure_torch, get_best_device, get_device_info, get_torch_dtype
    from app.language_utils import detect_document_language
    from app.utils import Chunk, ensure_dir, load_config, normalize_ws, write_json
    from app.vector_store import LocalVectorStore
except ImportError:
    from gpu_utils import configure_torch, get_best_device, get_device_info, get_torch_dtype
    from language_utils import detect_document_language
    from utils import Chunk, ensure_dir, load_config, normalize_ws, write_json
    from vector_store import LocalVectorStore


class OfflineGitaQA:
    CONCEPT_MAP = {
        "attachment": ["attachment", "detachment", "attached", "unattached", "fruits", "results", "success", "failure"],
        "karma": ["karma", "action", "actions", "work", "duty", "deed", "perform", "performing"],
        "karma yoga": ["karma yoga", "selfless action", "detached action", "work without attachment", "duty without attachment"],
        "renunciation": ["renunciation", "renounce", "sannyasa", "sanyas", "tyaga", "abandonment"],
        "soul": ["soul", "self", "atma", "atman", "spirit", "living being", "jiva", "jivatma"],
        "paramatma": ["paramatma", "supersoul", "super soul", "lord in the heart", "indwelling lord", "kshetrajna"],
        "brahman": ["brahman", "impersonal brahman", "absolute truth", "supreme reality"],
        "bhagavan": ["bhagavan", "supreme personality", "supreme lord", "krishna", "krsna", "purushottama"],
        "bhakti": ["bhakti", "devotion", "devotional service", "loving service", "surrender"],
        "jnana": ["jnana", "knowledge", "wisdom", "self-knowledge", "discrimination"],
        "dhyana": ["dhyana", "meditation", "mind control", "concentration", "yoga practice"],
        "gunas": ["gunas", "modes", "goodness", "passion", "ignorance", "sattva", "rajas", "tamas"],
        "dharma": ["dharma", "duty", "righteousness", "svadharma", "sacred duty"],
        "moksha": ["moksha", "liberation", "release", "freedom", "deliverance"],
        "equanimity": ["equanimity", "balance", "steady", "steadfast", "samatva", "equal in success and failure"],
        "desire": ["desire", "lust", "craving", "kama", "longing"],
        "anger": ["anger", "wrath", "krodha"],
        "mind": ["mind", "restless mind", "control the mind", "mental discipline", "manas"],
        "intellect": ["intellect", "buddhi", "discernment", "intelligence"],
        "sacrifice": ["sacrifice", "yajna", "offering", "ritual offering"],
        "food": ["food", "diet", "eating", "offer food", "prasada"],
        "faith": ["faith", "shraddha", "belief", "devotional faith"],
        "worship": ["worship", "adoration", "offerings", "devotion to god"],
        "field and knower": ["field", "knower of the field", "kshetra", "kshetrajna"],
        "universal form": ["universal form", "cosmic form", "visvarupa", "vishvarupa"],
        "divine and demoniac": ["divine qualities", "demoniac qualities", "asuric", "daivic"],
        "three paths": ["karma yoga", "jnana yoga", "bhakti yoga", "dhyana yoga"],
        "supreme path": ["highest path", "best path", "supreme path", "topmost yoga", "greatest yogi"],
    }

    def __init__(self, config_path: str = "app/config.yaml") -> None:
        self.cfg = load_config(config_path)
        configure_torch()

        self.index_dir = Path(self.cfg["paths"]["index_dir"])
        self.answers_dir = ensure_dir(self.cfg["paths"]["answers_dir"])
        self.top_k = int(self.cfg["retrieval"].get("top_k", 5))

        prefer_gpu = bool(self.cfg.get("performance", {}).get("prefer_gpu", True))
        self.embedding_device = get_best_device() if prefer_gpu else "cpu"
        self.device = get_best_device() if prefer_gpu else "cpu"
        self.dtype = (
            get_torch_dtype()
            if bool(self.cfg.get("performance", {}).get("use_fp16_on_gpu", True))
            else torch.float32
        )
        self.device_info = get_device_info()

        self.embedder = SentenceTransformer(
            self.cfg["models"]["embedding_model"],
            device=self.embedding_device,
        )

        self.store = LocalVectorStore.load(self.index_dir)
        self.chunks: List[Chunk] = self.store.metadata

        self.detected_document_language = detect_document_language(
            [c.combined_text[:800] for c in self.chunks[:30]]
        )

        self.tokenizer = None
        self.llm = None
        self.llm_backend = "fallback"

        llm_path = self.cfg["models"]["nalanda_model_path"]
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                llm_path,
                trust_remote_code=True,
                use_fast=False,
                local_files_only=True,
            )

            self.llm = AutoModelForCausalLM.from_pretrained(
                llm_path,
                trust_remote_code=True,
                local_files_only=True,
                torch_dtype=self.dtype if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
            ).to(self.device)

            self.llm.eval()
            self.llm_backend = "huggingface"
        except Exception as e:
            self.tokenizer = None
            self.llm = None
            self.llm_backend = f"fallback_only ({repr(e)})"

    def resolve_document_language(self, selected_document_language: str) -> str:
        return self.detected_document_language if selected_document_language == "Auto" else selected_document_language

    def resolve_query_language(self, query_language: str, document_language: str) -> str:
        if query_language == "Same as document":
            return document_language
        if query_language == "Auto":
            return "English"
        return query_language

    @classmethod
    def _concept_bonus(cls, question: str, english: str, verse: str | None = None) -> float:
        q = normalize_ws(question).lower()
        e = normalize_ws(english).lower()
        bonus = 0.0

        matched_concepts = []
        for concept, terms in cls.CONCEPT_MAP.items():
            if concept in q or any(term in q for term in terms):
                matched_concepts.append((concept, terms))

        for _, terms in matched_concepts:
            hits = sum(1 for term in terms if term in e)
            bonus += min(hits * 0.06, 0.24)

        if any(t in q for t in ["paramatma", "supersoul", "super soul", "lord in the heart"]):
            if any(t in e for t in ["paramatma", "supersoul", "super soul", "heart", "kshetrajna"]):
                bonus += 0.25

        if any(t in q for t in ["renunciation", "sannyasa", "tyaga"]):
            if any(t in e for t in ["renunciation", "sannyasa", "tyaga", "abandonment"]):
                bonus += 0.22

        if any(t in q for t in ["attachment", "results", "fruits"]):
            if any(t in e for t in ["attachment", "detachment", "fruits", "success", "failure"]):
                bonus += 0.22

        if any(t in q for t in ["atma", "soul", "self", "spirit"]):
            if any(t in e for t in ["atma", "soul", "self", "spirit", "eternal", "imperishable"]):
                bonus += 0.20

        if any(t in q for t in ["bhakti", "devotion", "devotional", "highest path", "best path"]):
            if any(t in e for t in ["bhakti", "devotion", "devotional", "yogi", "worship", "surrender"]):
                bonus += 0.20

        if any(t in q for t in ["brahman", "absolute truth", "supreme reality"]):
            if any(t in e for t in ["brahman", "absolute", "supreme reality", "imperishable"]):
                bonus += 0.20

        return bonus

    @staticmethod
    def _is_noisy_text(text: str) -> bool:
        if not text:
            return True

        text = normalize_ws(text)
        if len(text) < 40:
            return True

        weird_chars = len(re.findall(r"[�<>_/\\|{}\[\]~]", text))
        alpha_chars = len(re.findall(r"[A-Za-z]", text))
        digit_chars = len(re.findall(r"\d", text))

        if alpha_chars < 20:
            return True
        if weird_chars > 8:
            return True
        if digit_chars > alpha_chars:
            return True

        return False

    @classmethod
    def _score_result_quality(cls, result: Dict, question: str = "") -> float:
        score = float(result.get("score", 0.0))
        verse = result.get("verse")
        english_raw = normalize_ws(result.get("english", "") or "")
        english = english_raw.lower()
        sanskrit = normalize_ws(result.get("sanskrit", "") or "")
        q = normalize_ws(question).lower()

        quality_bonus = 0.0

        if verse:
            quality_bonus += 0.15
        if english_raw and not cls._is_noisy_text(english_raw):
            quality_bonus += 0.06
        if sanskrit:
            quality_bonus += 0.02
        if "page" in english and len(english) < 100:
            quality_bonus -= 0.03
        if cls._is_noisy_text(english_raw):
            quality_bonus -= 0.10

        if "arjun said" in english or "arjuna said" in english or "arjun asked" in english or "arjuna asked" in english:
            quality_bonus -= 0.25

        quality_bonus += cls._concept_bonus(question, english_raw, verse)

        if verse in {"2.47", "2.48", "3.19", "5.10", "5.11", "6.47", "18.2", "18.6", "18.9", "18.66", "13.22", "13.23", "15.15"}:
            quality_bonus += 0.20

        if any(t in q for t in ["renunciation", "sannyasa", "tyaga"]):
            if verse in {"18.2", "18.6", "18.9", "5.2"}:
                quality_bonus += 0.35

        if any(t in q for t in ["paramatma", "supersoul", "super soul", "lord in the heart"]):
            if verse in {"13.23", "13.32", "15.15", "18.61"}:
                quality_bonus += 1.00
            elif verse and verse.startswith("13."):
                quality_bonus += 0.20
            elif verse in {"2.25", "7.7"}:
                quality_bonus += 0.10

        if any(t in q for t in ["atma", "soul", "self", "spirit"]):
            if verse in {"2.17", "2.18", "2.20", "2.22", "15.7"}:
                quality_bonus += 0.80
            elif verse and verse.startswith("2."):
                quality_bonus += 0.20

        if any(t in q for t in ["paramatma", "supersoul", "super soul", "lord in the heart"]):
            if verse in {"17.19", "18.14", "2.3"}:
                quality_bonus -= 0.60

        if any(t in q for t in ["atma", "soul", "self", "spirit"]):
            if verse in {"4.16", "3.40", "18.22"}:
                quality_bonus -= 0.50

        if any(t in q for t in ["bhakti", "devotion", "highest path", "best path"]):
            if verse in {"6.47", "9.22", "12.2", "18.66"}:
                quality_bonus += 0.35

        return score + quality_bonus

    @staticmethod
    def _dedupe_results(results: List[Dict], limit: int) -> List[Dict]:
        deduped: List[Dict] = []
        seen = set()

        for r in results:
            key = (
                r.get("verse"),
                r.get("page"),
                normalize_ws(r.get("english", "") or "")[:120],
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(r)
            if len(deduped) >= limit:
                break

        return deduped

    def retrieve(self, question: str, top_k: int | None = None) -> List[Dict]:
        top_k = top_k or self.top_k
        raw_k = max(top_k * 4, 16)

        q_vec = self.embedder.encode(
            [question],
            batch_size=int(self.cfg.get("performance", {}).get("query_batch_size", 1)),
            convert_to_numpy=True,
            normalize_embeddings=False,
        ).astype("float32")

        scores, idxs = self.store.search(q_vec, raw_k)

        raw_results: List[Dict] = []
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist()):
            c = self.chunks[idx]
            raw_results.append(
                {
                    "score": float(score),
                    "chunk_id": c.chunk_id,
                    "page": c.page,
                    "chapter": c.chapter,
                    "verse": c.verse,
                    "sanskrit": c.sanskrit,
                    "english": c.english,
                    "combined_text": c.combined_text,
                }
            )

        filtered: List[Dict] = []
        for r in raw_results:
            english = normalize_ws(r.get("english", "") or "")
            english_l = english.lower()
            if self._is_noisy_text(english) and not bool(r.get("verse")):
                continue
            if "arjun said" in english_l or "arjuna said" in english_l or "arjun asked" in english_l or "arjuna asked" in english_l:
                continue
            filtered.append(r)

        candidates = filtered if filtered else raw_results
        candidates.sort(key=lambda r: self._score_result_quality(r, question), reverse=True)

        return self._dedupe_results(candidates, top_k)

    @staticmethod
    def _verse_label(r: Dict) -> str:
        return r.get("verse") or f"page {r.get('page')}"

    def _select_supporting_verses(self, retrieved: List[Dict], question: str, max_items: int = 3) -> List[Dict]:
        verse_results = [r for r in retrieved if r.get("verse")]
        non_verse_results = [r for r in retrieved if not r.get("verse")]

        verse_results.sort(key=lambda r: self._score_result_quality(r, question), reverse=True)
        non_verse_results.sort(key=lambda r: self._score_result_quality(r, question), reverse=True)

        selected = self._dedupe_results(verse_results, max_items)
        if len(selected) < max_items:
            needed = max_items - len(selected)
            fillers = self._dedupe_results(non_verse_results, needed)
            selected.extend(fillers)

        return selected[:max_items]

    def build_prompt(
        self,
        question: str,
        retrieved: List[Dict],
        answer_language: str = "English",
        document_language: str = "Auto",
        query_language: str = "Auto",
    ) -> str:
        context_lines = []
        for i, r in enumerate(retrieved, start=1):
            verse_label = self._verse_label(r)
            context_lines.append(
                f"[{i}] Verse: {verse_label}\n"
                f"Sanskrit: {normalize_ws(r['sanskrit'] or '')}\n"
                f"English translation/commentary: {normalize_ws(r['english'] or '')}"
            )

        resolved_doc_lang = self.resolve_document_language(document_language)
        resolved_query_lang = self.resolve_query_language(query_language, resolved_doc_lang)
        context = "\n\n".join(context_lines)

        return f"""
You are a fully local scripture assistant.

Use only the retrieved context below.
Do not invent verses.
Use ONLY the verses present in the retrieved context. Do NOT introduce new verses.
Only use verses that directly answer the question. Ignore unrelated verses.
If the context is insufficient, say so plainly.
Prefer verse references over page references whenever available.
Summarize across multiple retrieved passages when possible.
Keep the answer faithful to the provided text.
Do not include any extra roles like "Human:" or "Assistant:".
Do not repeat sections.
Do not output supporting verses or citations; those will be added separately.
Only produce the two sections requested below.

Document language: {resolved_doc_lang}
User query language: {resolved_query_lang}
Response language: {answer_language}
If the response language is Hindi, answer fully in Hindi using simple, clear sentences.

Question:
{question}

Retrieved context:
{context}

Return in exactly this format:

Answer: Provide a clear explanation in 3 to 5 sentences.

Gita perspective: Provide a philosophical explanation in 1 to 3 sentences.
""".strip()

    @torch.inference_mode()
    def generate(self, prompt: str) -> str:
        if self.tokenizer is None or self.llm is None:
            return ""

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        output = self.llm.generate(
            **inputs,
            max_new_tokens=int(self.cfg["generation"]["max_new_tokens"]),
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.1,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
            use_cache=True,
        )

        gen = self.tokenizer.decode(output[0], skip_special_tokens=True)

        if gen.startswith(prompt):
            gen = gen[len(prompt):].strip()

        gen = gen.replace("Human:", "").replace("Assistant:", "").strip()

        junk_markers = [
            "Return in exactly this format:",
            "Answer: Provide a clear explanation in 3 to 5 sentences.",
            "Gita perspective: Provide a philosophical explanation in 1 to 3 sentences.",
            "User query language:",
            "Response language:",
            "Question:",
            "Retrieved context:",
        ]
        for marker in junk_markers:
            if marker in gen:
                gen = gen.split(marker)[0].strip()

        answer_pos = gen.find("Answer:")
        if answer_pos != -1:
            gen = gen[answer_pos:].strip()

        answer_text = ""
        perspective_text = ""

        answer_match = re.search(
            r"Answer:\s*(.*?)(?:\nGita perspective:|Gita perspective:|$)",
            gen,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if answer_match:
            answer_text = normalize_ws(answer_match.group(1))

        perspective_match = re.search(
            r"Gita perspective:\s*(.*?)(?:\nAnswer:|Answer:|Supporting verses:|Citations:|$)",
            gen,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if perspective_match:
            perspective_text = normalize_ws(perspective_match.group(1))

        if len(answer_text) < 25:
            cleaned = normalize_ws(gen)
            cleaned = re.sub(r"^Answer:\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.split(
                r"Gita perspective:|Supporting verses:|Citations:",
                cleaned,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()
            if len(cleaned) >= 25:
                answer_text = cleaned

        leakage_patterns = [
            r"Return in exactly this format:.*$",
            r"Answer:\s*Provide a clear explanation in 3 to 5 sentences\..*$",
            r"Gita perspective:\s*Provide a philosophical explanation in 1 to 3 sentences\..*$",
            r"User query language:.*$",
            r"Response language:.*$",
            r"Question:.*$",
            r"Retrieved context:.*$",
        ]
        for pat in leakage_patterns:
            answer_text = re.sub(pat, "", answer_text, flags=re.IGNORECASE | re.DOTALL).strip()
            perspective_text = re.sub(pat, "", perspective_text, flags=re.IGNORECASE | re.DOTALL).strip()

        answer_text = re.split(
            r"User query language:|Response language:|Question:|Retrieved context:",
            answer_text,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip()

        if len(answer_text) > 700:
            clipped = answer_text[:700]
            sentence_end = max(clipped.rfind(". "), clipped.rfind("? "), clipped.rfind("! "))
            if sentence_end >= 120:
                answer_text = clipped[: sentence_end + 1].strip()
            else:
                answer_text = clipped.rsplit(" ", 1)[0].rstrip(" ,;:.") + "."

        perspective_text = re.split(
            r"User query language:|Response language:|Question:|Retrieved context:",
            perspective_text,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip()

        if len(perspective_text) > 240:
            perspective_text = perspective_text[:240].rsplit(" ", 1)[0].rstrip(" ,;:.") + "."

        if not answer_text:
            return ""

        if not perspective_text:
            perspective_text = "The Gita frames such questions through duty, detachment, self-knowledge, and disciplined action."

        if self.device == "cuda" and bool(self.cfg.get("performance", {}).get("clear_cuda_cache_between_tasks", False)):
            torch.cuda.empty_cache()

        return f"Answer: {answer_text}\nGita perspective: {perspective_text}".strip()

    @staticmethod
    def _clean_sanskrit_for_display(text: str) -> str:
        text = normalize_ws(text or "")
        return text if text else "not available"

    @staticmethod
    def _clean_meaning_for_display(text: str, max_len: int = 180) -> str:
        text = normalize_ws(text or "")
        if not text:
            return "not available"
        if len(text) > max_len:
            return text[:max_len].rstrip() + "..."
        return text

    def _format_supporting_verses(self, retrieved: List[Dict], question: str, max_items: int = 3) -> Tuple[str, str]:
        selected = self._select_supporting_verses(retrieved, question=question, max_items=max_items)

        if not selected:
            return (
                "- none:\n  Sanskrit: not available\n  Meaning: insufficient context",
                "none",
            )

        lines: List[str] = []
        citations: List[str] = []

        for r in selected:
            verse = self._verse_label(r)
            citations.append(verse)
            sanskrit = self._clean_sanskrit_for_display(r.get("sanskrit", "") or "")
            meaning = self._clean_meaning_for_display(r.get("english", "") or "")
            lines.append(
                f"- {verse}:\n"
                f"  Sanskrit: {sanskrit}\n"
                f"  Meaning: {meaning}"
            )

        citation_text = ", ".join(dict.fromkeys(citations))
        return "\n".join(lines), citation_text

    def _assemble_final_answer(
        self,
        narrative: str,
        retrieved: List[Dict],
        question: str,
        answer_language: str = "English",
    ) -> str:
        _, citations = self._format_supporting_verses(retrieved, question=question)

        answer_match = re.search(r"Answer:\s*(.+?)(?=Gita perspective:|$)", narrative, flags=re.DOTALL | re.IGNORECASE)
        perspective_match = re.search(r"Gita perspective:\s*(.+)$", narrative, flags=re.DOTALL | re.IGNORECASE)

        answer_text = normalize_ws(answer_match.group(1)) if answer_match else ""
        perspective_text = normalize_ws(perspective_match.group(1)) if perspective_match else ""

        if len(perspective_text) > 240:
            perspective_text = perspective_text[:240].rsplit(" ", 1)[0].rstrip(" ,;:.") + "."

        if not answer_text:
            if answer_language == "Sanskrit":
                answer_text = "उपलब्धसन्दर्भानुसार उत्तरं सावधानतया प्रस्तुतम्।"
            else:
                answer_text = "The answer below is based only on the retrieved local context."

        if not perspective_text:
            if answer_language == "Sanskrit":
                perspective_text = "गीता कर्तव्य, समत्व, आत्मबोध, तथा आसक्तिरहित कर्म पर बल देती है।"
            else:
                perspective_text = "The Gita frames such questions through duty, detachment, self-knowledge, and disciplined action."

        answer_with_refs = answer_text
        if citations and citations != "none":
            answer_with_refs = f"{answer_text} [{citations}]"

        return (
            f"Answer: {answer_with_refs}\n"
            f"Gita perspective: {perspective_text}\n"
        )

    def fallback_answer(
        self,
        question: str,
        retrieved: List[Dict],
        answer_language: str = "English",
    ) -> str:
        if not retrieved:
            if answer_language == "Sanskrit":
                return (
                    "Answer: स्थानीय अनुक्रमणिकायां उपयुक्तः सन्दर्भः न प्राप्तः।\n"
                    "Gita perspective: पर्याप्तः सन्दर्भः उपलब्धः नास्ति।\n"
                )

            if answer_language == "Hindi":
                return (
                    "Answer: मुझे उपयुक्त संदर्भ नहीं मिला।\n"
                    "Gita perspective: उपलब्ध संदर्भ पर्याप्त नहीं है।\n"
                )

            return (
                "Answer: I could not find a relevant passage in the local index.\n"
                "Gita perspective: The retrieved context is insufficient for a confident answer.\n"
            )

        best = retrieved[0]
        best_verse = self._verse_label(best)

        summaries = []
        for r in self._select_supporting_verses(retrieved, question=question, max_items=3):
            verse = self._verse_label(r)
            english = normalize_ws(r.get("english", "") or "")
            if english:
                summaries.append(
                    f"{verse}: {english[:220].rstrip()}" + ("..." if len(english) > 220 else "")
                )

        combined_summary = " ".join(summaries).strip()
        if answer_language == "Sanskrit":
            narrative = (
                f"Answer: उपलब्धसन्दर्भानुसार प्रमुखः सन्दर्भः {best_verse} इति दृश्यते। "
                f"{combined_summary if combined_summary else 'उपलब्धसन्दर्भः सीमितः अस्ति।'}\n"
                "Gita perspective: गीता कर्म, समत्व, आत्मबोध, तथा ईश्वरसमर्पणम् इत्येतान् विषयान् प्रतिपादयति।"
            )
        else:
            narrative = (
                f"Answer: Based on the retrieved text, the most relevant material centers on {best_verse}. "
                f"{combined_summary if combined_summary else 'The retrieved context is limited, so this answer is cautious.'}\n"
                "Gita perspective: The Gita explains such questions through duty, self-knowledge, disciplined action, devotion, and detachment from ego-centered outcomes."
            )

        return self._assemble_final_answer(
            narrative,
            retrieved,
            question=question,
            answer_language=answer_language,
        )

    def answer(
        self,
        question: str,
        answer_language: str = "English",
        document_language: str = "Auto",
        query_language: str = "Auto",
    ) -> Dict:
        retrieved = self.retrieve(question)
        prompt = self.build_prompt(
            question=question,
            retrieved=retrieved,
            answer_language=answer_language,
            document_language=document_language,
            query_language=query_language,
        )
        narrative = self.generate(prompt)

        if not narrative or "Answer:" not in narrative:
            raw = self.fallback_answer(question, retrieved, answer_language=answer_language)
        else:
            raw = self._assemble_final_answer(
                narrative,
                retrieved,
                question=question,
                answer_language=answer_language,
            )

        supporting_verses_text, citations = self._format_supporting_verses(
            retrieved,
            question=question,
            max_items=3,
        )
        selected_supporting_verses = self._select_supporting_verses(
            retrieved,
            question=question,
            max_items=3,
        )

        answer_only_match = re.search(
            r"Answer:\s*(.*?)(?:\nGita perspective:|$)",
            raw,
            flags=re.DOTALL | re.IGNORECASE,
        )
        answer_only_text = normalize_ws(answer_only_match.group(1)) if answer_only_match else raw

        if len(answer_only_text) > 500:
            clipped = answer_only_text[:500]
            sentence_end = max(clipped.rfind(". "), clipped.rfind("? "), clipped.rfind("! "))
            if sentence_end >= 120:
                answer_only_text = clipped[: sentence_end + 1].strip()
            else:
                answer_only_text = clipped.rsplit(" ", 1)[0].rstrip(" ,;:.") + "."

        latest_txt = Path(self.cfg["paths"]["lam_input_text"])
        ensure_dir(latest_txt.parent)
        latest_txt.write_text(answer_only_text, encoding="utf-8")

        payload = {
            "question": question,
            "answer_language": answer_language,
            "document_language_selected": document_language,
            "document_language_resolved": self.resolve_document_language(document_language),
            "query_language_selected": query_language,
            "query_language_resolved": self.resolve_query_language(
                query_language,
                self.resolve_document_language(document_language),
            ),
            "answer": raw,
            "answer_for_tts": answer_only_text,
            "supporting_verses_text": supporting_verses_text,
            "supporting_verses": selected_supporting_verses,
            "citations": citations,
            "sources": retrieved,
            "lam_text_file": str(latest_txt),
            "runtime_device": self.device,
            "embedding_device": self.embedding_device,
            "device_info": self.device_info,
            "vector_backend": self.store.backend,
            "llm_backend": self.llm_backend,
        }

        write_json(Path(self.answers_dir) / "latest_answer.json", payload)
        return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="User question")
    parser.add_argument("--config", default="app/config.yaml")
    parser.add_argument("--answer-language", default="English", choices=["English", "Sanskrit", "Hindi"])
    parser.add_argument("--document-language", default="Auto")
    parser.add_argument("--query-language", default="Auto")
    args = parser.parse_args()

    qa = OfflineGitaQA(config_path=args.config)
    result = qa.answer(
        question=args.question,
        answer_language=args.answer_language,
        document_language=args.document_language,
        query_language=args.query_language,
    )
    print(result["answer"])


if __name__ == "__main__":
    main()

import asyncio
import math
from dataclasses import dataclass

from app.config import get_settings


@dataclass(frozen=True)
class AiResult:
    value: float | str | None
    model_name: str | None
    provider: str
    status: str
    error_message: str | None = None
    metrics: dict | None = None


class AiProvider:
    def is_semantic_enabled(self) -> bool:
        settings = get_settings()
        return settings.enable_semantic_matching and bool(settings.hf_api_token)

    def is_summary_enabled(self) -> bool:
        settings = get_settings()
        return settings.enable_ai_summaries and bool(settings.hf_api_token)

    async def semantic_similarity(self, left: str, right: str) -> AiResult:
        settings = get_settings()
        if not self.is_semantic_enabled():
            return AiResult(None, settings.hf_embedding_model, settings.hf_provider, "skipped", "semantic matching disabled")
        if not left.strip() or not right.strip():
            return AiResult(None, settings.hf_embedding_model, settings.hf_provider, "skipped", "blank semantic input")
        try:
            embeddings = await asyncio.to_thread(self._embed_pair, left, right)
            score = _cosine_similarity(embeddings[0], embeddings[1])
            return AiResult(score, settings.hf_embedding_model, settings.hf_provider, "succeeded", metrics={"score": score})
        except Exception as exc:
            return AiResult(None, settings.hf_embedding_model, settings.hf_provider, "failed", str(exc))

    async def summarize(self, text: str) -> AiResult:
        settings = get_settings()
        if not self.is_summary_enabled():
            return AiResult(None, settings.hf_summary_model, settings.hf_provider, "skipped", "AI summaries disabled")
        if not text.strip():
            return AiResult(None, settings.hf_summary_model, settings.hf_provider, "skipped", "blank summary input")
        try:
            summary = await asyncio.to_thread(self._summarize_text, text)
            return AiResult(summary, settings.hf_summary_model, settings.hf_provider, "succeeded")
        except Exception as exc:
            return AiResult(None, settings.hf_summary_model, settings.hf_provider, "failed", str(exc))

    def _client(self):
        from huggingface_hub import InferenceClient

        settings = get_settings()
        return InferenceClient(provider=settings.hf_provider, api_key=settings.hf_api_token, timeout=20)

    def _embed_pair(self, left: str, right: str) -> list[list[float]]:
        settings = get_settings()
        result = self._client().feature_extraction([left, right], model=settings.hf_embedding_model, normalize=True)
        return _as_vectors(result)

    def _summarize_text(self, text: str) -> str:
        settings = get_settings()
        client = self._client()
        if hasattr(client, "summarization"):
            result = client.summarization(text[:4000], model=settings.hf_summary_model)
            if isinstance(result, str):
                return result
            if hasattr(result, "summary_text"):
                return result.summary_text
            if isinstance(result, list) and result:
                first = result[0]
                return first.get("summary_text", str(first)) if isinstance(first, dict) else str(first)
        completion = client.chat_completion(
            model=settings.hf_summary_model,
            messages=[
                {"role": "system", "content": "Summarize food recall notices for operations staff in two concise sentences."},
                {"role": "user", "content": text[:4000]},
            ],
            max_tokens=120,
            temperature=0.2,
        )
        return completion.choices[0].message.content or ""


def _as_vectors(value) -> list[list[float]]:
    if hasattr(value, "tolist"):
        value = value.tolist()
    if value and isinstance(value[0], (int, float)):
        return [value]
    return value


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return round(max(0.0, min(dot / (left_norm * right_norm), 1.0)), 4)


ai_provider = AiProvider()

import asyncio
import json

import boto3
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import ExternalServiceError

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are the Pure Lioraa product assistant for a beauty e-commerce store.
Only recommend products that appear in the CONTEXT section below — never invent products,
prices, or ingredients. Do not provide medical diagnoses or unsupported health claims; if asked
about a medical condition, suggest the customer consult a qualified professional. If the CONTEXT
does not contain a suitable product, say so honestly instead of guessing."""


class BedrockClient:
    """Wraps AWS Bedrock. boto3 is sync, so calls are pushed to a thread to stay
    non-blocking inside the async request handlers."""

    def __init__(self) -> None:
        self._runtime = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
    async def embed_text(self, text: str) -> list[float]:
        """Titan Text Embeddings V2 — used both to index KnowledgeChunk rows and
        to embed the customer's question at query time."""

        def _invoke() -> list[float]:
            response = self._runtime.invoke_model(
                modelId=settings.BEDROCK_EMBEDDING_MODEL_ID,
                body=json.dumps({"inputText": text}),
            )
            payload = json.loads(response["body"].read())
            return payload["embedding"]

        try:
            return await asyncio.to_thread(_invoke)
        except Exception as exc:  # noqa: BLE001 — boto3 raises provider-specific exceptions
            logger.error("bedrock_embed_failed", error=str(exc))
            raise ExternalServiceError("Could not reach the AI embedding service") from exc

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, max=6))
    async def generate_answer(self, *, question: str, context_chunks: list[str]) -> str:
        """Uses the Bedrock Converse API (uniform across Nova Lite/Micro and any
        future model swap) with Guardrails applied when configured."""
        context = "\n\n".join(f"- {chunk}" for chunk in context_chunks) or "(no matching products found)"
        user_message = f"CONTEXT:\n{context}\n\nCUSTOMER QUESTION:\n{question}"

        def _invoke() -> str:
            kwargs: dict = {
                "modelId": settings.BEDROCK_CHAT_MODEL_ID,
                "system": [{"text": SYSTEM_PROMPT}],
                "messages": [{"role": "user", "content": [{"text": user_message}]}],
                "inferenceConfig": {"maxTokens": 512, "temperature": 0.2},
            }
            if settings.BEDROCK_GUARDRAIL_ID:
                kwargs["guardrailConfig"] = {
                    "guardrailIdentifier": settings.BEDROCK_GUARDRAIL_ID,
                    "guardrailVersion": settings.BEDROCK_GUARDRAIL_VERSION or "DRAFT",
                }
            response = self._runtime.converse(**kwargs)
            return response["output"]["message"]["content"][0]["text"]

        try:
            return await asyncio.to_thread(_invoke)
        except Exception as exc:  # noqa: BLE001
            logger.error("bedrock_generate_failed", error=str(exc))
            raise ExternalServiceError("Could not reach the AI chat service") from exc

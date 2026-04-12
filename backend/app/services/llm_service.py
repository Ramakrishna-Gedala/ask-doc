# LLM and embedding service using AWS Bedrock
import boto3
import json
import logging
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Handles LLM calls via AWS Bedrock"""

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def generate_response(self, prompt: str, context: str) -> str:
        """
        Generate LLM response using Claude via Bedrock.

        Args:
            prompt: User query
            context: Retrieved chunks context

        Returns:
            LLM response
        """
        # Build system prompt with guardrails
        system_prompt = """You are a helpful assistant. Answer questions based ONLY on the provided context.
If the context doesn't contain information to answer the question, say "I don't have enough information in the document to answer this."
Be concise and accurate."""

        # Build final prompt
        full_prompt = f"""Context:
{context}

Question: {prompt}

Answer:"""

        try:
            # Call Claude via Bedrock
            response = self.client.invoke_model(
                modelId=settings.BEDROCK_LLM_MODEL,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-06-01",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": [
                        {
                            "role": "user",
                            "content": full_prompt
                        }
                    ]
                })
            )

            # Parse response
            response_body = json.loads(response["body"].read())
            answer = response_body["content"][0]["text"]
            logger.info("LLM response generated successfully")
            return answer

        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise


class EmbeddingService:
    """Handles embeddings via AWS Bedrock Titan"""

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text using Titan.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1536 dimensions for Titan)
        """
        try:
            response = self.client.invoke_model(
                modelId=settings.BEDROCK_EMBEDDING_MODEL,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({"inputText": text})
            )

            response_body = json.loads(response["body"].read())
            embedding = response_body["embedding"]
            return embedding

        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        embeddings = []
        for text in texts:
            try:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to embed text: {str(e)}")
                # Return zero vector on failure
                embeddings.append([0.0] * 1536)

        return embeddings

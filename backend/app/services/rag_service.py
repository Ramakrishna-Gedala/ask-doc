# RAG (Retrieval-Augmented Generation) service
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.db import Chunk, Document, ChatHistory
from app.services.llm_service import LLMService, EmbeddingService
from app.models.schemas import QueryResponse, ChunkResponse
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """Handles RAG pipeline: retrieve, augment, generate"""

    def __init__(self):
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()

    def query_document(
        self,
        db: Session,
        user_id: int,
        document_id: int,
        query: str,
        top_k: int = 5
    ) -> QueryResponse:
        """
        Execute RAG query on document.

        Flow:
        1. Embed user query
        2. Search similar chunks using pgvector
        3. Build context from top-k chunks
        4. Generate answer with LLM
        5. Store in chat history
        """

        # Validate document ownership
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()

        if not document:
            raise ValueError("Document not found or access denied")

        # Step 1: Embed query
        logger.info(f"Embedding query: {query}")
        query_embedding = self.embedding_service.embed_text(query)

        # Step 2: Semantic search using pgvector
        logger.info("Searching for similar chunks")
        similar_chunks = db.query(Chunk).filter(
            Chunk.document_id == document_id
        ).order_by(
            # pgvector similarity operator <=> (cosine similarity)
            func.cast(Chunk.embedding, type_=object).astext.op("<->")(
                func.cast(query_embedding, type_=object).astext
            )
        ).limit(top_k).all()

        if not similar_chunks:
            return QueryResponse(
                answer="No relevant information found in the document.",
                relevant_chunks=[],
                query=query,
                document_id=document_id
            )

        # Step 3: Build context
        context_parts = []
        for chunk in similar_chunks:
            context_parts.append(f"- {chunk.content}")
        context = "\n".join(context_parts)

        # Step 4: Generate answer
        logger.info("Generating LLM response")
        try:
            answer = self.llm_service.generate_response(query, context)
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            answer = "Failed to generate response. Please try again."

        # Step 5: Store in chat history
        chat_entry = ChatHistory(
            user_id=user_id,
            document_id=document_id,
            query=query,
            answer=answer,
            relevant_chunks=len(similar_chunks)
        )
        db.add(chat_entry)
        db.commit()

        # Build response
        chunk_responses = [
            ChunkResponse(
                id=chunk.id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                tokens=chunk.tokens
            )
            for chunk in similar_chunks
        ]

        return QueryResponse(
            answer=answer,
            relevant_chunks=chunk_responses,
            query=query,
            document_id=document_id
        )

    def get_chat_history(self, db: Session, user_id: int, document_id: int, limit: int = 50):
        """Get chat history for document"""
        history = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id,
            ChatHistory.document_id == document_id
        ).order_by(ChatHistory.created_at.desc()).limit(limit).all()

        return history

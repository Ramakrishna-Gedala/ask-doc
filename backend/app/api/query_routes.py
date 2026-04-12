# Query/RAG routes
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import RAGService
from app.services.validation_service import ValidationService
from app.api.auth_routes import get_current_user, TokenData
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["RAG Query"])
rag_service = RAGService()
validation_service = ValidationService()


@router.post("/ask", response_model=QueryResponse)
def ask_document(
    request: QueryRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ask a question about a document using RAG.

    Flow:
    1. Validate query
    2. Embed query
    3. Semantic search in pgvector
    4. Build context from top-k chunks
    5. Generate answer with Claude
    6. Return answer + relevant chunks

    Request:
    - **document_id**: ID of document to query
    - **query**: Question to ask
    - **top_k**: Number of relevant chunks to retrieve (default: 5)

    Returns: Answer + relevant chunks
    """
    try:
        # Validate query
        ValidationService.validate_query(request.query)

        # Perform RAG query
        logger.info(f"RAG query for document {request.document_id}: {request.query}")
        response = rag_service.query_document(
            db=db,
            user_id=current_user.user_id,
            document_id=request.document_id,
            query=request.query,
            top_k=request.top_k
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query"
        )


@router.get("/history/{document_id}")
def get_chat_history(
    document_id: int,
    limit: int = 50,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a document"""
    try:
        history = rag_service.get_chat_history(db, current_user.user_id, document_id, limit)
        return {
            "document_id": document_id,
            "total": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Failed to get chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )

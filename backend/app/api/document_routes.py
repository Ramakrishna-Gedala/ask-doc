# Document management routes
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import DocumentResponse, DocumentListResponse
from app.services.document_service import DocumentService
from app.services.file_processor import FileProcessor
from app.services.chunking_service import ChunkingService
from app.services.llm_service import EmbeddingService
from app.services.validation_service import ValidationService
from app.models.db import Chunk
from app.core.config import settings
from app.api.auth_routes import get_current_user, TokenData
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])
doc_service = DocumentService()
file_processor = FileProcessor()
chunking_service = ChunkingService()
embedding_service = EmbeddingService()
validation_service = ValidationService()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document.

    - **file**: PDF, CSV, or DOCX file (max 10MB)

    Returns: Document metadata with id
    """
    user_id = current_user.user_id

    try:
        # Check user document limit
        doc_count = doc_service.count_user_documents(db, user_id)
        if doc_count >= settings.MAX_FILES_PER_USER:
            raise ValueError(f"Maximum {settings.MAX_FILES_PER_USER} documents per user")

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file
        file_type = ValidationService.validate_file_type(file.filename, settings.ALLOWED_FILE_TYPES)
        ValidationService.validate_file_size(file_size, settings.MAX_FILE_SIZE)

        # Process file and extract text
        logger.info(f"Processing file: {file.filename}")
        original_text = FileProcessor.process_file(file_content, file_type)

        # Upload to S3
        logger.info("Uploading to S3")
        s3_key = doc_service.upload_to_s3(file_content, file.filename, user_id)

        # Save document metadata
        document = doc_service.save_document_metadata(
            db=db,
            user_id=user_id,
            filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            s3_key=s3_key,
            original_text=original_text
        )

        # Chunk text
        logger.info("Chunking document")
        chunks = chunking_service.chunk_text(original_text)

        # Generate embeddings and save chunks
        logger.info("Generating embeddings")
        for chunk_index, chunk_text in enumerate(chunks):
            # Generate embedding
            embedding = embedding_service.embed_text(chunk_text)

            # Estimate tokens
            tokens = validation_service.estimate_tokens(chunk_text)

            # Save chunk with embedding
            chunk_obj = Chunk(
                document_id=document.id,
                chunk_index=chunk_index,
                content=chunk_text,
                embedding=embedding,
                tokens=tokens
            )
            db.add(chunk_obj)

        db.commit()

        logger.info(f"Document processed successfully: {document.id}")
        return document

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document"
        )


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for current user"""
    try:
        documents = doc_service.get_user_documents(db, current_user.user_id)
        return DocumentListResponse(
            total=len(documents),
            documents=documents
        )
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific document by ID"""
    try:
        document = doc_service.get_document(db, document_id, current_user.user_id)
        return document
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    try:
        doc_service.delete_document(db, document_id, current_user.user_id)
        return {"message": "Document deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )

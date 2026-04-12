# Document management service
from sqlalchemy.orm import Session
from app.models.db import Document, Chunk, User
from app.core.config import settings
import boto3
import logging
from typing import List

logger = logging.getLogger(__name__)


class DocumentService:
    """Handles document upload and management"""

    def __init__(self):
        # Initialize S3 client
        self.s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def upload_to_s3(self, file_content: bytes, filename: str, user_id: int) -> str:
        """Upload file to S3 and return S3 key"""
        # Create S3 key: user_id/timestamp/filename
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat()
        s3_key = f"documents/{user_id}/{timestamp}/{filename}"

        try:
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=s3_key,
                Body=file_content,
            )
            logger.info(f"File uploaded to S3: {s3_key}")
            return s3_key
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise

    def save_document_metadata(
        self,
        db: Session,
        user_id: int,
        filename: str,
        file_type: str,
        file_size: int,
        s3_key: str,
        original_text: str
    ) -> Document:
        """Save document metadata to database"""
        document = Document(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            s3_key=s3_key,
            original_text=original_text
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        logger.info(f"Document metadata saved: {document.id}")
        return document

    def get_user_documents(self, db: Session, user_id: int) -> List[Document]:
        """Get all documents for a user"""
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        return documents

    def get_document(self, db: Session, document_id: int, user_id: int) -> Document:
        """Get specific document (ensure ownership)"""
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
        if not document:
            raise ValueError("Document not found or access denied")
        return document

    def delete_document(self, db: Session, document_id: int, user_id: int) -> None:
        """Delete document and related chunks"""
        document = self.get_document(db, document_id, user_id)

        # Delete from S3
        try:
            self.s3_client.delete_object(
                Bucket=settings.S3_BUCKET,
                Key=document.s3_key
            )
        except Exception as e:
            logger.warning(f"S3 delete failed: {str(e)}")

        # Delete from DB (cascades to chunks)
        db.delete(document)
        db.commit()
        logger.info(f"Document deleted: {document_id}")

    def count_user_documents(self, db: Session, user_id: int) -> int:
        """Count documents for user"""
        return db.query(Document).filter(Document.user_id == user_id).count()

# SQLAlchemy ORM models
from sqlalchemy import Column, Integer, String, DateTime, Text, LargeBinary, ForeignKey, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model - represents a tenant"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Document(Base):
    """Document model - stores file metadata"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, csv, docx
    file_size = Column(Integer, nullable=False)  # bytes
    s3_key = Column(String(500), nullable=False)  # S3 object key
    original_text = Column(Text)  # Raw extracted text
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename})>"


class Chunk(Base):
    """Chunk model - stores document chunks with embeddings"""
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    content = Column(Text, nullable=False)  # Text content
    embedding = Column(Vector(1536), nullable=False)  # Titan embedding (1536 dimensions)
    tokens = Column(Integer)  # Approximate token count
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<Chunk(id={self.id}, document_id={self.document_id})>"


class ChatHistory(Base):
    """Chat history - stores user queries and responses"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    relevant_chunks = Column(Integer)  # Number of chunks used in answer
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, user_id={self.user_id})>"

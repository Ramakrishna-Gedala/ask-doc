# Pydantic schemas for request/response validation
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# ==================== Auth Schemas ====================
class SignupRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Document Schemas ====================
class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    file_size: int


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]


# ==================== Chunk Schemas ====================
class ChunkResponse(BaseModel):
    id: int
    chunk_index: int
    content: str
    tokens: Optional[int]

    class Config:
        from_attributes = True


# ==================== Query/RAG Schemas ====================
class QueryRequest(BaseModel):
    document_id: int
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    relevant_chunks: List[ChunkResponse]
    query: str
    document_id: int


class ChatHistoryEntry(BaseModel):
    id: int
    query: str
    answer: str
    relevant_chunks: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Error Schemas ====================
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

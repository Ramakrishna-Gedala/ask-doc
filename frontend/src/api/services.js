// API service functions
import client from './client';

// ==================== Auth ====================
export const authService = {
  signup: (email, fullName, password) =>
    client.post('/auth/signup', { email, full_name: fullName, password }),

  login: (email, password) =>
    client.post('/auth/login', { email, password }),

  getCurrentUser: () =>
    client.get('/auth/me'),
};

// ==================== Documents ====================
export const documentService = {
  uploadDocument: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return client.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  listDocuments: () =>
    client.get('/documents/'),

  getDocument: (documentId) =>
    client.get(`/documents/${documentId}`),

  deleteDocument: (documentId) =>
    client.delete(`/documents/${documentId}`),
};

// ==================== Query/RAG ====================
export const queryService = {
  askQuestion: (documentId, query, topK = 5) =>
    client.post('/query/ask', { document_id: documentId, query, top_k: topK }),

  getChatHistory: (documentId, limit = 50) =>
    client.get(`/query/history/${documentId}`, { params: { limit } }),
};

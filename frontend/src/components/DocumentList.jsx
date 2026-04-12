// Document list component
import React, { useState, useEffect } from 'react';
import { Trash2, MessageSquare } from 'lucide-react';
import { documentService } from '../api/services';
import '../styles/DocumentList.css';

const DocumentList = ({ documents, onSelectDocument, onDelete, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;

    try {
      setLoading(true);
      setError(null);
      await documentService.deleteDocument(documentId);
      onDelete(documentId);
      onRefresh();
    } catch (err) {
      setError('Failed to delete document');
    } finally {
      setLoading(false);
    }
  };

  if (documents.length === 0) {
    return (
      <div className="empty-state">
        <p>No documents uploaded yet. Upload your first document to get started.</p>
      </div>
    );
  }

  return (
    <div className="document-list">
      <h2>Your Documents ({documents.length})</h2>

      {error && <div className="error-message">{error}</div>}

      <div className="documents-grid">
        {documents.map((doc) => (
          <div key={doc.id} className="document-card">
            <div className="doc-header">
              <div className="doc-info">
                <h3 className="doc-name">{doc.filename}</h3>
                <span className="doc-type">{doc.file_type.toUpperCase()}</span>
              </div>
              <span className="doc-size">
                {(doc.file_size / 1024 / 1024).toFixed(2)}MB
              </span>
            </div>

            <p className="doc-date">
              {new Date(doc.created_at).toLocaleDateString()}
            </p>

            <div className="doc-actions">
              <button
                onClick={() => onSelectDocument(doc.id)}
                className="btn-ask"
              >
                <MessageSquare size={16} />
                Ask Questions
              </button>
              <button
                onClick={() => handleDelete(doc.id)}
                disabled={loading}
                className="btn-delete"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentList;

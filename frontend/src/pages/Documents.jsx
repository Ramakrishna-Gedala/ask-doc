// Documents page - main dashboard
import React, { useState, useEffect } from 'react';
import Navigation from '../components/Navigation';
import DocumentUpload from '../components/DocumentUpload';
import DocumentList from '../components/DocumentList';
import QueryInterface from '../components/QueryInterface';
import { documentService } from '../api/services';
import '../styles/Documents.css';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await documentService.listDocuments();
      setDocuments(response.data.documents);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = (newDocument) => {
    setDocuments((prev) => [newDocument, ...prev]);
    alert('Document uploaded and processed successfully!');
  };

  const handleDeleteDocument = (documentId) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== documentId));
  };

  const handleSelectDocument = (documentId) => {
    setSelectedDocumentId(documentId);
  };

  const handleBack = () => {
    setSelectedDocumentId(null);
  };

  // Show query interface if a document is selected
  if (selectedDocumentId) {
    return (
      <>
        <Navigation />
        <div className="page-container">
          <QueryInterface documentId={selectedDocumentId} onBack={handleBack} />
        </div>
      </>
    );
  }

  // Show documents page
  return (
    <>
      <Navigation />
      <div className="page-container">
        <h1 className="page-title">Document Management</h1>

        {error && <div className="error-message">{error}</div>}

        <div className="documents-section">
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />

          {loading ? (
            <div className="loading-state">
              <p>Loading documents...</p>
            </div>
          ) : (
            <DocumentList
              documents={documents}
              onSelectDocument={handleSelectDocument}
              onDelete={handleDeleteDocument}
              onRefresh={loadDocuments}
            />
          )}
        </div>
      </div>
    </>
  );
};

export default Documents;

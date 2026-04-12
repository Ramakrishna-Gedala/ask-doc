// Document upload component
import React, { useState } from 'react';
import { Upload, X, AlertCircle } from 'lucide-react';
import { documentService } from '../api/services';
import '../styles/DocumentUpload.css';

const DocumentUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['pdf', 'csv', 'docx', 'application/pdf', 'text/csv', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!validTypes.includes(selectedFile.type) && !validTypes.includes(selectedFile.name.split('.').pop().toLowerCase())) {
        setError('Only PDF, CSV, and DOCX files are allowed');
        return;
      }

      // Validate file size (10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setLoading(true);
      setError(null);
      const response = await documentService.uploadDocument(file);
      onUploadSuccess(response.data);
      setFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-card">
      <h2>Upload Document</h2>
      <p className="upload-description">
        Supported formats: PDF, CSV, DOCX (Max 10MB)
      </p>

      <div className="upload-area">
        <input
          type="file"
          id="file-input"
          onChange={handleFileSelect}
          disabled={loading}
          accept=".pdf,.csv,.docx"
          style={{ display: 'none' }}
        />
        <label htmlFor="file-input" className="upload-label">
          <Upload size={40} />
          <span>Click to select file or drag and drop</span>
        </label>
      </div>

      {file && (
        <div className="selected-file">
          <span>{file.name}</span>
          <button onClick={() => setFile(null)} disabled={loading}>
            <X size={18} />
          </button>
        </div>
      )}

      {error && (
        <div className="error-message">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="btn-upload"
      >
        {loading ? 'Uploading...' : 'Upload Document'}
      </button>
    </div>
  );
};

export default DocumentUpload;

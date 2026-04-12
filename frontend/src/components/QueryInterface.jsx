// Query interface for asking questions about documents
import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader, ArrowLeft, AlertCircle } from 'lucide-react';
import { queryService } from '../api/services';
import '../styles/QueryInterface.css';

const QueryInterface = ({ documentId, onBack }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    try {
      setError(null);
      const userQuery = query;
      setQuery('');

      // Add user message
      setMessages((prev) => [...prev, { type: 'user', content: userQuery }]);
      setLoading(true);

      // Get response
      const response = await queryService.askQuestion(documentId, userQuery);
      const { answer, relevant_chunks } = response.data;

      // Add assistant message
      setMessages((prev) => [
        ...prev,
        { type: 'assistant', content: answer, chunks: relevant_chunks },
      ]);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to process query';
      setError(errorMsg);
      setMessages((prev) => [...prev, { type: 'error', content: errorMsg }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="query-interface">
      <div className="query-header">
        <button onClick={onBack} className="btn-back">
          <ArrowLeft size={20} />
          Back
        </button>
        <h2>Ask Questions About Document</h2>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h3>Welcome!</h3>
            <p>Ask me any questions about this document. I'll search for relevant information and provide accurate answers.</p>
          </div>
        )}

        {messages.map((message, idx) => (
          <div key={idx} className={`message message-${message.type}`}>
            <div className="message-content">
              <p>{message.content}</p>

              {message.chunks && message.chunks.length > 0 && (
                <div className="relevant-chunks">
                  <p className="chunks-label">Relevant excerpts:</p>
                  {message.chunks.map((chunk) => (
                    <div key={chunk.id} className="chunk-preview">
                      <p>{chunk.content.substring(0, 150)}...</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {error && (
          <div className="message message-error">
            <div className="message-content">
              <AlertCircle size={18} />
              <p>{error}</p>
            </div>
          </div>
        )}

        {loading && (
          <div className="message message-loading">
            <Loader size={20} className="spinner" />
            <p>Thinking...</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
          maxLength="500"
        />
        <button type="submit" disabled={loading || !query.trim()}>
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default QueryInterface;

// Navigation component
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, FileText } from 'lucide-react';
import '../styles/Navigation.css';

const Navigation = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-brand">
          <FileText size={24} />
          <span>Ask-Doc</span>
        </div>
        <div className="nav-links">
          <button className="nav-link" onClick={() => navigate('/documents')}>
            Documents
          </button>
          <span className="user-email">{user.email}</span>
          <button className="btn-logout" onClick={handleLogout}>
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;

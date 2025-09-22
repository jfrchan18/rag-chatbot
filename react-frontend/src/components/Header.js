import React from 'react';

function Header({ onNewChat, onUploadPDF }) {
  return (
    <header className="topbar">
      <div className="brand">
        RAG Chatbot 
        <span className="author">by JFRChan</span>
      </div>
      <div className="actions">
        <button 
          onClick={onNewChat}
          title="New chat"
        >
          New chat
        </button>
        <button 
          onClick={onUploadPDF}
          title="Upload a PDF file"
        >
          Upload PDF
        </button>
      </div>
    </header>
  );
}

export default Header;

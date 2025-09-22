import React, { useState, useRef, useEffect } from 'react';

function Composer({ onSend, isLoading }) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmedMessage = message.trim();
    if (!trimmedMessage || isLoading) return;
    
    onSend(trimmedMessage);
    setMessage('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const autoResize = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  };

  useEffect(() => {
    autoResize();
  }, [message]);

  return (
    <form onSubmit={handleSubmit} className="composer">
      <textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask something…"
        rows={1}
        disabled={isLoading}
        className="prompt-input"
      />
      <button 
        type="submit" 
        disabled={isLoading || !message.trim()}
        className="send-button"
      >
        Submit
      </button>
    </form>
  );
}

export default Composer;

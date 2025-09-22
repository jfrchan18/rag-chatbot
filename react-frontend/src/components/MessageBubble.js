import React from 'react';

function MessageBubble({ text, who, timestamp }) {
  const isTyping = text === "…thinking";
  
  return (
    <div className={`bubble ${who} ${isTyping ? 'typing' : ''}`}>
      {text}
    </div>
  );
}

export default MessageBubble;

import React, { forwardRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';

const Chat = forwardRef(({ messages }, ref) => {
  useEffect(() => {
    if (ref?.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
    }
  }, [messages, ref]);

  return (
    <section ref={ref} className="chat" aria-live="polite">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          text={message.text}
          who={message.who}
          timestamp={message.timestamp}
        />
      ))}
    </section>
  );
});

Chat.displayName = 'Chat';

export default Chat;

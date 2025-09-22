import React, { useState, useRef, useEffect } from 'react';
import Header from './components/Header';
import UploadSection from './components/UploadSection';
import Chat from './components/Chat';
import Composer from './components/Composer';
import ErrorMessage from './components/ErrorMessage';
import './App.css';

const API_URL = "http://localhost:8000";

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadStatus, setUploadStatus] = useState({ visible: false, message: '', type: '' });
  const chatRef = useRef(null);

  // Add welcome message on component mount
  useEffect(() => {
    if (messages.length === 0) {
      addMessage("Hello! I'm your RAG chatbot. Upload a PDF document and ask me questions about it!", "bot");
    }
  }, []);

  const addMessage = (text, who = "bot") => {
    const newMessage = {
      id: Date.now() + Math.random(),
      text,
      who,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const ask = async (query) => {
    setError('');
    setIsLoading(true);
    
    addMessage(query, "user");
    const thinkingId = Date.now() + Math.random();
    addMessage("…thinking", "bot", thinkingId);

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query, top_k: 4 }),
      });

      if (!res.ok) {
        let detail = await res.text();
        try { detail = JSON.parse(detail).detail ?? detail; } catch {}
        throw new Error(`${res.status} ${res.statusText} — ${detail}`);
      }

      const data = await res.json();
      
      // Update the thinking message with the actual response
      setMessages(prev => prev.map(msg => 
        msg.id === thinkingId 
          ? { ...msg, text: data.answer ?? "(no answer)" }
          : msg
      ));
    } catch (err) {
      setMessages(prev => prev.map(msg => 
        msg.id === thinkingId 
          ? { ...msg, text: "(failed)" }
          : msg
      ));
      setError(`Error: ${err.message || err}`);
    } finally {
      setIsLoading(false);
    }
  };

  const uploadPDF = async (file) => {
    setUploadStatus({ visible: true, message: "Uploading PDF...", type: '' });
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_name", file.name);

      const res = await fetch(`${API_URL}/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        let detail = await res.text();
        try { detail = JSON.parse(detail).detail ?? detail; } catch {}
        throw new Error(`${res.status} ${res.statusText} — ${detail}`);
      }

      const data = await res.json();
      setUploadStatus({
        visible: true,
        message: `✅ Uploaded "${data.filename}" (doc_id=${data.doc_id}), chunks created: ${data.chunks_created}`,
        type: 'success'
      });

      // Add success message to chat
      addMessage(`📄 PDF "${data.filename}" ingested! You can now ask about it.`, "bot");
    } catch (error) {
      setUploadStatus({
        visible: true,
        message: `❌ Upload failed: ${error.message}`,
        type: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError('');
    setUploadStatus({ visible: false, message: '', type: '' });
    addMessage("Hello! I'm your RAG chatbot. Upload a PDF document and ask me questions about it!", "bot");
  };

  const exportChat = () => {
    if (messages.length === 0) {
      alert('No conversation to export');
      return;
    }

    const exportText = messages.map(msg => 
      `${msg.who === 'user' ? 'User' : 'Assistant'}: ${msg.text}`
    ).join('\n\n');

    const blob = new Blob([exportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `rag-chat-export-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app">
      <Header onNewChat={clearChat} onUploadPDF={exportChat} />
      <UploadSection 
        onUpload={uploadPDF} 
        status={uploadStatus}
        isLoading={isLoading}
      />
      <Chat messages={messages} ref={chatRef} />
      <Composer onSend={ask} isLoading={isLoading} />
      <ErrorMessage error={error} />
    </div>
  );
}

export default App;

import React, { useRef } from 'react';

function UploadSection({ onUpload, status, isLoading }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!/pdf$/i.test(file.type) && !file.name.toLowerCase().endsWith(".pdf")) {
      // Handle error - could add error state here
      return;
    }

    onUpload(file);
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <section className="upload-section">
      <h3>Upload PDF Document</h3>
      <div className="upload-form">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <button 
          onClick={handleButtonClick}
          disabled={isLoading}
          className="upload-button"
        >
          {isLoading ? 'Uploading...' : 'Choose PDF File'}
        </button>
      </div>
      {status.visible && (
        <div className={`upload-status ${status.type}`}>
          {status.message}
        </div>
      )}
    </section>
  );
}

export default UploadSection;

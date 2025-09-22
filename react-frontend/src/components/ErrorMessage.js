import React from 'react';

function ErrorMessage({ error }) {
  if (!error) return null;

  return (
    <div className="error">
      {error}
    </div>
  );
}

export default ErrorMessage;

import React, { useEffect, useState } from 'react';
import './EmailContainer.css'


const EmailComponent = ({ email }) => {
  return (
    <div className="email">
      <p><strong>From:</strong> {email.From}</p>
      <p><strong>To:</strong> {email.To}</p>
      <p><strong>Date:</strong> {email.DateTime}</p>
      <p><strong>Body:</strong> {email.EmailBody}</p>
    </div>
  );
};


const EmailContainer = () => {
  const [emails, setEmails] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onmessage = (event) => {
      const newEmail = JSON.parse(event.data);
      setEmails((prevEmails) => [...prevEmails, newEmail]);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="email-container">
      {emails.map((email, index) => (
        <EmailComponent key={index} email={email} />
      ))}
    </div>
  );
};

export {EmailContainer, EmailComponent};

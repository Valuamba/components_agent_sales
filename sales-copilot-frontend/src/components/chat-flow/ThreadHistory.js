import React, { useEffect, useState } from 'react';
import './ThreadHistory.css';
import AssistantContainer from '../assistant/AssistantContainer';
import {EmailContainer, EmailComponent} from '../assistant/EmailContainer';

function ThreadHistory() {
  const [isReasoningFlowVisible, setIsReasoningFlowVisible] = useState(false);

  const getMessageComponent = (message) => {
    switch (message.type) {
      case 'email':
        return <EmailComponent email={message} />;
      case 'customer_service':
        return <AssistantContainer />;
      default:
        return null;
    }
  };

  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onmessage = (message) => {
      console.log('New EVENT!!')
      // Parse the incoming message to a JSON object
      const parsedMessage = JSON.parse(message.data);

      // Update the state to include the new message
      setMessages((prevMessages) => [...prevMessages, parsedMessage]);
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

  const toggleReasoningFlow = () => {
    setIsReasoningFlowVisible(!isReasoningFlowVisible);
  };


  return (
    <div className="center-container">
      <div className="chat-flow">
        <div className="customer-service-container">
          <div className="email-header">
            <h3 className="email-subject">Enquiry for Supply of Firetrol Battery Charger AS-2001 | AL RAMIZ</h3>
            <div className="email-info">
              <span className="email-from-to">From: Ramees Khan | AREC</span>
              <span className="email-from-to">To: Recipient</span>
              <span className="thread-date-time">2024-01-01 08:12PM</span>
            </div>
          </div>
        </div>
        <div className='assistant-container'>
          
            {messages.map((message, index) => (
              getMessageComponent(message)
          ))}

          <EmailComponent></EmailComponent>
          <AssistantContainer/>
          {/* <EmailContainer></EmailContainer> */} 
        </div>
      </div>
    </div>
  );
}

export default ThreadHistory;

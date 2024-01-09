import React, { useState } from 'react';
import './ThreadHistory.css';
import AssistantContainer from '../assistant/AssistantContainer';

function ThreadHistory() {
  const [isReasoningFlowVisible, setIsReasoningFlowVisible] = useState(false);

  const toggleReasoningFlow = () => {
    setIsReasoningFlowVisible(!isReasoningFlowVisible);
  };

  return (
    <div class="center-container">
      <div className="chat-flow">
        <div className="customer-service-container">
          <div className="email-header">
            <h3 className="email-subject">Enquiry for Supply of Firetrol Battery Charger AS-2001 | AL RAMIZ</h3>
            <div className="email-info">
              <span className="email-from-to">From: Ramees Khan | AREC</span>
              <span className="email-from-to">To: Recipient</span>
              <span className="email-date-time">2024-01-01 08:12PM</span>
            </div>
          </div>
        </div>
        <div className='assistant-container'>
          <AssistantContainer/>
        </div>
      </div>
    </div>
  );
}

export default ThreadHistory;

import React, { useState } from "react";
import "./AssistantContainer.css";
import './ToolResponseEditor.css'


const AssistantContainer = ({name, children}) => {
  return (
    <div className="email-assistant">
      <h1>{name}</h1>
      <div className="tools-container">
        {children}
      </div>
    </div>
  );
}

export default AssistantContainer;

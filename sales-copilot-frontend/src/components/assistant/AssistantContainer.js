import React, { useState } from "react";
// import ExpandableSection from './ExpandableSection';
import "./AssistantContainer.css";
import "./DropDown.css";
import "./ExpandableSection.css";
import { marked } from "marked";
import PartsListEditor from './ToolResponseEditor.js'
import './ToolResponseEditor.css'
import EmailContainer from "./EmailContainer.js";
import DraftEmailWidget from "../Widgets/draft-email/DraftEmailWidget.js";


const Dropdown = ({ title, children }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="dropdown">
      {/* <span>Some span text</span> */}
      <button className="dropdown-button" onClick={() => setIsOpen(!isOpen)}>
        {title} <span className="dropdown-arrow">{isOpen ? "▲" : "▼"}</span>
      </button>
      {isOpen && <div className="dropdown-content">{children}</div>}
    </div>
  );
};

const SectionDetail = ({ title, children }) => {
  return (
    <div className="section-detail">
      <strong>{title}:</strong> {children}
    </div>
  );
};

function MarkdownContent({ className, markdown }) {
  const htmlContent = marked.parse(markdown);

  return (
    <pre
      className={className}
      dangerouslySetInnerHTML={{ __html: htmlContent }}
    />
  );
}

const CustomerServiceState = Object.freeze({
  CLASSIFY: "classify",
  DRAFT_EMAIL: "draft_email",
});

function ExpandableSection({ title }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => setIsExpanded(!isExpanded);

  const state = CustomerServiceState.DRAFT_EMAIL;

  const message = `**System message:** You are a sales manager trained on base tasks to find manufacturer detail information at images.\n**User:** Please generate a message that asks the client about giving more details for detail Endress+Hauser\n\nFew shot: Hey sir/madam, could you please help me?`;
  const stepsDescription =
    '#### Step 2\n- **Observation:** I see the chat window with "John". There is a text input field at the bottom and a send button next to it.\n- **Thought:** I need to tap on the text input field to start typing the message.\n- **Action:** `tap(6)` (Assuming the text input field is labeled as 6)\n\n#### Step 3\n- **Observation:** The keyboard is now active and I can type the message.\n- **Thought:** I need to type the message "Hello, John".\n- **Action:** `text("Hello, John")`\n\n#### Step 4\n- **Observation:** The message "Hello, John" is now in the text input field.\n- **Thought:** I need to send the message by tapping the send button.\n- **Action:** `tap(7)` (Assuming the send button is labeled as 7)\n\n#### Step 5\n- **Observation:** The message "Hello, John" has been sent and is now visible in the chat history.\n- **Thought:** I have completed the task of sending a message to "John".\n- **Action:** `FINISH`\n\n**Summary:** I opened the chat window with "John", typed the message "Hello, John" in the text input field, and sent the message by tapping the send button. The task is now completed.';

  // Use stepsDescription as needed

  return (
    <div className="expandable-section">
      <button class="toggleButton" onClick={toggleExpand}>
        {isExpanded ? "-" : "+"} {title}
      </button>
      {isExpanded && 
            state === CustomerServiceState.CLASSIFY ? (
                <div className="section-content">
                    <Dropdown title="Sources">{/* Content for Sources */}</Dropdown>
                    <Dropdown title="Reasoning flow">
                      <div className="system-message">
                        <MarkdownContent
                          markdown={stepsDescription}
                          className="pre-formatted"
                        />
                      </div>
                    </Dropdown>
                    <Dropdown title="Metadata">
                      <div className="system-message">
                        <MarkdownContent markdown={message} className="pre-formatted" />
          
                        {/* <pre className="pre-formatted">{MarkdownContent(message)}</pre> */}
                      </div>
                    </Dropdown>
                    <PartsListEditor/>
                </div>
              )
              : state === CustomerServiceState.DRAFT_EMAIL ? (
                <div className="section-content">
                    <DraftEmailWidget></DraftEmailWidget>
                  </div>
              )
              : (
                <div></div>
              )
            }
    </div>
  );
}

function AssistantContainer() {
  return (
    <div className="email-assistant">
      <h1>Customer Service Assistant:</h1>
      <div className="tools-container">
        <ExpandableSection title="Extract detail info from e-mail body" />
        <ExpandableSection title="Extract detail info from pdf" />
        <ExpandableSection title="Extract detail info from image" />
      </div>
    </div>
  );
}

export default AssistantContainer;

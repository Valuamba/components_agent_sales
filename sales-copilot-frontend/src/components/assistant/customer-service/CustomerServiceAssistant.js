import React, { useState } from "react";

import ExpandableSection from "../../utils/expandable-section/ExpandableSection";
import MarkdownContent from "../../utils/MarkdownContent";
import MetadataDropdown from "../../utils/metadata-dropdown/MetadataDropdown";
import DraftEmailWidget from "../../Widgets/draft-email/DraftEmailWidget";
import PartsListEditor from "../ToolResponseEditor";
import "./CustomerServiceAssistant.css";
import AssistantContainer from "../AssistantContainer";
import CustomerServiceState from "../../utils/states";

const DraftMessageContainer = () => {
  return (
    <div className="section-content">
      <DraftEmailWidget></DraftEmailWidget>
    </div>
  );
};

const ClassifyCustomerRequest = () => {
  const message = `**System message:** You are a sales manager trained on base tasks to find manufacturer detail information at images.\n**User:** Please generate a message that asks the client about giving more details for detail Endress+Hauser\n\nFew shot: Hey sir/madam, could you please help me?`;
  const stepsDescription =
    '#### Step 2\n- **Observation:** I see the chat window with "John". There is a text input field at the bottom and a send button next to it.\n- **Thought:** I need to tap on the text input field to start typing the message.\n- **Action:** `tap(6)` (Assuming the text input field is labeled as 6)\n\n#### Step 3\n- **Observation:** The keyboard is now active and I can type the message.\n- **Thought:** I need to type the message "Hello, John".\n- **Action:** `text("Hello, John")`\n\n#### Step 4\n- **Observation:** The message "Hello, John" is now in the text input field.\n- **Thought:** I need to send the message by tapping the send button.\n- **Action:** `tap(7)` (Assuming the send button is labeled as 7)\n\n#### Step 5\n- **Observation:** The message "Hello, John" has been sent and is now visible in the chat history.\n- **Thought:** I have completed the task of sending a message to "John".\n- **Action:** `FINISH`\n\n**Summary:** I opened the chat window with "John", typed the message "Hello, John" in the text input field, and sent the message by tapping the send button. The task is now completed.';

  return <div className="section-content">
    <MetadataDropdown title="Sources">
    </MetadataDropdown>
    <MetadataDropdown title="Reasoning flow">
      <div className="system-message">
        <MarkdownContent
          markdown={stepsDescription}
          className="pre-formatted"
        />
      </div>
    </MetadataDropdown>
    <MetadataDropdown title="Metadata">
      <div className="system-message">
        <MarkdownContent markdown={message} className="pre-formatted" />
      </div>
    </MetadataDropdown>
    <PartsListEditor />
  </div>;
};

const CustomerServiceAssistant = ({state}) => {

  return (
    <AssistantContainer name="Customer Service Assistant">
      <ExpandableSection title="Draft Email">
        {state === CustomerServiceState.CLASSIFY ? (
          <ClassifyCustomerRequest />
        ) : state === CustomerServiceState.DRAFT_EMAIL ? (
          <DraftMessageContainer />
        ) : (
          <div>{state}</div>
        )}
      </ExpandableSection>
      
    </AssistantContainer>
  );
};

export default CustomerServiceAssistant;

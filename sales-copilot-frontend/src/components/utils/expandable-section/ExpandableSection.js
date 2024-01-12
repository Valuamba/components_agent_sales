import { useState } from "react";
import React from "react";
import './ExpandableSection.css'

const ExpandableSection = ({ title, children }) => {
    const [isExpanded, setIsExpanded] = useState(false);
  
    const toggleExpand = () => setIsExpanded(!isExpanded);
  
    return (
      <div className="expandable-section">
        <button class="toggleButton" onClick={toggleExpand}>
          {isExpanded ? "-" : "+"} {title}
        </button>
        {isExpanded && (children)}
      </div>
    );
}


export default ExpandableSection;
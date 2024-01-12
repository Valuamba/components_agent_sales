import React, {useState} from 'react';
import './MetadataDropdown.css'


const MetadataDropdown = ({ title, children }) => {
    const [isOpen, setIsOpen] = useState(false);
  
    return (
      <div className="dropdown">
        <button className="dropdown-button" onClick={() => setIsOpen(!isOpen)}>
          {title} <span className="dropdown-arrow">{isOpen ? "▲" : "▼"}</span>
        </button>
        {isOpen && <div className="dropdown-content">{children}</div>}
      </div>
    );
  };


export default MetadataDropdown;
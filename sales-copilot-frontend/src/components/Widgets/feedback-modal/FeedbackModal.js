import React from 'react';
import './FeedbackModal.css';

const FeedbackModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <h2>Help us improve</h2>
        <p>Provide additional feedback on this answer. Select all that apply.</p>
        <form className="feedback-form">
          <label className="checkbox-container">Inaccurate<input type="checkbox" /><span className="checkmark"></span></label>
          <label className="checkbox-container">Too short<input type="checkbox" /><span className="checkmark"></span></label>
          <label className="checkbox-container">Not helpful<input type="checkbox" /><span className="checkmark"></span></label>
          <label className="checkbox-container">Hallucinates<input type="checkbox" /><span className="checkmark"></span></label>
          
          {/* Repeat the label/input structure for each checkbox option */}
          <textarea placeholder="How can the response be improved? (optional)" />
          <div className="modal-buttons">
            <button type="button" onClick={onClose}>Cancel</button>
            <button type="submit">Submit</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FeedbackModal;

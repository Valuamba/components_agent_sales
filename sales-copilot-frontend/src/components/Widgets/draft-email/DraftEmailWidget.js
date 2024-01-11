import React, {useState} from "react";
import './DraftEmailWidget.css'
import { FaThumbsUp, FaThumbsDown } from 'react-icons/fa';
import FeedbackModal from "../feedback-modal/FeedbackModal";


const DraftEmailWidget = (to, from, body) => {
    const [feedback, setFeedback] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const closeModal = () => setIsModalOpen(false);


    const handleFeedback = (type) => {
        setFeedback(type);

        if (type === 'dislike') {
            setIsModalOpen(true);
        }
      };

    to = "elon@spacex.com";
    from = "ivan@famaga.de"
    body = "Dear SpaceX Team,\n\nI am John Smith from AstroTech Innovations, reaching out with an exciting opportunity tailored for SpaceX's starship engines. Our latest product, the 'AstroThrust-5X', promises to enhance your spacecraft's efficiency and durability.\n\nKey features include a 20% increase in thrust power, exceptional fuel efficiency with hybrid compatibility, and a robust design using aerospace-grade materials for extreme temperature resilience. Our components are engineered for easy integration with existing SpaceX models, ensuring a smooth upgrade process.\n\nUnderstanding SpaceX's mission-centric approach, we offer customization to align with your specific requirements. With our proposal, we extend a special discount and priority support, aiming to foster a long-term partnership.\n\nLet's explore this opportunity further. Would you be available for a brief call next week?\n\nBest Regards,\nJohn Smith\nSales Manager, AstroTech Innovations\nEmail: john.smith@astrotech.com\nPhone: +1 (555) 987-6543";


    return (
        <div className="email-draft-items-container">
            <div className="email-field">
                <span className="email-field-label">To:</span>
                <input className="email-field-input" value={to} placeholder="mmm.marchuk@mail.ru"></input>
            </div>
            <div className="email-field">
                <span className="email-field-label">From:</span>
                <input className="email-field-input" value={from} placeholder="ivan@famaga.de"></input>
            </div>
            <textarea className="email-draft-body" value={body}></textarea>

            <div className="feedback-email-actions-container">
                <div className="feedback-container">
                    <button className={`feedback-button ${feedback === 'like' ? 'active' : ''}`} onClick={() => handleFeedback('like')}>
                        <FaThumbsUp />
                    </button>
                    <button className={`feedback-button ${feedback === 'dislike' ? 'active' : ''}`} onClick={() => handleFeedback('dislike')}>
                        <FaThumbsDown />
                    </button>
                    <FeedbackModal isOpen={isModalOpen} onClose={closeModal} />
                </div>
                <div className="email-action-container">
                    <button className="email-dismiss email-action-button">Dismiss</button>
                    <button className="email-submit email-action-button">Submit and Send</button>
                </div>
            </div>
        </div>
    )
}

export default DraftEmailWidget;
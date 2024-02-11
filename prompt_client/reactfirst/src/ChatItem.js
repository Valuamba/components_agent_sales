import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatItem = ({ item }) => {
    const hasFeedback = item.feedback && item.feedback.trim() !== '';

    return (
        <div className="chat-item">
            <div className="chat-item-uuid">
                <input type="text" value={item.id} readOnly />
            </div>
            {hasFeedback && (
                <div className="message feedback">
                <ReactMarkdown>{item.feedback}</ReactMarkdown>
                {/* <FaCommentDots /> */}
                </div>
            )}
        <div className="message user-message">
            <ReactMarkdown children={item.prompt} />
        </div>
        <div className="message bot-message">
            <ReactMarkdown children={item.response} />
        </div>
        </div>
    );
    };

export default ChatItem;

import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatItem = ({ item }) => {
    const hasFeedback = item.feedback && item.feedback.trim() !== '';

    const formatText = (text) => {
        return text.split('\n').join('  \n'); // Two spaces followed by a newline for markdown
    };

    return (
        <div className="chat-item">
            <div className="chat-item-uuid">
                <input type="text" value={item.id} readOnly />
            </div>
            {hasFeedback && (
                <div className="message feedback">
                <ReactMarkdown>{formatText(item.feedback)}</ReactMarkdown>
                </div>
            )}
            <div className="message user-message">
                <ReactMarkdown>{formatText(item.prompt)}</ReactMarkdown>
            </div>
            <div className="message bot-message">
                <ReactMarkdown>{formatText(item.response)}</ReactMarkdown>
            </div>
        </div>
    );
    };

export default ChatItem;

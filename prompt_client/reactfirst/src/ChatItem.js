import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

const ChatItem = ({ item }) => {
    const [userViewMode, setUserViewMode] = useState('visual'); // 'visual' or 'markdown' for user message
    const [botViewMode, setBotViewMode] = useState('visual'); // 'visual' or 'markdown' for bot message

    const [editingFeedback, setEditingFeedback] = useState(false); // State to control edit form visibility
    const [feedback, setFeedback] = useState(item.feedback || '');
    const [tempFeedback, setTempFeedback] = useState('');
    const [isLike, setIsLike] = useState(item.is_like);


    // This effect runs whenever the `item` prop changes
    useEffect(() => {
        setFeedback(item.feedback || '');
        setIsLike(item.is_like);
    }, [item]);

    const handleEditClick = () => {
        setTempFeedback(feedback); // Copy current feedback to temporary state
        setEditingFeedback(true); // Show edit form
    };

        // Function to cancel editing
    const handleCancel = () => {
        setEditingFeedback(false); // Hide edit form
        setTempFeedback(''); // Clear temporary feedback
    };

    // Function to save feedback after editing
    const handleSave = () => {
        setFeedback(tempFeedback); // Update feedback with edited content
        setEditingFeedback(false); // Hide edit form
        submitFeedback(); // Call your existing function to submit feedback to the backend
    };

     const submitFeedback = () => {
        const feedbackData = { feedback: tempFeedback, is_like: isLike };
        fetch(`http://127.0.0.1:8004/feedback/${item.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(feedbackData),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Feedback submitted successfully:', data);
            // Handle success response, e.g., showing a notification to the user
        })
        .catch(error => {
            console.error('Failed to submit feedback:', error);
            // Handle error response, e.g., showing an error message to the user
        });
    };
    const formatText = (text) => {
        return text.split('\n').join('  \n'); // Two spaces followed by a newline for markdown
    };

    return (
        <div className="chat-item">
            <div className="chat-item-uuid">
                <input type="text" value={item.id} readOnly/>
            </div>
            <div className="message feedback">
                <ReactMarkdown>{feedback}</ReactMarkdown>

                {/* Display icons for like or dislike if provided, excluding feedback icon */}
                {!editingFeedback && (
                    <div className="feedback-icons">
                        {isLike === true &&
                            <span className="icon like-icon">👍</span> /* Replace with <FaThumbsUp /> */}
                        {isLike === false &&
                            <span className="icon dislike-icon">👎</span> /* Replace with <FaThumbsDown /> */}
                    </div>
                )}

                {editingFeedback ? (
                    <>
                        <textarea
                            value={tempFeedback}
                            onChange={(e) => setTempFeedback(e.target.value)}
                            placeholder="Edit your feedback here..."
                        />
                        <div className="like-dislike-buttons">
                            <button
                                onClick={() => setIsLike(true)}
                                className={`like ${isLike === true ? 'selected' : ''}`}>
                                👍 Like
                            </button>
                            <button
                                onClick={() => setIsLike(false)}
                                className={`dislike ${isLike === false ? 'selected' : ''}`}>
                                👎 Dislike
                            </button>
                        </div>
                        <button onClick={handleSave} className="save">Save</button>
                        <button onClick={handleCancel} className="cancel">Cancel</button>
                    </>
                ) : (
                    <button onClick={handleEditClick} className="edit">Edit</button>
                )}
            </div>
            <div className="message user-message">
                <div className="view-toggle-buttons">
                    <button onClick={() => setUserViewMode('visual')}>Visual</button>
                    <button onClick={() => setUserViewMode('markdown')}>Markdown</button>
                </div>
                {userViewMode === 'visual' ?
                    <ReactMarkdown>{formatText(item.prompt)}</ReactMarkdown> :
                    <pre>{formatText(item.prompt)}</pre>
                }
            </div>
            <div className="message bot-message">
                <div className="view-toggle-buttons">
                    <button onClick={() => setBotViewMode('visual')}>Visual</button>
                    <button onClick={() => setBotViewMode('markdown')}>Markdown</button>
                </div>
                {botViewMode === 'visual' ?
                    <ReactMarkdown>{formatText(item.response)}</ReactMarkdown> :
                    <pre>{formatText(item.response)}</pre>
                }
            </div>
        </div>
    );
};

export default ChatItem;

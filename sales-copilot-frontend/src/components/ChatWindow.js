import React, { useState } from "react";
import './ChatWindow.css';


// import React, { useState } from 'react';

const ChatWindow = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');

    const handleSendMessage = () => {
        if (inputMessage.trim()) {
            setMessages([...messages, { text: inputMessage, sender: 'user' }]);
            setInputMessage('');

            // Here you can add the logic to process the message with the AI
        }
    };

    const handleInputChange = (event) => {
        setInputMessage(event.target.value);
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleSendMessage();
        }
    };

    return (
        <div className="chat-interface">
            <div className="chat-history">
                {messages.map((message, index) => (
                    <div key={index} className={`message ${message.sender}`}>
                        {message.text}
                    </div>
                ))}
            </div>
            <div className="message-input">
                <input
                    type="text"
                    value={inputMessage}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message here..."
                />
                <button onClick={handleSendMessage}>Send</button>
            </div>
        </div>
    );
};

export default ChatWindow;


// const ChatWindow = () => {
//   const [messages, setMessages] = useState([]);
//   const [input, setInput] = useState("");

//   const handleInputChange = (event) => {
//     setInput(event.target.value);
//   };

//   const handleSend = () => {
//     setMessages([...messages, { text: input, sender: "user" }]);
//     setInput("");
//   };

//   return (
//     <div className="chat-window">
//       <div className="chat-history">
//         {messages.map((message, index) => (
//           <div key={index} className={`chat-message ${message.sender}`}>
//             <p>{message.text}</p>
//           </div>
//         ))}
//       </div>
//       <div className="chat-input">
//         <input
//           type="text"
//           value={input}
//           onChange={handleInputChange}
//           placeholder="Type your message here"
//         />
//         <button onClick={handleSend}>Send</button>
//       </div>
//     </div>
//   );
// };

// export default ChatWindow;
import React, { useState, useEffect } from 'react';
import ChatItem from './ChatItem';
import './App.css';
import { format } from 'date-fns';


import { FaThumbsUp, FaThumbsDown, FaCommentDots } from 'react-icons/fa';



const App = () => {
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/prompts/?skip=0&limit=100', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    })
    .then(response => response.json())
    .then(data => {
      // Sort the items by date in ascending order
      const sortedData = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setItems(sortedData);
    })
    .catch(error => console.error('Error fetching data:', error));
  }, []); // The empty array ensures this effect runs once on mount

  const formatDate = (dateString) => {
    return format(new Date(dateString), 'yyyy-MM-dd HH:mm');
  };

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-content">
        {items.map((item, index) => (
          <div
            key={item.id}
            className={`sidebar-item ${selectedItem && selectedItem.id === item.id ? 'selected' : ''}`}
            onClick={() => setSelectedItem(item)}
          >
            <div className="item-content">
              <div className="item-id">{index + 1}</div>
              <div className="item-date">{formatDate(item.created_at)}</div>
              <div className="item-prompt">{item.prompt.substring(0, 100)}</div>
              <div className="item-icons">
                {item.is_like === true && <FaThumbsUp />}
                {item.is_like === false && <FaThumbsDown />}
                {item.feedback && <FaCommentDots />}
              </div>
            </div>
          </div>
        ))}
        </div>
      </div>
      <div className="chat">
        {selectedItem ? (
          <ChatItem item={selectedItem} />
        ) : (
          <div className="select-message">Select an item to view the chat</div>
        )}
      </div>
    </div>
  );
};

export default App;

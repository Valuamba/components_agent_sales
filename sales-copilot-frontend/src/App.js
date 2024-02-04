import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-api-dom";
import SearchContainer from "./components/search/SearchContainer"; // Import your SearchContainer component
import './App.css';
import ChatWindow from './components/ChatWindow';
import EnquiryList from "./components/emails-panel/EnquiryList";
import ThreadHistory from "./components/chat-flow/ThreadHistory";

function App() {
  return (
    <Router>
      <div className="App">
        {/* ChatWindow can be displayed on every page */}

        {/* Routing logic */}
        <Routes>
          {/* Other routes can be added similarly */}
          <Route path="/" element={
            <div className="app-container">
            <EnquiryList />
            <ThreadHistory />
          </div>
          }/>
          <Route path="/chat" element={<ChatWindow />} />
          <Route path="/search" element={<SearchContainer />} />
          <Route path="/enquiry" element={<EnquiryList />} />
          <Route path="/service" element={<ThreadHistory />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

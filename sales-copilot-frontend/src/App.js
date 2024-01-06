import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SearchContainer from "./components/search/SearchContainer"; // Import your SearchContainer component
import './App.css';
import ChatWindow from './components/ChatWindow'; // Import your ChatWindow component

function App() {
  return (
    <Router>
      <div className="App">
        {/* ChatWindow can be displayed on every page */}

        {/* Routing logic */}
        <Routes>
          {/* Other routes can be added similarly */}
          <Route path="/chat" element={<ChatWindow />} />
          <Route path="/search" element={<SearchContainer />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

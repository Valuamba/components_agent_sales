import React from 'react';
import './SearchContainer.css'

const SearchContainer = () => {
  return (
    <div className="search-container">
      <div className="search-bar">
        <input type="text" placeholder="Enter search query" />
        <button>Search</button>
      </div>
      <div className="metadata">
        <p>Country: USA</p>
        <p>Page: 1</p>
      </div>
      <div className="search-results">
        {/* Map over your search results and render them here */}
      </div>
      <div className="highlighted-keywords">
        {/* Map over your highlighted keywords and render them here */}
      </div>
      <div className="selected-results">
        {/* Map over your selected results and render them here */}
      </div>
    </div>
  );
};

export default SearchContainer;

import React from 'react';
import './EnquiryList.css';


class EnquiryList extends React.Component {
  state = {
    enquiries: [
      { id: 1, date: '2024-01-01', title: 'Enquiry for Supply of Firetrol Battery Charger AS-2001 | AL RAMIZ', name: 'Ramees Khan | AREC' },
      // ... other enquiries
    ],
    searchQuery: '',
  };

  handleSearch = (event) => {
    this.setState({ searchQuery: event.target.value });
  };

  renderEnquiry = (enquiry) => {
    return (
      <div key={enquiry.id} className="enquiry-item">
        <div className="enquiry-date">{enquiry.date}</div>
        <div className="enquiry-title">{enquiry.title}</div>
        <div className="enquiry-name">{enquiry.name}</div>
      </div>
    );
  };

  render() {
    const filteredEnquiries = this.state.enquiries.filter((enquiry) =>
      enquiry.title.toLowerCase().includes(this.state.searchQuery.toLowerCase())
    );

    return (
      <div className="enquiry-panel">
        <input
          type="text"
          placeholder="Search"
          value={this.state.searchQuery}
          onChange={this.handleSearch}
          className="search-bar"
        />
        <div className="enquiry-list">
          {filteredEnquiries.map(this.renderEnquiry)}
        </div>
      </div>
    );
  }
}

export default EnquiryList;

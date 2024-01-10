import React, { useState } from 'react';
import './ToolResponseEditor.css'; // Make sure this file contains the styles provided in the previous message
import { FaTrashAlt } from 'react-icons/fa'; // You'll need to install react-icons or use an alternative method for the icon


// The PartInfo component provides inputs for editing a single part's details
const PartInfoEditor = ({ partInfo, onUpdate, onDelete }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    onUpdate({ ...partInfo, [name]: value });
  };

  return (
    <div className="part-info-editor">
      <input
        className="part-info-input"
        type="text"
        name="part_number"
        value={partInfo.part_number}
        onChange={handleChange}
        placeholder="Part Number"
      />
      <input
        className="part-info-input"
        type="text"
        name="brand"
        value={partInfo.brand}
        onChange={handleChange}
        placeholder="Brand"
      />
      <span className="part-info-id">{partInfo.id}</span>
      <button className="delete-part-button" onClick={() => onDelete(partInfo.id)}><FaTrashAlt /></button>

    </div>
  );
};

// The PartsListEditor component manages a list of PartInfo items
const PartsListEditor = () => {
  const [partsList, setPartsList] = useState([
    { part_number: 'PN001', brand: 'Brand A', id: 1 },
    { part_number: 'PN002', brand: 'Brand B', id: 2 },
    { part_number: 'PN003', brand: 'Brand C', id: 3 },
    { part_number: 'PN004', brand: 'Brand D', id: 4 },
    { part_number: 'PN005', brand: 'Brand E', id: 5 },
  ]);

  const handleAddPart = () => {
    setPartsList([...partsList, { part_number: '', brand: '', id: Date.now() }]);
  };

  const updatePart = (updatedPart) => {
    setPartsList(partsList.map((part) => (part.id === updatedPart.id ? updatedPart : part)));
  };

  const deletePart = (partId) => {
    setPartsList(partsList.filter((part) => part.id !== partId));
  };

  return (
    <div className="parts-list-editor">
      {partsList.map((partInfo) => (
        <PartInfoEditor key={partInfo.id} partInfo={partInfo} onUpdate={updatePart} onDelete={deletePart} />
      ))}
      <button className="add-part-button" onClick={handleAddPart}>Add Part</button>
    </div>
  );
};

export default PartsListEditor;

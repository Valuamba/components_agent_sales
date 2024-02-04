import React, { useEffect, useState } from 'react';
import './EmailAssistant.css'
import AssistantContainer from '../AssistantContainer';


const emailContent = "Dear Sir/Ma'am,\n\nWe’re currently enquiring for Supply of Firetrol Battery Charger AS-2001 (Type 3AB LL-1580) Qty: 01 No.\nPlease quote your best discounted prices and availability.\nI have attached a picture below for your reference.\n\nThanking you.\nBest Regards,\nRAMEES KHAN\nGeneral Manager\nM: +971-52-6927466 | E: ramees@arecuae.com\nAL RAMIZ ELECT. CONT. LLC\nA: Industrial Area 17, Sharjah - United Arab Emirates\nA: P.O Box: 96286, Sharjah\nT: +971-6-5356891\nE: info@arecuae.com | W: www.arecuae.com\n\nTransformers/Maintenance, Erection & Testing | Rewinding – Transformers, Motors & Generators | Cables – Laying, Termination, Testing – HT & LT | Distribution Boards – MDB, SMDB, DB | Generator Alternator – Repair & Maintenance, Bus Bar Modification & Testing | MV, LV Electrical Panel – Installation & Testing | Hiring of all types of Testing Instruments – Oil Filter Plants, Oil Tanks, Vacuum Pumps, Crimping Tools & Generators.\n\nDisclaimer: This e-mail and any attachments may contain confidential and privileged information. If you are not the intended recipient, please notify the sender immediately by return e-mail, delete this e-mail and destroy any copies. Any dissemination or use of this information by a person other than the intended recipient is unauthorized and may be illegal.";


const EmailComponent = ({ email }) => {
  return (
    <AssistantContainer name="Email Assistant">
        <div className='email-container'>
            <div className='email-details'>
                <div className="email-from-to-container">
                    <span className="email-from-to"><strong>From:</strong> Ramees Khan | AREC</span>
                    <span className="email-from-to"><strong>To:</strong> Recipient</span>
                </div>
                <div className='email-date-time'>
                    <span>2024-01-01 08:12PM</span>
                </div>
            </div>
                <div class="formatted-text">
                    {emailContent}
                </div>
        </div>
    </AssistantContainer>
  );
};


export default EmailComponent;

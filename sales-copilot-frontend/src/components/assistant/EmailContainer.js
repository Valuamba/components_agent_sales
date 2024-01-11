import React, { useEffect, useState } from 'react';
import './EmailContainer.css'


const EmailComponent = ({ email }) => {
  return (
    <dev className="email-container">
        <h1>Email Assistant:</h1>
        <div className='email-details'>
            <div className="email-from-to-container">
                <span className="email-from-to"><strong>From:</strong> Ramees Khan | AREC</span>
                <span className="email-from-to"><strong>To:</strong> Recipient</span>
            </div>
            <div className='email-date-time'>
                <span>2024-01-01 08:12PM</span>
            </div>
        </div>
        
        <div>
            <span>
            Dear Sir/Ma’am,
We’re currently enquiring for Supply of Firetrol Battery Charger AS-2001 (Type 3AB LL-1580) Qty: 01 No.
Please quote your best discounted prices and availability.
I have attached a picture below for your reference.Thanking you.
Best Regards,
RAMEES KHAN
General Manager
M: +971-52-6927466 | E: ramees@arecuae.com
AL RAMIZ ELECT. CONT. LLC
A: Industrial Area 17, Sharjah - United Arab Emirates
A: P.O Box: 96286, Sharjah
T: +971-6-5356891
E: info@arecuae.com | W: www.arecuae.com
Transformers/Maintenance, Erection & Testing | Rewinding – Transformers, Motors & Generators | Cables – Laying, Termination, Testing – HT & LT | Distribution Boards – MDB, SMDB, DB | Generator Alternator – Repair & Maintenance, Bus Bar Modification & Testing | MV, LV Electrical Panel – Installation & Testing | Hiring of all types of Testing Instruments – Oil Filter Plants, Oil Tanks, Vacuum Pumps, Crimping Tools & Generators.
Disclaimer: This e-mail and any attachments may contain confidential and privileged information. If you are not the intended recipient, please notify the sender immediately by return e-mail, delete this e-mail and destroy any copies. Any dissemination or use of this information by a person other than the intended recipient is unauthorized and may be illegal.


            </span>
        </div>
    </dev>
    
  );
};


const EmailContainer = () => {
  const [emails, setEmails] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onmessage = (event) => {
      const newEmail = JSON.parse(event.data);
      setEmails((prevEmails) => [...prevEmails, newEmail]);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="email-container">
      {emails.map((email, index) => (
        <EmailComponent key={index} email={email} />
      ))}
    </div>
  );
};

export {EmailContainer, EmailComponent};

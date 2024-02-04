-- Create the Deal table
CREATE TABLE Deal (
    deal_id INT NOT NULL,
    subject VARCHAR(255),
    country VARCHAR(255),
    domain VARCHAR(255),
    email VARCHAR(255),
    office_country VARCHAR(255),
    phone_number VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (deal_id)
);

-- Create the Feedback table
CREATE TABLE Feedback (
    id SERIAL PRIMARY KEY,
    feedback_types INT[],
    commentary TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Create the Message table
CREATE TABLE Message (
    id INT NOT NULL,
    peer_id UUID PRIMARY KEY,
    body TEXT,
    from_type SMALLINT CHECK (from_type IN (0, 1)),
    sent_at TIMESTAMPTZ NOT NULL,
    reply_to UUID REFERENCES Message(peer_id),
    deal_id INT REFERENCES Deal(deal_id),
    intents JSONB,
    feedback_id INT REFERENCES Feedback(id),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

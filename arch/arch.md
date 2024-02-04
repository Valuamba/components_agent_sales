

The are next participants at my service architecture:
- CRM
- sales-agi
- DB
- gpt-4

The flow overview:

1. The CRM send info about email (Body, Subject, Datetime, from, to) to sales-agi.
2. sales-agi logs this message to database.
3. sales-agi send request to classify email request.
4. gpt-4 returns classified message items:
    Item - array:
        - amount
        - brand name
        - part number
        - model
    Customer:
        - country
        - email
        - phone
        - office
5. sales-agi append this metadata to logged message
6. Loop - while each item would be handled
    6.1 Find note by brand name or part number at DB using semantic search
    6.2 Find prices and full brand name at google by query: "brand name + part number"
    6.3 Gather information and return
7. Log information about info from DB and google prices at message note DB

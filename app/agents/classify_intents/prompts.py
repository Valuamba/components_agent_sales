RESPONSE_FORMAT = """
Put the result at ```json``` format, like:
```json
[
    {
        "id": "<message_id>",
        "body": "<message body>",
        "from": "<message from>", //this should be one of two values: customer or manager
        "intents": [
            {
                "intent": "<main intent>",
                "sub_intent": "<sub intent>",
                "branch": "<branch>"
            }
        ]
    
    }
]
```
"""

INTENT_CLASSIFICATION_PROMPT = """
Please attach to each message in chat history tags, annotations, indexes, intents to better classification and search.
The message could have one or more intents.

[CHAT HISTORY]
{chat_history_str}
[/CHAT HISTORY]

For example, this message would have intents:
- customer: Hello So as not to waste precious time. We order devices from offer no. 440822 of friday, 29 september 2023 . 
If possible, please provide an additional discount on your purchase. Please confirm acceptance of our order. 
In the meantime, once you know what the transport cost will be, we will discuss how to deliver the parcel to us 
or whether we will collect it ourselves.

Example of intents/sub-intents/branches namings:
   - Order Processing -> Order Placement Confirmation -> Confirmation of Specific Offer
   - Order Processing -> Order Acceptance Confirmation -> Confirmation of Order Receipt and Acceptance
   - Pricing and Quotes -> Discount Inquiry -> Request for Additional Discount on Purchase
   - Pricing and Quotes -> Transport Cost Inquiry -> Inquiry About Delivery Costs
   - Delivery and Shipping -> Delivery Method Discussion -> Discussing Whether to Ship or Self-Collect
   - Delivery and Shipping -> Discussing Logistics -> Coordination of Transport and Delivery Options
"""

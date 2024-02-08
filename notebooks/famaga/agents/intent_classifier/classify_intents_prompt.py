RESPONSE_FORMAT = """
Put the result at ```json``` format, like:
```json
{
    "intents": [
        {
            "intent": "<main intent>",
            "sub_intent": "<sub intent>",
            "branch": "<branch>"
        }
    ]
}
```
Use only " brackets, not '.
"""

INTENT_CLASSIFICATIONI_INSTRUCTION_NAME = 'Intent Classification'

INTENT_CLASSIFICATION_PROMPT = """
Please classifiy for email message [EMAIL MESSAGE] all intent to better classification and search. You can use our default list of intents [INTENTS] or
if there is no suitable intent you can generate your own.

[EMAIL MESSAGE]
{email}
[/EMAIL MESSAGE]

[INTENTS]
{intents}
[/INTENTS]

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

REQUIRED_VALUES = ['email', 'intents']
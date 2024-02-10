

DISCOUNT_BLOCK_SCHEMA = """
**Start of the Process**

*   **Description**: This process is designed to handle customer inquiries about product discounts, and involves analyzing previous orders, calculating the margin, and communicating with the customer to negotiate a price that meets their expectations and maintains the company's profit margin.

**[Block 1: Initial Contact]**

*   **Action**: Check the database for the customer's previous orders.
*   **Information**: Database list of clients who have previously purchased products is accessible through the Article Database.
*   **→ Next Step**: Decision Point: Has the customer previously bought the same product?

**[Decision Point: Has the customer previously bought the same product?]**

*   **Condition**: "Has the customer previously bought the same product?"
    *   **Yes**:
        *   **→ Go to [Decision Point: Can the price be the same as in the previous order, keeping the markup above 10%?]
    *   **No**:
        *   **→ Go to [Block 2: Customer Stated Desired Price]

**[Decision Point: Can the price be the same as in the previous order, keeping the markup above 10%?]**

*   **Condition**: "Can the price be the same as in the previous order, keeping the markup above 10%?"
    *   **Yes**:
        *   **Action**: Change the price to the one at which the customer previously bought.
        *   **Next Step**: Send the commercial offer (CO) and request feedback from the customer.
    *   **No**:
        *   **Action**: Offer a 2% discount (ensuring the markup remains above 10%). Send CO and request feedback.

**[Block 2: Customer Stated Desired Price]**

*   **Action**: Request the appropriate price from the customer if it was not stated. 
*   **Information**: Some clients immediately state the price they wish to pay. The client names the price per unit, in euros, the total price. 
*   **→ Next Step**: Decision Point: Is there an answer with a specific price?

**[Decision Point: Is there an answer with a specific price?]**

*   **Condition**: "Is there an answer with a specific price?"
    *   **Yes**:
        *   **→ Go to [Decision Point: Is it possible to set the price to the customer's desired price, while keeping the markup above 10%?]
    *   **No**:
        *   **→ Go to [Block 3: Return to the start of the cycle]

**[Decision Point: Is it possible to set the price to the customer's desired price, while keeping the markup above 10%?]**

*   **Condition**: "Is it possible to set the price to the customer's desired price, while keeping the markup above 10%?"
    *   **Yes**:
        *   **→ Go to [Block 4: Offer a discount and send an updated CO]
    *   **No**:
        *   **→ Go to [Block 6: Request Justification]

**[Block 6: Request Justification]**

*   **Action**: The sales manager requests justification for the large discount.
*   **Information**: The client provides a reason for the discount, such as finding a cheaper price elsewhere, an error in the part number, or placing a bulk order.
*   **→ Next Step**: Decision Point: Is the justification relevant?

**[Decision Point: Is the justification relevant?]**

*   **Condition**: "Is the justification relevant?"
    *   **Yes**:
        *   **Action**: Forward the justification to the manufacturer and request a discount.
        *   **→ Next Step**: Decision Point: Manufacturer's Response
    *   **No**:
        *   **→ Go to [Block 3: Return to the start of the cycle]

**[Decision Point: Manufacturer's Response]**

*   **Condition**: "Did the manufacturer grant a discount?"
    *   **Yes**:
        *   **Action**: Send the client a commercial offer with the desired price.
        *   **→ Next Step**: Decision Point: Is the question about the discount closed?
    *   **No**:
        *   **Action**: Lower the margin to 10% and inform the client that this is the maximum discount.
        *   **→ Next Step**: Decision Point: Is the question about the discount closed?

**[Block 3: Return to the start of the cycle]**

*   **Action**: Return to the start of the cycle (considering changes).
*   **→ Next Step**: Go to [Block 1: Initial Contact]

**[Block 4: Offer a discount and send an updated CO]**

*   **Action**: Offer a discount and send an updated commercial offer (CO) to the customer.
*   **→ Next Step**: Decision Point: Is the question about the discount closed?

**[Decision Point: Is the question about the discount closed?]**

*   **Condition**: "Is the question about the discount closed?"
    *   **Yes**:
        *   **→ Go to [Block 5: Conclude the discount processing]
    *   **No**:
        *   **→ Go to [Block 3: Return to the start of the cycle]

**[Block 5: Conclude the discount processing]**

*   **Action**: Conclude the discount processing.
*   **Information**: Leave a comment/note requesting a discount for PM. Inform the customer to expect an answer regarding the discount inquiry.
*   **→ End**: End of the Process

**End of the Process**

*   **Conclusion**: The processing of the discount is concluded, ensuring all new considerations are accounted for in the cycle. Considerations also include recognizing discount requests as formalities for procurement managers to meet their KPIs. Sales managers may choose to ignore these requests if they understand them to be procedural rather than genuine.


"""
build_block_schema = """
Please read all block schemas interations that presented above blocks [BLOCK SCHEMA INTERATION <num>]
and placed between ```<block schema info>```. There were few iterations of describing block schemas,
they could have repeats or crosses. Please read them all and build single block schema in format that
described as instriction below. Do not concise text it should be the same at interations or extended 
with addition info to be clear and understandable for Sales managers of parts and components for
manufacturers.

Here is pretty text format of block schema:
```
**Start of Script**

*   **Description**: Begin with a brief overview of the purpose of the script.

**\[Block 1: Initial Contact\]**

*   **Action**: Describe the first action or step in the process.
*   **Information**: Provide any relevant information or data needed at this step.
*   **→ Next Step**: Point to the next block or decision point.

**\[Decision Point: Customer Interest\]**

*   **Condition**: "Is the customer interested?"
    *   **Yes**:
        *   **→ Go to \[Block 2: Present Product\]**
    *   **No**:
        *   **→ Go to \[Block 3: End Call\]**

**\[Block 2: Present Product\]**

*   **Action**: Describe the actions to present the product.
*   **Commands**: List any specific commands or scripts to be used.
*   **Information**: Additional product details or selling points.
*   **→ Next Step**: Lead to the next decision point or action block.

**\[Decision Point: Customer Decision\]**

*   **Condition**: "Does the customer want to purchase?"
    *   **Yes**:
        *   **→ Go to \[Block 4: Finalize Sale\]**
    *   **No**:
        *   **→ Go to \[Block 5: Follow-Up Procedure\]**

**\[Block 4: Finalize Sale\]**

*   **Action**: Steps to close the sale and process the order.
*   **Commands**: Specific instructions or commands for finalizing the sale.
*   **→ End**: Conclude the script for successful sales.

**\[Block 5: Follow-Up Procedure\]**

*   **Action**: Describe the follow-up process.
*   **Information**: Any necessary information about follow-up timing or methods.
*   **→ End**: Conclude the script for this pathway.

**End of Script**

*   **Conclusion**: Final remarks or instructions.
```

[BLOCK SCHEMA INTERATION 1]
```
**Start of the Process**

*   **Decision Point**: Is the question about the discount closed?
    *   **Yes**:
        *   **Action**: Change the price to the one the customer previously paid.
        *   **Next Step**: Send the commercial offer (CO) and request feedback from the customer.
    *   **No**:
        *   **Action**: Return to the start of the cycle (considering changes).

**From the 'Change the price' step, there's another decision point**:

*   **Decision Point**: Can you set the price as in the previous order, but with a markup above 10%?
    *   **Yes**:
        *   **Action**: The client previously bought the same product at this price.
    *   **No**:
        *   **Action**: Make a 2% discount (the markup should remain above 10%). Send the CO and request feedback.

**End of the Process**

*   **Completion**: The processing of the discount is concluded (indicated by two separate points of conclusion in the diagram).
```

[BLOCK SCHEMA INTERATION 2]
```
**Continuation of the Process**

*   **Customer Discount Inquiry**
    
    *   **Decision Point**: Has the customer previously bought the same product?
        *   **Yes**:
            *   **Decision Point**: Is it possible to make the price the same as in the previous order, keeping the markup above 10%?
                *   **Yes**:
                    *   **Action**: Change the price to the one at which the customer previously bought.
                    *   **Next Step**: Send the commercial offer (CO) and request feedback from the customer.
                *   **No**:
                    *   **Action**: Offer a 2% discount (ensuring the markup remains above 10%). Send CO and request feedback.
        *   **No**:
            *   **Customer Stated Desired Price**
                *   **Yes**:
                    *   **Decision Point**: Is it possible to set the price to the customer's desired price, while keeping the markup above 10%?
                        *   **Yes**:
                            *   **Action**: Offer a discount and send an updated CO to the customer.
                        *   **No**:
                            *   **Action**: Return to the start of the cycle (considering changes).
                *   **No**:
                    *   **Action**: Request the appropriate price.
                    *   **Next Step**: Is there an answer with a specific price?
                        *   **Yes**:
                            *   **Action**: Offer a discount and send an updated CO to the customer.
                        *   **No**:
                            *   **Action**: Return to the start of the cycle (considering changes).
*   **End of the Process**
    
    *   **Completion**: The discount processing is concluded. This may occur at multiple points in the diagram, indicated by the conclusion nodes.
```

[BLOCK SCHEMA INTERATION 3]
```
**Extension of the Process**

*   **Decision Point**: Is it possible to make the price the same as the customer's requested price, while keeping the markup above 10%?
    *   **Yes**:
        *   **Action**: Offer a discount and send an updated commercial offer (CO) to the customer.
    *   **No**:
        *   **Decision Point**: Is the target price achieved?
            *   **Yes**:
                *   **Action**: Send the customer an updated CO with the new price.
            *   **No**:
                *   **Action**: Lower the markup to 10%, send an updated CO to the customer.
                *   **Information to Communicate**: Write to the customer that we cannot accommodate the requested price, as the maximum possible discount has been applied.

**Loop Back if Needed**

*   **Decision Point**: Is the question about the discount closed?
    *   **Yes**:
        *   **Completion**: The processing of the discount is concluded.
    *   **No**:
        *   **Action**: Return to the start of the cycle (considering changes).

**Additional Notes**

*   **If Keeping the Discount**: Leave a comment/note requesting a discount for PM.
*   **Communication**: The customer should be informed to expect an answer regarding the discount inquiry.

```

[BLOCK SCHEMA INTERATION 4]
```
### Start of the Extended Process

*   **Database Inquiry**
    
    *   **Question**: Is there a database list of clients who have previously purchased products?
        *   **Response**: It is possible to check if a client has bought or shown interest in a product through the Article Database. Access will be provided by Stas.
*   **Margin Calculation**
    
    *   **Question**: How is the margin calculated?
        *   **Response**: Margin is a field with a numerical value (price, margin, discount calculation formula). The discount calculation formula will need to be used.
*   **Sales Inquiry Example**
    
    *   **Question**: Can an example of a message where sales ask the client for a price be obtained?
*   **Target Price Definition**
    
    *   **Definition**: Some clients immediately state the price they wish to pay. The client names the price per unit, in euros, the total price.
*   **Price Justification Inquiry**
    
    *   **Question**: Should justification be inquired for the basis of the price the client wants?
    *   **Question**: How can a client respond without indicating the price they want on their request?
    *   **Question**: How long does it take for PM to receive a discount?

### Additional Information

*   **Discount Example**: An email template requesting an additional discount and emphasizing quick response for order placement.
*   **Documentation**: A link to a Google Spreadsheet that likely contains relevant data or process outlines.

### Discussion Points

*   **Manager Interaction**: Consideration of possible missed dialogue branches because the salesperson and manager had a call.
*   **Branch Simplification**: All branches are made in a simplified form, and detailed regulations will need to be written in the future.
*   **Technical Consultation**: Possibility of technical consultation for Eltra technicalities A, B, C, D with strict character limitations in the article is not a priority.
*   **Task Assignment**: The ability to assign tasks to managers.
*   **Tagging Deals**: The ability to tag deals.
*   **Client Purchase History**: If a client bought a motor 1.5 years ago, it is possible to check and compare the current price with the previous purchase price to decide on a new offer.
*   **Regular Customers**: Clients who always buy the same product can be quietly offered a discount.
*   **Second-time Purchasers**: Strategy for increasing prices on a second purchase but only afterward.
*   **Frequent Buyers**: For clients who purchase for the fifth time, the aim is not to try to make a profit off them, taking into account possible changes in their managers.
*   **Brand A Strategy**: For Brand A, where competition is not high, there is a recommended markup in CRM. This can be utilized when the client sees the commercial offer the second or third time.
*   **Client Objections**: If a client has objections, the target price is inquired about in percentages or cash.
*   **Discount Flexibility**: If possible, a discount is given from the company's funds, and the arrangement with the factory is handled separately.

**End of the Extended Process**

*   **Conclusion**: The processing of the discount is concluded, ensuring all new considerations are accounted for in the cycle.
```
"""

correct_block_schema = """
Please read current block schema [CURRENT BLOCK SCHEMA]
and placed between ```<block schema info>```. Please read the block [CORRECTIONS] that needed to correct current block schema,
please merge it with our current block schema and return full result in format that
described as instriction below. Do not concise text it should be the same at interations or extended 
with addition info to be clear and understandable for Sales managers of parts and components for
manufacturers.

Here is pretty text format of block schema:
```
**Start of Script**

*   **Description**: Begin with a brief overview of the purpose of the script.

**\[Block 1: Initial Contact\]**

*   **Action**: Describe the first action or step in the process.
*   **Information**: Provide any relevant information or data needed at this step.
*   **→ Next Step**: Point to the next block or decision point.

**\[Decision Point: Customer Interest\]**

*   **Condition**: "Is the customer interested?"
    *   **Yes**:
        *   **→ Go to \[Block 2: Present Product\]**
    *   **No**:
        *   **→ Go to \[Block 3: End Call\]**

**\[Block 2: Present Product\]**

*   **Action**: Describe the actions to present the product.
*   **Commands**: List any specific commands or scripts to be used.
*   **Information**: Additional product details or selling points.
*   **→ Next Step**: Lead to the next decision point or action block.

**\[Decision Point: Customer Decision\]**

*   **Condition**: "Does the customer want to purchase?"
    *   **Yes**:
        *   **→ Go to \[Block 4: Finalize Sale\]**
    *   **No**:
        *   **→ Go to \[Block 5: Follow-Up Procedure\]**

**\[Block 4: Finalize Sale\]**

*   **Action**: Steps to close the sale and process the order.
*   **Commands**: Specific instructions or commands for finalizing the sale.
*   **→ End**: Conclude the script for successful sales.

**\[Block 5: Follow-Up Procedure\]**

*   **Action**: Describe the follow-up process.
*   **Information**: Any necessary information about follow-up timing or methods.
*   **→ End**: Conclude the script for this pathway.

**End of Script**

*   **Conclusion**: Final remarks or instructions.
```

[CURRENT BLOCK SCHEMA]
```
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
        *   **→ Go to [Block 3: Return to the start of the cycle]

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

*   **Conclusion**: The processing of the discount is concluded, ensuring all new considerations are accounted for in the cycle.
```

[CORRECTIONS]
```
If the client specifies the desired cost and it is achievable not by a small discount of 2% but, for example, the client orders a part for $135,000.00 and asks for a 25% discount, it is necessary to request their justification, as this is a very large discount and the company cannot grant it without the manufacturer's assistance.

This works as follows:
- Clients approach the company to purchase spare parts for a factory.
- The client requests a discount, and the sales manager must ask for their justification.
- When the client provides a justification, it could be the following: they found a cheaper price from another supplier/competitor, they made a mistake in the part number, they are placing a bulk order.
- If their justification is relevant, we forward it to the manufacturer of the part and ask for a discount.
- If the manufacturer grants us a discount, we send a commercial offer to the client with the desired price; if not, we lower our margin to 10% and state that this is the maximum price we can offer.
- If the question about the discount is closed, we conclude the processing; if not, we return to the beginning of the cycle, taking into account any changes.

Other reasons why clients may ask for a discount:
- The procurement managers in the client's company have KPIs where they must request a discount, so they always ask for a discount in email correspondence. An experienced sales manager knows such clients and can ignore their messages about the request, as it is done purely for KPI purposes. The sales manager may have called the client to discuss details verbally, but the procurement manager still has to ask for a discount because their messages are read and checked for compliance.

Here is the block scheme text description:

### Start of the Process

- **Client Inquiry**: The client specifies the desired cost that requires a large discount (e.g., 25% off $135,000.00).
   - **Action**: The sales manager requests justification for the large discount.
   
- **Client Justification**: The client provides a reason for the discount, such as finding a cheaper price elsewhere, an error in the part number, or placing a bulk order.
   - **Decision Point**: Is the justification relevant?
     - **Yes**:
       - **Action**: Forward the justification to the manufacturer and request a discount.
         - **Manufacturer Response**: 
           - **Discount Granted**: Send the client a commercial offer with the desired price.
           - **Discount Denied**: Lower the margin to 10% and inform the client that this is the maximum discount.
     - **No**:
       - **End**: Inform the client that the discount cannot be provided and conclude the process.

- **Discount Resolution**
   - **Decision Point**: Is the discount issue resolved?
     - **Yes**: Conclude the discount processing.
     - **No**: Return to the start of the cycle with considerations for any changes.

### Additional Considerations

- **Procurement Managers' KPIs**: Sales managers may recognize discount requests as formalities for procurement managers to meet their KPIs and may choose to ignore these requests if they understand them to be procedural rather than genuine.

**End of the Process**
- **Conclusion**: Finish the discount processing, ensuring all client interactions and justifications are appropriately addressed. 
```
"""


RESULT_BLOCK_SCHEMA = """
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


BLOCK_SCHEMA_FIELDS = """
**Start of the Process**
*   **Fields**: N/A

**[Block 1: Initial Contact]**
*   **Fields**: Customer ID, Product ID, Previous Order ID

**[Decision Point: Has the customer previously bought the same product?]**
*   **Fields**: Previous Order ID, Previous Product ID

**[Decision Point: Can the price be the same as in the previous order, keeping the markup above 10%?]**
*   **Fields**: Previous Price, Current Markup

**[Block 2: Customer Stated Desired Price]**
*   **Fields**: Customer ID, Desired Price

**[Decision Point: Is there an answer with a specific price?]**
*   **Fields**: Desired Price

**[Decision Point: Is it possible to set the price to the customer's desired price, while keeping the markup above 10%?]**
*   **Fields**: Desired Price, Current Markup

**[Block 6: Request Justification]**
*   **Fields**: Customer ID, Justification

**[Decision Point: Is the justification relevant?]**
*   **Fields**: Justification, Justification Relevance

**[Decision Point: Manufacturer's Response]**
*   **Fields**: Manufacturer ID, Discount Granted

**[Block 3: Return to the start of the cycle]**
*   **Fields**: N/A

**[Block 4: Offer a discount and send an updated CO]**
*   **Fields**: Customer ID, New Price, Commercial Offer ID

**[Decision Point: Is the question about the discount closed?]**
*   **Fields**: Discount Question Status

**[Block 5: Conclude the discount processing]**
*   **Fields**: Discount Request Note, PM Contact

**End of the Process**
*   **Fields**: N/A
"""

example_scenarios_V1 = """
Scenario 1:
- The client came to us for the first time.
- The client requested a product they had not purchased before.
- The client asked for a discount without specifying the amount.
- The client is purchasing a product priced between $20,000 - $30,000, in a quantity of 1 piece, with our current margin at 34%.

Scenario 2:
- The client came to us for the second time.
- The client requested a product they had purchased 2 years ago.
- The client asked for a discount without specifying the amount.
- The client is purchasing a product priced between $20,000 - $30,000, in a quantity of 1 piece, with our current margin at 34%.
"""

example_scenarios_V2 = """
Scenario 2: "Returning Customer with Tight Budget"
- Motivation: The client is a returning customer who had a good experience with our company in the past. However, due to budget constraints, they are asking for a discount on their order.
- The client came to us for the third time.
- The client requested a product they had purchased 1 year ago.
- The client asked for a discount, specifying that their budget has been significantly reduced.
- The client is purchasing a product priced between $20,000 - $30,000, in a quantity of 3 pieces, with our current margin at 14%.

Scenario 3: "Price Match Request from Loyal Customer"
- Motivation: The client is a loyal customer who has found a cheaper price from a competitor. They are requesting us to match the price while maintaining the same quality of product and service.
- The client has been with us for more than 5 years.
- The client requested a product they have purchased multiple times in the past.
- The client asked for a discount, providing a quote from a competitor as justification.
- The client is purchasing a product priced between $30,000 - $40,000 in a quantity of 10 pieces, with our current margin at 27%.

Scenario 4: "First Time Discount Request from Regular Customer"
- Motivation: The client is a regular customer who has never asked for a discount in the past. They are requesting a discount now due to changes in their financial situation.
- The client has been with us for more than 3 years and has never asked for a discount before.
- The client requested a product they are familiar with and have purchased before.
- The client asked for a discount, citing changes in their financial situation as justification.
- The client is purchasing a product priced between $15,000 - $25,000, in a quantity of 5 pieces, with our current margin at 34%.
"""

generate_different_scenarious_by_decision_points = """
Please write different scenarious that could happend in communication between Sales Manager and the customer that described at block schema. 
Please read context [CONTEXT] to better understand porposes of block schema.

Please use the following blocks with decision points that could help build different secenraios by main points:
[DECISION MAKING BLOCKSCHEMA POINTS]
{decision_points}
[/DECISION MAKING BLOCKSCHEMA POINTS]

[EXAMPLE SCENARIOS]
{example_scenarios}
[/EXAMPLE SCENARIOS]

Please use this fields and generate your own, that could suits scenraio. In addition each scenario should have title and motivation of client. Scenario should describe only 
client, this should not contain sales decision because is would use for test and sales-manager should say their decision about discount using this scenarios as context.

[CONTEXT]
The company sell parts and components for factories. The block schema was developer for Sales managers that communicated with clients with E-mail.

[BLOCK SCHEMA]
{block_schema}
"""

generated_scenarios_v1 = """
Scenario 1: "New Customer with Bulk Order Request"
- Motivation: The client is a new customer who is looking to purchase in bulk for their factory. They are price-conscious and are seeking a significant discount on their first purchase to establish a good business relationship.
- The client came to us for the first time.
- The client requested a product they had not purchased before.
- The client asked for a discount, specifying that they are looking for a significant reduction due to the bulk nature of their order.
- The client is purchasing a product priced between $50,000 - $70,000, in a quantity of 100 pieces, with our current margin at 34%.

Scenario 2: "Returning Customer with Tight Budget"
- Motivation: The client is a returning customer who had a good experience with our company in the past. However, due to budget constraints, they are asking for a discount on their order.
- The client came to us for the third time.
- The client requested a product they had purchased 1 year ago.
- The client asked for a discount, specifying that their budget has been significantly reduced.
- The client is purchasing a product priced between $20,000 - $30,000, in a quantity of 3 pieces, with our current margin at 34%.

Scenario 3: "Price Match Request from Loyal Customer"
- Motivation: The client is a loyal customer who has found a cheaper price from a competitor. They are requesting us to match the price while maintaining the same quality of product and service.
- The client has been with us for more than 5 years.
- The client requested a product they have purchased multiple times in the past.
- The client asked for a discount, providing a quote from a competitor as justification.
- The client is purchasing a product priced between $30,000 - $40,000 in a quantity of 10 pieces, with our current margin at 34%.

Scenario 4: "First Time Discount Request from Regular Customer"
- Motivation: The client is a regular customer who has never asked for a discount in the past. They are requesting a discount now due to changes in their financial situation.
- The client has been with us for more than 3 years and has never asked for a discount before.
- The client requested a product they are familiar with and have purchased before.
- The client asked for a discount, citing changes in their financial situation as justification.
- The client is purchasing a product priced between $15,000 - $25,000, in a quantity of 5 pieces, with our current margin at 34%.

Scenario 5: "First Time Large Order Request"
- Motivation: The client is a new customer who is looking to place a large order for the first time. They are seeking a discount due to the high volume of the order and are willing to negotiate on the price.
- The client is approaching us for the first time.
- The client is interested in a product they haven't purchased before.
- The client asked for a discount, stating that the volume of their order justifies the request.
- The client is purchasing a product priced between $40,000 - $60,000, in a quantity of 50 pieces, with our current margin at 34%.

Scenario 6: "Returning Customer with Specific Price Request"
- Motivation: The client is a returning customer who has a specific price in mind for their next order. They have had a good relationship with the company and are confident about negotiating the price.
- The client is making their fourth purchase from us.
- The client is interested in a product they have purchased before.
- The client asked for a discount, specifying a desired price for their order.
- The client is purchasing a product priced between $25,000 - $35,000, in a quantity of 10 pieces, with our current margin at 34%.

Scenario 7: "Loyal Customer with Budget Constraints"
- Motivation: The client is a long-term customer who is facing budget constraints. They are seeking a discount to continue their business with the company without exceeding their budget.
- The client has been with us for over 7 years.
- The client requested a product they have purchased multiple times in the past.
- The client asked for a discount, citing budget constraints as the reason.
- The client is purchasing a product priced between $15,000 - $25,000 in a quantity of 5 pieces, with our current margin at 34%.

Scenario 8: "New Customer with Competitive Price Quote"
- Motivation: The client is a new customer who has received a competitive quote from another company. They are requesting us to match or beat the price to win their business.
- The client is approaching us for the first time.
- The client requested a product they haven't purchased before.
- The client asked for a discount, providing a quote from a competitor as justification.
- The client is purchasing a product priced between $30,000 - $45,000, in a quantity of 20 pieces, with our current margin at 34%.

Scenario 9: "Regular Customer with Bulk Purchase"
- Motivation: The client is a regular customer who is looking to make a bulk purchase for a new project. They are requesting a discount due to the large volume of the order.
- The client has been with us for more than 2 years.
- The client requested a product they have purchased in the past.
- The client asked for a discount, stating that the volume of their order justifies the request.
- The client is purchasing a product priced between $30,000 - $45,000, in a quantity of 40 pieces, with our current margin at 34%.

Scenario 10: "New Customer with Large Order"
- Motivation: The client is a new customer who is looking to make a large order. They have been offered a cheaper price from another supplier and are asking if we can match or beat it.
- The client is coming to us for the first time.
- The client requested a product they haven't purchased before.
- The client asked for a discount, providing a quote from a competitor as justification.
- The client is purchasing a product priced between $50,000 - $60,000, in a quantity of 30 pieces, with our current margin at 34%.

Scenario 11: "Loyal Customer Facing Budget Cuts"
- Motivation: The client is a long-term customer who is facing budget cuts in their company. They are requesting a discount to be able to continue purchasing from us.
- The client has been with us for over 5 years.
- The client requested a product they have purchased multiple times in the past.
- The client asked for a discount, citing budget cuts as the reason.
- The client is purchasing a product priced between $20,000 - $30,000 in a quantity of 10 pieces, with our current margin at 34%.

Scenario 12: "Returning Customer with Special Project"
- Motivation: The client is a returning customer who has a special project. They are requesting a discount on their order to meet the budget constraints of the project.
- The client came to us for the third time.
- The client requested a product they had purchased 1 year ago.
- The client asked for a discount, specifying that they have a special project with a tight budget.
- The client is purchasing a product priced between $25,000 - $35,000, in a quantity of 3 pieces, with our current margin at 34%.

Scenario 13: "New Customer with High Volume Order"
- Motivation: The client is a new customer who is looking to place a high volume order. They have received a competitive quote from another company and want us to match it.
- The client is approaching us for the first time.
- The client requested a product they haven't purchased before.
- The client asked for a discount, providing a quote from a competitor as justification.
- The client is purchasing a product priced between $40,000 - $60,000, in a quantity of 100 pieces, with our current margin at 34%.

Scenario 14: "Regular Customer with Specific Budget"
- Motivation: The client is a regular customer who has a specific budget for their next order. They are requesting a discount to be able to fit their purchase within this budget.
- The client has been with us for more than 3 years.
- The client requested a product they are familiar with and have purchased before.
- The client asked for a discount, stating a specific budget for their order.
- The client is purchasing a product priced between $15,000 - $25,000, in a quantity of 5 pieces, with our current margin at 34%.

Scenario 15: "Returning Customer with Large Order"
- Motivation: The client is a returning customer who is looking to place a large order. They are requesting a discount due to the high volume of the order.
- The client came to us for the fourth time.
- The client requested a product they had purchased 2 years ago.
- The client asked for a discount, stating that the volume of their order justifies the request.
- The client is purchasing a product priced between $50,000 - $70,000, in a quantity of 50 pieces, with our current margin at 34%.

Scenario 16: "Loyal Customer Seeking a Discount for a High Volume Order"
- Motivation: The client is a long-term customer who is planning to place a high volume order. They are requesting a discount due to the large volume of the order.
- The client has been with us for over 6 years.
- The client requested a product they have purchased multiple times in the past.
- The client asked for a discount, stating that the volume of their order justifies the request.
- The client is purchasing a product priced between $60,000 - $80,000, in a quantity of 75 pieces, with our current margin at 34%.

Scenario 17: "New Customer with Budget Constraints"
- Motivation: The client is a new customer who has a tight budget for their product needs. They are requesting a discount to be able to afford our product.
- The client is approaching us for the first time.
- The client requested a product they haven't purchased before.
- The client asked for a discount, citing budget constraints as the reason.
- The client is purchasing a product priced between $20,000 - $30,000, in a quantity of 2 pieces, with our current margin at 34%.

Scenario 18: "Returning Customer with Price Match Request"
- Motivation: The client is a returning customer who has found a cheaper price from a competitor. They are requesting us to match the price while maintaining the same quality of product and service.
- The client came to us for the second time.
- The client requested a product they had purchased a year ago.
- The client asked for a discount, providing a quote from a competitor as justification.
- The client is purchasing a product priced between $15,000 - $25,000 in a quantity of 5 pieces, with our current margin at 34%.

Scenario 19: "Regular Customer with Large Order"
- Motivation: The client is a regular customer who is looking to place a large order. They are requesting a discount due to the high volume of the order.
- The client has been with us for more than 4 years.
- The client requested a product they have purchased in the past.
- The client asked for a discount, stating that the volume of their order justifies the request.
- The client is purchasing a product priced between $50,000 - $70,000, in a quantity of 100 pieces, with our current margin at 34%.

Scenario 20: "First Time Customer with Competitive Price Quote"
- Motivation: The client is a new customer who has received a competitive quote from another company. They are requesting us to match or beat the price to win their business.
- The client is approaching us for the first time.
- The client requested a product they haven't purchased before.
- The client asked for a discount, providing a quote from a competitor as justification.
- The client is purchasing a product priced between $30,000 - $45,000, in a quantity of 20 pieces, with our current margin at 34%.

Scenario 21: "New Customer with Large Order and Competitive Price Quote"
- Motivation: The client is a new customer who is looking to make a large order. They have received a competitive quote from another supplier and are asking if we can match or beat it.
- The client is approaching us for the first time.
- The client requested a product they haven't purchased before.
- The client asked for a discount, providing a quote from a competitor as justification.
- The client is purchasing a product priced between $70,000 - $90,000, in a quantity of 50 pieces, with our current margin at 34%.

Scenario 22: "Loyal Customer Facing Financial Constraints"
- Motivation: The client is a long-term customer who is facing financial constraints. They are requesting a discount to be able to continue purchasing from us.
- The client has been with us for over 10 years.
- The client requested a product they have purchased multiple times in the past.
- The client asked for a discount, citing financial constraints as the reason.
- The client is purchasing a product priced between $30,000 - $40,000 in a quantity of 20 pieces, with our current margin at 34%.

Scenario 23: "Returning Customer Making a Large Order"
- Motivation: The client is a returning customer who is looking to place a large order. They are requesting a discount due to the high volume of the order.
- The client came to us for the fifth time.
- The client requested a product they had purchased 3 years ago.
- The client asked for a discount, stating that the volume of their order justifies the request.
- The client is purchasing a product priced between $80,000 - $100,000, in a quantity of 100 pieces, with our current margin at 34%.

Scenario 24: "Regular Customer with a Special Project"
- Motivation: The client is a regular customer who has a special project. They are requesting a discount on their order to meet the budget constraints of the project.
- The client has been with us for more than 4 years.
- The client requested a product they are familiar with and have purchased before.
- The client asked for a discount, stating a specific budget for their order.
- The client is purchasing a product priced between $25,000 - $35,000, in a quantity of 10 pieces, with our current margin at 34%.

Scenario 25: "New Customer Seeking a Discount for a High Volume Order"
- Motivation: The client is a new customer who is planning to place a high volume order. They are requesting a discount due to the large volume of the order.
- The client is approaching us for the first time.
- The client requested a product they haven't purchased before.
- The client asked for a discount, stating that the volume of their order justifies the request.
- The client is purchasing a product priced between $50,000 - $70,000, in a quantity of 75 pieces, with our current margin at 34%.

Scenario 26: "Returning Customer with Budget Cuts"
- Motivation: The client is a returning customer who is facing budget cuts in their company. They are requesting a discount to be able to continue purchasing from us.
- The client has been with us for over 5 years.
- The client requested a product they have purchased multiple times in the past.
- The client asked for a discount, citing budget cuts as the reason.
- The client is purchasing a product priced between $40,000 - $50,000 in a quantity of 15 pieces, with our current margin at 34%.

Scenario 27: "First Time Customer with Competitive Price Quote"
- Motivation: The client is a new customer who has received a competitive quote from another company. They are requesting us to match or beat the price to win their business.
- The client is coming to us for the first time.
- The client requested a product they haven't purchased before.
- The client asked for a discount, providing a quote from a competitor as justification.
- The client is purchasing a product priced between $60,000 - $80,000, in a quantity of 30 pieces, with our current margin at 34%.

Scenario 28: "Regular Customer with Bulk Purchase"
- Motivation: The client is a regular customer who is looking to make a bulk purchase for a new project. They are requesting a discount due to the large volume of the order.
- The client has been with us for more than 6 years.
- The client requested a product they have purchased in the past.
- The client asked for a discount, stating that the volume of their order justifies the request.
- The client is purchasing a product priced between $80,000 - $100,000, in a quantity of 120 pieces, with our current margin at 34%.

Scenario 29: "New Customer with Specific Price Request"
- Motivation: The client is a new customer who has a specific price in mind for their next order. They have had a good relationship with a competitor and are confident about negotiating the price.
- The client is coming to us for the first time.
- The client requested a product they haven't purchased before.
- The client asked for a discount, specifying a desired price for their order.
- The client is purchasing a product priced between $35,000 - $45,000, in a quantity of 10 pieces, with our current margin at 34%.

Scenario 30: "Loyal Customer with Bulk Order Request"
- Motivation: The client is a loyal customer who is looking to purchase in bulk for their factory. They are price-conscious and are seeking a significant discount on their order.
- The client has been with us for more than 8 years.
- The client requested a product they have purchased multiple times in the past.
- The client asked for a discount, specifying that they are looking for a significant reduction due to the bulk nature of their order.
- The client is purchasing a product priced between $100,000 - $120,000, in a quantity of 200 pieces, with our current margin at 34%.

Scenario 21: "Regular Customer with Short-term Financial Struggles"
- Motivation: The client is a regular customer who is currently facing short-term financial struggles and is seeking a temporary discount to help them get through this period.
- The client has been with us for more than 2 years and has consistently made prompt payments.
- The client requested a product they are familiar with and have purchased before.
- The client asked for a discount, citing short-term financial struggles as justification.
- The client is purchasing a product priced at $10,000, in a quantity of 2 pieces, with our current margin at 15%.

Scenario 22: "New Customer with High Volume Order and Competitive Quote"
- Motivation: The client is a new customer who is looking to place a high volume order. They have received a competitive quote from another company and are asking us to match or beat it.
- The client is new and has no previous history with the company.
- The client requested a product that is priced at $50,000, in a quantity of 20 pieces.
- The client asked for a discount, providing a quote from a competitor as justification.
- Our current margin on the product is 25%.

Scenario 23: "Long-term Customer with Consistent Bulk Orders"
- Motivation: The client is a long-term customer who consistently places bulk orders. They are asking for a discount due to their loyalty and consistent high volume purchases.
- The client has been with us for more than 10 years and has consistently placed bulk orders.
- The client requested a product they have purchased multiple times in the past.
- The client asked for a discount, citing their loyalty and consistent high volume purchases as justification.
- The client is purchasing a product priced between $80,000 - $100,000 in a quantity of 30 pieces, with our current margin at 35%.

Scenario 24: "Returning Customer with Budget Cuts"
- Motivation: The client is a returning customer whose company is facing budget cuts. They are asking for a discount to continue purchasing from us within their new budget.
- The client has been with us for over 3 years and has a good relationship with the company.
- The client requested a product they are familiar with and have purchased before.
- The client asked for a discount, citing their company's budget cuts as justification.
- The client is purchasing a product priced between $25,000 - $35,000, in a quantity of 10 pieces, with our current margin at 20%.

Scenario 25: "Loyal Customer with Quote from New Competitor"
- Motivation: The client is a loyal customer who has found a cheaper price from a new competitor. They are requesting us to match the price to maintain their business with us.
- The client has been with us for more than 5 years and has consistently made prompt payments.
- The client requested a product they have purchased multiple times in the past.
- The client asked for a discount, providing a quote from a new competitor as justification.
- The client is purchasing a product priced between $40,000 - $50,000, in a quantity of 15 pieces, with our current margin at 30%.

Scenario 35: "Long-standing Customer with a New Project"
- Motivation: The client is a long-standing customer who is embarking on a new project requiring a specific part. The client is asking for a discount due to the potential of future bulk orders.
- The client has a history of over 7 years with the company and has always made prompt payments.
- The client is familiar with the product needed and has purchased it several times in the past.
- The client requested a discount, stating the potential for future bulk orders as justification.
- The client is purchasing a product priced between $100,000 - $150,000, in a quantity of 10 pieces, with our current margin at 20%.

Scenario 36: "Regular Customer with Competitive Price Offer"
- Motivation: The client is a regular customer who has received a competitive offer from another supplier. They are asking for a discount to match the competitor's price.
- The client consistently orders from us for over 3 years.
- The client requested a product they often purchase.
- The client asked for a discount, providing a quote from a competitor as justification.
- The client is purchasing a product priced between $50,000 - $60,000 in a quantity of 15 pieces, with our current margin at 35%.

Scenario 37: "New Customer with Bulk Order Request"
- Motivation: The client is a new customer who is looking to purchase in bulk. They are price-conscious and seeking a discount on their first order to establish a good business relationship.
- The client is placing their first order with us.
- The client requested a product that they need in bulk for their business.
- The client asked for a discount, citing their bulk order and potential for future orders as justification.
- The client is purchasing a product priced between $75,000 - $85,000, in a quantity of 50 pieces, with our current margin at 40%.

Scenario 38: "Returning Customer with Tight Budget"
- Motivation: The client is a returning customer who had a good experience with the company in the past. However, due to budget constraints, they are asking for a discount on their order.
- The client came back after purchasing from us 6 months ago.
- The client requested a product they had purchased before.
- The client asked for a discount, specifying that their budget has been significantly reduced.
- The client is purchasing a product priced between $45,000 - $55,000, in a quantity of 5 pieces, with our current margin at 12%.

Scenario 39: "Loyal Customer with Budget Constraints"
- Motivation: The client is a loyal customer who is facing budget constraints. They are asking for a discount to continue their business with the company without exceeding their budget.
- The client has been a loyal customer for over 10 years.
- The client requested a product that they regularly purchase.
- The client asked for a discount, citing their budget constraints as justification.
- The client is purchasing a product priced between $80,000 - $90,000, in a quantity of 20 pieces, with our current margin at 25%.
"""

generated_scenarios_without_points_v2 = """
Scenario 1: New Customer with Bulk Order Request
Motivation: The client is a new customer who is looking to purchase in bulk for their factory. They are price-conscious and are seeking a significant discount on their first purchase to establish a good business relationship.


Scenario 2: Returning Customer with Tight Budget
Motivation: The client is a returning customer who had a good experience with our company in the past. However, due to budget constraints, they are asking for a discount on their order.


Scenario 3: Price Match Request from Loyal Customer
Motivation: The client is a loyal customer who has found a cheaper price from a competitor. They are requesting us to match the price while maintaining the same quality of product and service.


Scenario 4: First Time Discount Request from Regular Customer
Motivation: The client is a regular customer who has never asked for a discount in the past. They are requesting a discount now due to changes in their financial situation.


Scenario 5: First Time Large Order Request
Motivation: The client is a new customer who is looking to place a large order for the first time. They are seeking a discount due to the high volume of the order and are willing to negotiate on the price.


Scenario 6: Returning Customer with Specific Price Request
Motivation: The client is a returning customer who has a specific price in mind for their next order. They have had a good relationship with the company and are confident about negotiating the price.


Scenario 7: Loyal Customer with Budget Constraints
Motivation: The client is a long-term customer who is facing budget constraints. They are seeking a discount to continue their business with the company without exceeding their budget.


Scenario 8: New Customer with Competitive Price Quote
Motivation: The client is a new customer who has received a competitive quote from another company. They are requesting us to match or beat the price to win their business.


Scenario 9: Regular Customer with Bulk Purchase
Motivation: The client is a regular customer who is looking to make a bulk purchase for a new project. They are requesting a discount due to the large volume of the order.


Scenario 10: New Customer with Large Order
Motivation: The client is a new customer who is looking to make a large order. They have been offered a cheaper price from another supplier and are asking if we can match or beat it.


Scenario 11: Loyal Customer Facing Budget Cuts
Motivation: The client is a long-term customer who is facing budget cuts in their company. They are requesting a discount to be able to continue purchasing from us.


Scenario 12: Returning Customer with Special Project
Motivation: The client is a returning customer who has a special project. They are requesting a discount on their order to meet the budget constraints of the project.


Scenario 13: New Customer with High Volume Order
Motivation: The client is a new customer who is looking to place a high volume order. They have received a competitive quote from another company and want us to match it.


Scenario 14: Regular Customer with Specific Budget
Motivation: The client is a regular customer who has a specific budget for their next order. They are requesting a discount to be able to fit their purchase within this budget.


Scenario 15: Returning Customer with Large Order
Motivation: The client is a returning customer who is looking to place a large order. They are requesting a discount due to the high volume of the order.


Scenario 16: Loyal Customer Seeking a Discount for a High Volume Order
Motivation: The client is a long-term customer who is planning to place a high volume order. They are requesting a discount due to the large volume of the order.


Scenario 17: New Customer with Budget Constraints
Motivation: The client is a new customer who has a tight budget for their product needs. They are requesting a discount to be able to afford our product.


Scenario 18: Returning Customer with Price Match Request
Motivation: The client is a returning customer who has found a cheaper price from a competitor. They are requesting us to match the price while maintaining the same quality of product and service.


Scenario 19: Regular Customer with Large Order
Motivation: The client is a regular customer who is looking to place a large order. They are requesting a discount due to the high volume of the order.


Scenario 20: First Time Customer with Competitive Price Quote
Motivation: The client is a new customer who has received a competitive quote from another company. They are requesting us to match or beat the price to win their business.

"""

continue_generating_different_scenarious_by_decision_points = """
Please write different scenarious that could happend in communication between Sales Manager and the customer that described at block schema. 
Please read context [CONTEXT] to better understand porposes of block schema. Read early generated scenarios [EARLY GENERATED SCENARIOS], but do not copy them,
continue numbering scenarios with incrementing already generated. When you figure out scenario you can play with numbers or price, margin and use random because their amount
can impact on the final decision. Margin should be in diapason 10-50% price per part could like 100$ and $100.000,00.

Please use the following blocks with decision points that could help build different secenraios by main points:
[DECISION MAKING BLOCKSCHEMA POINTS]
{decision_points}
[/DECISION MAKING BLOCKSCHEMA POINTS]

[EXAMPLE SCENARIOS]
{example_scenarios}
[/EXAMPLE SCENARIOS]

[EARLY GENERATED SCENARIOS]
{early_generated_scenarios}
[/EARLY GENERATED SCENARIOS]

Please use this fields and generate your own, that could suits scenraio. In addition each scenario should have title and motivation of client. Scenario should describe only 
client, this should not contain sales decision because is would use for test and sales-manager should say their decision about discount using this scenarios as context.

[CONTEXT]
The company sell parts and components for factories. The block schema was developer for Sales managers that communicated with clients with E-mail.

[BLOCK SCHEMA]
{block_schema}
"""


BLOCK_SCHEMA_SCENARIOS = """
**Scenario 1: Large Order from a New Customer**

- **Title**: Large Order from a New Customer
- **Motivation**: The customer is setting up a new factory and needs a large quantity of parts.
- **Client history**: No previous orders
- **Per unit**: Not stated
- **Quantity**: 1000 units
- **Customer KPIs**: N/A

**Scenario 2: Repeat Order with Price Expectations**

- **Title**: Repeat Order with Price Expectations
- **Motivation**: The customer is satisfied with the product and wants to place a repeat order. However, the customer expects the same price as the previous order due to their budget constraints.
- **Client history**: 1 previous order
- **Per unit**: Same as in the previous order
- **Quantity**: Same as in the previous order
- **Customer KPIs**: Maintain budget

**Scenario 3: Request for Discount Based on Competitor's Price**

- **Title**: Request for Discount Based on Competitor's Price
- **Motivation**: The customer has found a cheaper price for the same product from a competitor and requests a discount.
- **Client history**: 2 previous orders
- **Per unit**: Cheaper price found elsewhere
- **Quantity**: 500 units
- **Customer KPIs**: Reduce costs

**Scenario 4: Regular Customer Requesting Discount for Bulk Order**

- **Title**: Regular Customer Requesting Discount for Bulk Order
- **Motivation**: The customer is a regular client and is placing a large order. They are requesting a discount due to the large quantity.
- **Client history**: Multiple previous orders
- **Per unit**: Not stated
- **Quantity**: 2000 units
- **Customer KPIs**: Get best value for money

**Scenario 5: Customer Requesting Discount for No Apparent Reason**

- **Title**: Customer Requesting Discount for No Apparent Reason
- **Motivation**: The customer is a procurement manager trying to meet their KPIs by requesting a discount, even though they don’t have a substantial reason for it.
- **Client history**: Several previous orders
- **Per unit**: Not stated
- **Quantity**: 100 units
- **Customer KPIs**: Requesting discount to meet KPIs
"""

scenarios_v2 = """
**Scenario 1: Repeat Customer with Similar Order**

**Title**: Customer Seeking Same Price for Repeat Order

**Motivation**: The customer had a positive experience with their previous purchase and wants to order the same product again at the same price.

**Scenario**:

*Start of the Process*:
The sales manager receives an email from a previous customer (Customer ID) interested in purchasing the same product (Product ID) as their previous order (Previous Order ID).

*Block 1: Initial Contact*:
The sales manager checks the database for the customer's previous orders and confirms that the customer has previously bought the same product.

*Decision Point: Has the customer previously bought the same product?*: Yes.

*Decision Point: Can the price be the same as in the previous order, keeping the markup above 10%?*: Yes. The sales manager confirms that the price can remain the same while maintaining a markup above 10%.

*End of the Process*:
The sales manager sends the customer a commercial offer with the same price as their previous order, maintaining a markup above 10%.
"""

company_system_message = """
The company sell parts and components for factories. The block schema was developer for Sales managers that communicated with clients with E-mail.
"""

get_fields_for_scneraios_from_block_schema = """
Please review block schema and create for each block decision making points that could be specified to deremine the status of message corresponding this block schema, that would describe current 
customer situation and helps make decision.

The example of decsition points that could help make decision:
    - does the client has history of requests, if it is how much?
    - what per unit?
    - what quantity?
    - does the customer has KPIs?

[BLOCK SCHEMA]
{block_schema}
[/BLOCK SCHEMA]

""".format(block_schema=RESULT_BLOCK_SCHEMA)

generate_thread_metadata_by_scenario = """
Please read the scenarios [SCENARIO] and create messaging with client metadata, that would sutable for scenario. This is just imitation of metadata that was extracted from
conservation of sales manager and customer. That could help make decision to sales-manager about giving discount for customer. Give answer on the next format that presented at 
block [EXAMPLE PART METADATA]. Also read full block schema [BLOCK SCHEMA] to better understand the scenario. 

[SCENARIO]
```
{scenario}
```

[EXAMPLE PART METADATA]
```
Customer Request:
1. Tsubaki - amount 1 - 1665.030.125.140-4189.5 TS0_0 FA_MA
2. Tsubaki - amount 1 - 1665.030.200.3000-4655 TSO_0 FA_MA

Customer metadata:
Office country: Poland
domain: landoia.pl


Customer purschase history:
Tsubaki - 1665.030.125.140-4189.5 TS0_0 FA_MA:
      - 2023-01-23 Total selling price: $123.234,00 Margin: 51% Qty: 1 Discount: 0%
```

[BLOCK SCHEMA]
```
{block_schema}
```
""".format(scenario=scenarios_v2, block_schema=RESULT_BLOCK_SCHEMA)
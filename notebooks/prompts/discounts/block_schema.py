build_block_schema = """
Please read all block schemas interations that presented above blocks [BLOCK SCHEMA INTERATION <num>]
and placed between ```<block adr info>```. There were few iterations of describing block schemas,
they could have repeats or crosses. Please read them all and build single block adr in format that
described as instriction below. Do not concise text it should be the same at interations or extended 
with addition info to be clear and understandable for Sales managers of parts and components for
manufacturers.

Here is pretty text format of block adr:
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
Please read current block adr [CURRENT BLOCK SCHEMA]
and placed between ```<block adr info>```. Please read the block [CORRECTIONS] that needed to correct current block adr,
please merge it with our current block adr and return full result in format that
described as instriction below. Do not concise text it should be the same at interations or extended 
with addition info to be clear and understandable for Sales managers of parts and components for
manufacturers.

Here is pretty text format of block adr:
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


generate_different_scenarious_by_decision_points = """
Please write different scenarious that could happend in communication between Sales Manager and the customer that described at block adr. 
Please read context [CONTEXT] to better understand porposes
of block adr.

Please use the following blocks with decision points that could help build different secenraios by main points:
[DECISION MAKING BLOCKSCHEMA POINTS]
{decision_points}
[/DECISION MAKING BLOCKSCHEMA POINTS]

[EXAMPLE SCENARIOS]
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
[/EXAMPLE SCENARIOS]

Please use this fields and generate your own, that could suits scenraio. In addition each scenario should have title and motivation of client. Scenario should only specify 
customer situation.

[CONTEXT]
The company sell parts and components for factories. The block adr was developer for Sales managers that communicated with clients with E-mail.

[BLOCK SCHEMA]
{block_schema}
""".format(block_schema=RESULT_BLOCK_SCHEMA)


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
The company sell parts and components for factories. The block adr was developer for Sales managers that communicated with clients with E-mail.
"""

get_fields_for_scneraios_from_block_schema = """
Please review block adr and create for each block decision making points that could be specified to deremine the status of message corresponding this block adr, that would describe current 
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
block [EXAMPLE PART METADATA]. Also read full block adr [BLOCK SCHEMA] to better understand the scenario. 

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
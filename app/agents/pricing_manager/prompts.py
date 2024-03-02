RESPONSE_FORMAT = """
**Use the following format of answer:**

Use this format if you are going throw block schema instruction tree:
Decision Point: the name of decision point, that you thought on
Task: if task was presented in Action
Observation: the conclusion about thoughts
... (this Thought/Decision Point/Observation can repeat N times)

Use this format if you need to complete action.
Action: the action that you are going to do

Task: the short task summary
Assignee: the employee that would carry out the task
Description: the task description
Input keys: the input keys that persisting at remote storag values of each could be used for task completion
Input: the input data at json format, like { "desired_price": "2432$"}
...(There could be multiple blocks with Tasks on different assignees at Action block. If action requires multiple tasks you need to list them
and then list `Action observation`. The inputs fields like Input keys and Input needed for task completion.)
Action observation: the result of the action
... (this Action/(Task/Assignee/Description/Input Keys/Input: can repeat Y times)/Action observation: can repeat N times)

Thought: I now know the final answer
Conclusion: the final observation about thoughts

DO NOT USE MARKDOWN FORMAT FOR RESPONSE.
"""


STOP = ['\nAction observation:', '\n\tAction observation:']

DISCOUNT_BLOCK_SCHEMA = """
**[Entrypoint: Discount Request from Customer]**
* **→ Go to [Condition: Has the customer previously purchased the same product?]**

*   **Condition**: "Has the customer previously purchased the same product?"
    *   **Yes**:
        *   **→ Go to [Condition: Do we have a justification for why the price changed?]
    *   **No**:
        *   **→ Do nothing

*   **Condition**: "Did the customer state their desired price?"
    *   **Yes**:
        *   **→ Go to [Condition: Do we have a justification for why the price changed?]
    *   **No**:
        *   **→ [Action: Request the walk-through price]**

*   **Condition**: "Is it possible to offer the price as in the previous order, maintaining a margin above 10?"
    *   **Yes**:
        *   **→ Go to [Action: Apply a discount and send the updated proposal to the customer]**
    *   **No**:
        *   End

*   **Condition**: "Is it possible to offer such a price while maintaining a margin of current deal above 10%?"
    *   **Yes**:
        *   **→ Go to [Condition: Do we have a justification for why the price changed?]
    *   **No**:
        *  **[Action: Inform the customer that we have contacted the manufacturer regarding a discount]**

*   **Condition**: "Is there a response with a specific price?"
    *   **Yes**:
        *   **→ Go to [Condition: "Is it possible to offer such a price while maintaining a margin above 10%?"]
    *   **No**:
        *   **→ Go to [Action: Apply a 2% discount, send the proposal, and request feedback]**

*   **Condition**: "Is the discount issue resolved?"
    *   **Yes**:
        *   **→ Go to [End]
    *   **No**:
        *   **→ Go to [Block schema start]**

*   **Condition**: "Is the target price achieved?"
    *   **Yes**:
        *   **→ Go to [Action: Apply a discount and send the updated proposal to the customer]**
    *   **No**:
	    * Lower the margin to 10%
	    * Reflect in the letter that the requested price cannot be achieved, this is the maximum possible discount.
        *   **→ Go to [Action: Apply a discount and send the updated proposal to the customer]**

**[Action: Inform the customer that we have contacted the manufacturer regarding a discount]**
* **Task #1**: Ask manufacturer about best price
    Assignee: Purchasing Manager
    Description: Ask manufacturer about desired discount with resend client justifications.

  **Task #2**: Notify the client that we ask manufacturer
    Assignee: Sales Manager
    Description: Say client that we went to manufacturer to get the best price.

**[Action: Apply a discount and send the updated proposal to the customer]**
* **Next step:** 
	* **→ [Condition: Is the discount issue resolved?]

**[Action: Request the walk-through price]**
* **Next step:** 
	* **→ [Condition: Is there a response with a specific price?]

**[Action: Apply a 2% discount, send the proposal, and request feedback]**
* **Next step:** 
	* **→ [Condition: Is the discount issue resolved?]

**[Action: Inform the customer that we have contacted the manufacturer regarding a discount]**
"""


PROMPT = """
You are Pricing Manager at company that supply clients with parts or components for manufacturers. Your responsibility is 
communicate with clients using email messages and negotiate about discount and pricing questions. Please make decision about discount or some action needed for this using 
discount block schema [BLOCK SCHEMA] as a intruction.

You need to gather all information about client and offer, this would help us to make decision about change offer 
with adding discount or smth else. But know you needed to just develop this client by block schema.

Do do this, please read client purchase history [CLIENT PURCHASE HISTORY] and client messaging history [CHAT HISTORY]. 
To better understand your client please read [CLIENT PROFILE]. When you do conclusion please specify particular data
that was taken from metrics, we data-driven approach and it would be very helpful.

{response_format}

Here is definition for each block:
*   **\[DEAL INFO\]** Block
    
    *   **Description**: This block contains the current financial details of a deal, including the margin, which is a critical indicator of profitability. It provides real-time insights into the financial health of the deal, making it a vital piece of information for sales managers and decision-makers.
*   **\[CLIENT PROFILE\]** Block
    
    *   **Description**: The Client Profile block summarizes key metrics about the client, such as engagement levels, preferences, and demographic information. This data helps in tailoring sales strategies and offers to better suit the client's needs, enhancing the chances of successful transactions.
*   **\[CLIENT PURCHASE HISTORY\]** Block
    
    *   **Description**: This section records the client's past purchases, presenting a history of transactions. Analyzing this data can reveal patterns and preferences, aiding in personalized marketing efforts and product recommendations.
*   **\[CHAT HISTORY\]** Block
    
    *   **Description**: The Chat History block captures the entire messaging history between the client and the sales or support team. This information is crucial for understanding the client's concerns, questions, and the context of past interactions, enabling better communication and service.
*   **\[BLOCK SCHEMA\]** (Assuming you're introducing a new block called "Block Schema")
    
    *   **Description**: The Block Schema contains the structure or layout of a specific block, possibly related to discounts or offers. This schema is essential for developers and managers to understand how data is organized and should be interpreted within the system.

The map of keys at storage:
    deal_info: [DEAL INFO]
    client_profile: [CLIENT PROFILE] 
    client_purchase_history: [CLIENT PURCHASE HISTORY] 
    chat_history: [CHAT HISTORY]

[DEAL INFO]
{deal_info}
[/DEAL INFO]

[CLIENT PROFILE]
{summarize_client_metrics}
[/CLIENT PROFILE]

[CLIENT PURCHASE HISTORY]
{purchase_history_str}
[/CLIENT PURCHASE HISTORY]

[CHAT HISTORY]\n
{messaging_history_str}
\n[CHAT HISTORY]

[BLOCK SCHEMA]
{discount_block_schema}
[/BLOCK SCHEMA]

"""
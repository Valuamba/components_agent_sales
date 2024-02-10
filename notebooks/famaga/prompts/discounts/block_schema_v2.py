BLOCK_SCHEMA_V2 = """
**[Actions]**

* Action 1: Retrieve client history
     Command: send a request to the database
     Assignee: Database Manager

Action: Retrieve the offer sent to the client

**[Decision Point: Offer Analysis]**
*   **Action:** Retrieve the purchase history of the product by all clients

*   **Condition:** "Has the price changed?"
    *   **Yes:**
        *   **→ Go to [Condition: Do we have a justification for why the price changed?]
    *   **No:**
        *   **→ Do nothing

*   **Condition:** "Do we have a justification for why the price changed?"
    *   **Yes:**
        *   **→ Go to Continue communication
    *   **No:**
        *   **→ Go to [Condition: Has the price changed to higher or lower?]

*   **Condition:** "Has the price changed to higher or lower?"
    *   **Higher:**
        *   **→ Go to [Decision Point: Analysis of the reasons for the price increase]**
    *   **Lower:**
        *   → **Error:** This does not happen
        *   → **Action:** Call operator

**[Decision Point: Analysis of part price volatility]**
*   **Action:** Retrieve the purchase history of the product

**[Decision Point: Client Interaction Analysis]**
*   **Action:** Retrieve the client's purchase history from the database

*   **Sub-decisions:** 
	*   **→ Go to [Decision Point: Part Analysis]
	*   **→ Go to [Decision Point: Determine client category]

*   **Condition:** "Has the client purchased the same product before?"
    *   **Yes:**
        *   **→ Go to [Decision Point: Analysis of price volatility in client's history]
    *   **No:**
        *   **→ Do nothing

**[Decision Point: Part Analysis]**
*   **Categories:**
	* The order of prices:
		* $100-$200
		* $200-$500
		* $500-$2000
		* $2000-$10,000
		* $10,000-$30,000
		* >$30,000

**[Decision Point: Determine client category]**
*   **Categories:**
	- On purchase frequency:
		- 1 month
		- 1-3 months
		- 3-6 months
		- 6-12 months
		- > 1 year
	- Total amount of purchases
	- Number of orders
	- Client rate

**[Decision Point: Analysis of price volatility in client's history]**
*   **Action:** Retrieve the purchase history of the product by the client

*   **Condition:** "Has the price changed?"
    *   **Yes:**
        *   **→ Go to [Condition: Do we have a justification for why the price changed?]
    *   **No:**
        *   **→ Do nothing

*   **Condition:** "Do we have a justification for why the price changed?"
    *   **Yes:**
        *   **→ Go to Continue communication
    *   **No:**
        *   **→ Go to [Condition: Has the price changed to higher or lower?]

*   **Condition:** "Has the price changed to higher or lower?"
    *   **Higher:**
        *   **→ Go to [Decision Point: Analysis of the reasons for the price increase]**
    *   **Lower:**
        *   → **Error:** This does not happen
        *   → **Action:** Call operator

**[Decision Point: Analysis of the reasons for the price increase]**
*   **Options:**
	- Sales made a mistake in the quote
	- Selling to the naive: the client is buying from us for the second time, and we try to raise the price betting on him not noticing
	- External factors:
		- demand increase
		- change in competitor's price
		- manufacturer's price increase
		- logistics
		- retailer's price increase
		- inflation/taxes
		- change in company pricing policy
	- Client context: we know the client, giving us the opportunity to use a trick and raise the price

"""
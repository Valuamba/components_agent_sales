import redis
from pydantic import BaseModel, Field
from typing import List, Optional, Type, Any
from core.actions.base import BaseAction
from core.models.action import Action, ActionMetadata, Metadata
from core.bot import TelegramBotClient
from repositories import TaskRepository
from services import OpenAIClient, LoggingService
from models.deal import AgentTask, StatusType, LLMRun
from utility import select_json_block


class DiscountDecision(BaseAction):
    def __init__(self,
                 openai_client: OpenAIClient,
                 task_repository: TaskRepository,
                 telegram_bot: TelegramBotClient,
                 logger: LoggingService,
                 redis_client: redis.Redis):
        super().__init__(task_repository, telegram_bot, logger, openai_client, redis_client)

    @classmethod
    def get_action_name(cls):
        return "discount_decision"

    def prepare_ui(self, output):
        return output

    def discount_decision(self, run: LLMRun, customer_data: str, current_deal_str: str, purchase_history_str: str) -> Action:
        prompt = f"""
Here is an instruction:

1. **Customer previously purchased THIS product:** Try to offer the same price as last time if profitability allows. If not, set a 12% margin and explain that the supplier's price has changed, and this is the maximum possible discount.

2. **Customer has NOT previously purchased THIS product but specified a desired price:** Offer a discount if the margin allows. Otherwise, set a 10% margin and explain that this is the maximum possible discount.

3. **Customer has NOT purchased THIS product and has NOT specified a desired price, BUT has purchased other products:**

   a) **If the margin was unchanged in previous deals** (the price in the initial offer equals the price in the final offer for the same quantity within one quotation): Refuse the discount.

   b) **If the margin changed in previous deals** (the price in the initial offer does not equal the price in the final offer for the same quantity within one quotation):

      - If the price in the final offer is higher: Ignore the case (this is due to the supplier's price increase while the customer was deciding).
      - If a discount was given previously: Offer a 2% discount.

4. **Customer has NEVER purchased before and has NOT specified a desired price:** Check the total number of customer deals.

   a) **First quotation for a large company:** Offer a 2% discount and ask for the desired price.

   b) **First quotation for a non-large company:** Refuse the discount.

   c) **More than 10 quotations without any sales:** Set a 10% margin. This customer is a candidate for the blacklist; if they do not buy even with the maximum discount, we will likely not work with them in the future.

   d) **Several quotations with request dates differing by +/- 2 days (likely one project):** Propose a discount if the customer buys multiple quotations at once. Do not specify the exact price but ask for the desired price and hand it over to the manager for manual processing.

Additionally, remember the outcomes:

   a) **In case of a FULL discount refusal:** If the customer still buys, continue to refuse discounts. If the customer does not buy, offer a 2% discount next time and ask for the desired price.

   b) **In case of offering a 2% discount:** If the customer buys, continue offering 2% where possible. If the customer does not buy, offer a 3% discount next time (if margin allows) and continue to find the "acceptable discount" from deal to deal.

Margin formula:
 \text{{Margin}} = 100 \times \left(1 - \frac{{\text{{Total Purchase Price}}{{\text{{Total Selling Price}}\right) 

# Customer data

{customer_data}

## Current deal

{current_deal_str}

## Purchase history

{purchase_history_str}

Please make decision

"""
        model = "gpt-4o"
        action_version = 1
        return self.execute_action_raw(run, prompt, model,  self.get_action_name(), action_version)

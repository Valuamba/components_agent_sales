import redis
from pydantic import BaseModel, Field
from typing import List, Optional, Type, Any
from core.actions.base import BaseAction
from core.models.action import Action, ActionMetadata, Metadata
from core.bot import TelegramBotClient
from models.deal import LLMRun
from repositories import TaskRepository
from services import OpenAIClient, LoggingService
from utils.cache import stored


class DiscountMessage(BaseModel):
    message: str
    sender: str  # customer or manager


class CustomerData(BaseModel):
    desired_discount_per: Optional[float] = None
    desired_price: Optional[float] = None
    is_specified_desired_price: bool
    is_customer_large_company: bool
    deals_without_purchase: Optional[int] = None
    deals_with_purchases: Optional[int] = None


def prettify_customer_data(customer_data: CustomerData) -> str:
    if customer_data.desired_discount_per is not None or customer_data.desired_price is not None:
        customer_data.is_specified_desired_price = True
    else:
        customer_data.is_specified_desired_price = False

    prettified_data = []

    if customer_data.desired_discount_per is not None:
        prettified_data.append(f"Desired Discount Percentage: {customer_data.desired_discount_per}")
    if customer_data.desired_price is not None:
        prettified_data.append(f"Desired Price: {customer_data.desired_price}")
    prettified_data.append(f"Is Specified Desired Price: {'Yes' if customer_data.is_specified_desired_price else 'No'}")
    prettified_data.append(f"Is Customer Large Company: {'Yes' if customer_data.is_customer_large_company else 'No'}")
    if customer_data.deals_without_purchase is not None:
        prettified_data.append(f"Deals Without Purchase: {customer_data.deals_without_purchase}")
    if customer_data.deals_with_purchases is not None:
        prettified_data.append(f"Deals With Purchases: {customer_data.deals_with_purchases}")

    return '\n'.join(prettified_data)

class DiscountChronologyResponse(BaseModel):
    discount_messages: List[DiscountMessage]
    metadata: CustomerData

class DiscountMetadata(BaseAction):
    def __init__(self,
                 openai_client: OpenAIClient,
                 task_repository: TaskRepository,
                 telegram_bot: TelegramBotClient,
                 logger: LoggingService,
                 redis_client: redis.Redis):
        super().__init__(task_repository, telegram_bot, logger, openai_client, redis_client)

    @classmethod
    def get_action_name(cls):
        return "discount_metadata"

    def prepare_ui(self, output):
        return prettify_customer_data(output.metadata)

    # @stored
    def get_discount_meta(self, run: LLMRun, conversation: str) -> Action:
        prompt = """
        You are Sales manager. Read a conversation between customer and manager and classify discount chronology discussion.

        Respond with array of messages where was mentioned or discussed discount.
        Respond with an empty string, if none is found

        ```txt
        $TXT
        ```

        Put the response into ```json``` format like this:
        ```json
        {
            "discount_messages": [
                {
                    "message": <message>,
                    "sender": <sender who sent the message> // customer or manager
                }
            ],
            "metadata": {
                "desired_discount_per": <float or null>,
                "desired_price": <float or null>,
                "is_specified_desired_price": <boolean>,
                "is_customer_large_company": <boolean>
            }
        }
        ```
        """.strip() + "\n"

        filled = prompt.replace("$TXT", conversation)

        model = "gpt-4o"
        action_version = 1
        return self.execute_action(run, filled, model, DiscountChronologyResponse, self.get_action_name(), action_version)
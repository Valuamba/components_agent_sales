import requests
from pydantic import BaseModel, UUID4
from typing import List
import enum


class FromType(enum.Enum):
    Manager = 0
    Customer = 1
    
class IntentModel(BaseModel):
    uuid: UUID4
    intent: str
    sub_intent: str
    branch: str

class MessageModel(BaseModel):
    uuid: UUID4
    id: int
    body: str
    from_type: FromType
    intents: List[IntentModel]

class DealMessagesResponse(BaseModel):
    deal_uuid: UUID4
    messages: List[MessageModel]


class AgentsAPIClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def upload_email_content(self, deal_id: int, html_content: str, subject: str):
        """
        Upload email content to the API.

        :param email_content: EmailContent object containing the email data
        :return: Response from the API
        """
        full_url = f"{self.base_url}/v1/upload-html/"
        response = requests.post(full_url, json={
            'deal_id': deal_id,
            'html_content': html_content,
            'subject': subject
        }
        , headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to upload email content: {response.status_code} - {response.text}")

    def handle_messages(self, deal_id: int, messages_html: str):
        """
        Upload email content to the API.

        :param email_content: EmailContent object containing the email data
        :return: Response from the API
        """
        full_url = f"{self.base_url}/v1/agent/handle_messages/"
        response = requests.post(full_url, json={
            'deal_id': deal_id,
            'messages_html': messages_html,
        }
        , headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to upload email content: {response.status_code} - {response.text}")

    def get_messages_with_intents(self, deal_id: int):
        """
        Fetch messages with intents by deal_id.

        :param deal_id: The unique identifier for the deal
        :return: Parsed response as a Pydantic model
        """
        full_url = f"{self.base_url}/v1/deals/{deal_id}/messages"
        response = requests.get(full_url, headers=self.headers)

        if response.status_code == 200:
            return DealMessagesResponse(**response.json())
        else:
            raise Exception(f"Failed to fetch messages: {response.status_code} - {response.text}")
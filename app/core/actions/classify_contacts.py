from pydantic import BaseModel, EmailStr
from typing import List, Optional

from abc import ABC
from typing import List, Optional

from pydantic.v1 import BaseModel

from core.models.action import Action, ActionMetadata, Data, Metadata
from models.deal import AgentTask, StatusType
from repositories import TaskRepository
from services import OpenAIClient, LoggingService
from utility import select_json_block


class Address(BaseModel):
    office_country: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    suite: Optional[str] = None

class Contact(BaseModel):
    office_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    addresses: Optional[List[Address]] = None

class SocialMedia(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None

class Person(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    contact: Optional[Contact] = None
    social_media: Optional[SocialMedia] = None
    sign: Optional[str] = None


class ClassifyContactsAction:
    def __init__(self,
                 openai_client: OpenAIClient,
                 task_repository: TaskRepository,
                 logger_service: LoggingService):
        self.openai_client = openai_client
        self.task_repository = task_repository
        self.logger = logger_service

    @classmethod
    def get_action_name(cls):
        return "classify_contacts"

    def create_completion(self) -> any:
        return {}

    def classify_contacts_details(self, run_id: int, message: str):
        model = 'gpt-4'
        action_version = 1

        actual_status = StatusType.InProgress
        prompt = f"""
 Please select contact details from client message and put them into ```json``` format.
    
    Besides the sender contacts info please select sign block from email message and put it on different key.
    Please mention that customer could have different offices on different countries.
    
    Message:
    ```
    {message}
    ```
    
    Example of response:
    ```json
    {{
      "name": "John Doe",
      "title": "Director of Sales",
      "company": "XYZ Corporation",
      "contact": {{
        "office_phone": "+123-456-7890",
        "mobile_phone": "+098-765-4321",
        "email": "johndoe@xyzcorp.com",
        "website": "www.xyzcorp.com",
        "addresses": [
          {{
            "office_country": "United Kingdom",
            "street": "16/18a Hull Road",
            "city": "Hessle",
            "state": "East Yorkshire",
            "postal_code": "HU13 0AH"
          }},
          {{
            "office_country": "United States",
            "street": "1041 South East 17th Street Causeway",
            "suite": "Suite 207",
            "city": "Fort Lauderdale",
            "state": "Florida",
            "postal_code": "33316"
          }}
        ]
      }},
      "social_media": {{
        "linkedin": "linkedin.com/company/xyz-corporation",
        "twitter": "@XYZCorp"
      }},
      "sign": "Best Regards\n, Kim Jong Un"
    }}
    ```
    """

        task = AgentTask(run_id=run_id, status=actual_status.name, action=self.get_action_name(), prompt=prompt)
        db_session = self.task_repository.session
        self.task_repository.create_task_for_deal(task)

        try:
            completion = self.openai_client.create_completion(
                model,
                [
                    {"role": "user", "content": prompt}
                ],
            )

            task.response = completion.content  # Store raw output
            db_session.commit()

            response_raw_json = select_json_block(completion.content)
            parsed_contacts = Person(**response_raw_json)

            actual_status = StatusType.Passed
            task.status = actual_status.name
            db_session.commit()

            return Action(
                action=ActionMetadata(
                    action_version=action_version,
                    action_name=self.get_action_name(),
                    action_id=task.task_id,
                    action_time=round(completion.completion_time_ms, 0),
                    action_status=actual_status.value,
                ),
                data=parsed_contacts,
                metadata=Metadata(
                    completion_cost_usd=round(completion.usage_cost_usd, 3),
                    completion_time_sec=round(completion.completion_time_ms, 0),
                    llm_model=completion.model,
                    raw_output=completion.content
                )
            )
        except Exception as e:
            self.logger.error(f"Failed to process action [{self.get_action_name()}]: {str(e)}")

            actual_status = StatusType.Failed
            task.status = actual_status.name
            task.error = str(e)
            db_session.commit()

            return Action(
                action=ActionMetadata(
                    action_version=1,
                    action_name=self.get_action_name(),
                    action_id=task.task_id,
                    action_time=None,
                    action_status=actual_status.value,
                ),
                error={'code': type(e).__name__, 'message': str(e)}
            )
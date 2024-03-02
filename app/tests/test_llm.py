from enum import Enum

import pytest
from pydantic import BaseModel

from pydantic import BaseModel, Field

from pydantic import BaseModel, Field
from typing import get_type_hints, List, Type, Union
import typing

# from utility import select_json_block


def generate_json_schema(cls: Type[BaseModel], indent: int = 0) -> str:
    base_indent = ' ' * (indent * 2)  # Base indentation for this level
    nested_indent = ' ' * ((indent + 1) * 2)  # Indentation for nested elements
    fields = cls.__fields__
    lines = [f"{base_indent}{{"]

    for field_name, field in fields.items():
        field_type = get_type_hints(cls)[field_name]
        origin = typing.get_origin(field_type)
        args = typing.get_args(field_type)

        if origin is not None and issubclass(origin, List):  # It's a generic with origin List
            item_type = args[0]
            if issubclass(item_type, BaseModel):
                nested_schema = generate_json_schema(item_type, indent + 2)  # Increase indent for nested model
                description = field.description or 'No description'
                lines.append(f'{nested_indent}"{field_name}": [')
                lines.append(nested_schema)
                lines.append(f'{nested_indent}] // {description},')
            else:
                description = field.description or 'No description'
                lines.append(f'{nested_indent}"{field_name}": "List[{item_type.__name__}]" // {description},')
        elif issubclass(field_type, BaseModel):  # Direct Pydantic model
            nested_schema = generate_json_schema(field_type, indent + 1)
            lines.append(f'{nested_indent}"{field_name}": {nested_schema},')
        else:
            description = field.description or 'No description'
            lines.append(f'{nested_indent}"{field_name}": "{field_type.__name__}" // {description},')

    if lines[-1].endswith(','):
        lines[-1] = lines[-1].rstrip(',')  # Remove trailing comma on the last line
    lines.append(f"{base_indent}}}")
    return '\n'.join(lines)


class MyCustomBaseModel(BaseModel):
    @classmethod
    def generate_json_schema(cls):
        return generate_json_schema(cls)


from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import json

class Intent(MyCustomBaseModel):
    intent: str = Field(..., description="The main intent of the message.")
    sub_intent: str = Field(..., description="A more specific aspect of the main intent.")
    branch: str = Field(..., description="The branch of service this intent relates to.")

class MyMessage(MyCustomBaseModel):
    id: str = Field(..., description="The unique identifier for the message.")
    body: str = Field(..., description="The main body of the message, without signature.")
    sign: str = Field(..., description="The signature of the message.")
    # from_: Literal['customer', 'manager'] = Field(..., alias='from', description="The originator of the message; either a customer or a manager.")
    intents: List[Intent] = Field(..., description="A list of intents associated with the message.")


class SomeRoot(MyCustomBaseModel):
    messages: List[str]


class AgentType(str, Enum):
    CLASSIFY_PARTS = "classify-parts"


class ChatOpenAI:
    def create_completion(self, messages, model, **kwargs):
        return 'kek'


class Action(BaseModel):
    description: str
    assignee: AgentType
    task: str

    llm: ChatOpenAI

    def __init__(self, task: str, description: str, assignee: AgentType, llm):
        super().__init__(task=task, description=description, assignee=assignee, llm=llm)


class MessagingHistoryWithIntents(MyCustomBaseModel):
    messages_with_intents: List[MyMessage]


class ClassifyIntentsAction(Action):

    @property
    def _response_type(self) -> MyCustomBaseModel:
        return MessagingHistoryWithIntents

    @property
    def _input_type(self):
        return SomeRoot

    @property
    def _executive_prompt(self) -> str:
        return "Some promot"

    def get_input_schema(self):
        return self._input_type.generate_json_schema()

    def get_output_schema(self) -> str:
        return self._response_type.generate_json_schema()

    def get_response_format(self) -> str:
        return f"""
Put the result at ```json``` format, like:
```json
{self.get_output_schema()}
```
Please put new lines symbols if it suitable for context \\n at body and sign fields.
"""

    def invoke(self, input):
        massaging_history: SomeRoot = self.get_input_schema.parse_raw(input)

        messages_str = ''
        for idx, message in enumerate(massaging_history.messages):
            messages_str += f'Message {idx + 1}:\n```{message}```\n\n'

        response_completion = self.llm.create_completion([{"role": "user", "content":
            self._executive_prompt.format(chat_history_str=massaging_history) + '\n\n' + self.get_response_format()},
                                                          ], model='gpt-4', temperature=0.5)

        response_raw_json = '' #select_json_block(response_completion.content)
        return self._response_type.model_validate_json(response_raw_json)


# print(MessagingHistoryWithIntents.generate_json_schema())

@pytest.fixture
def action_fixture():
    task = "Sample Task"
    description = "Sample Description"
    assignee = AgentType.CLASSIFY_PARTS  # Adjust accordingly
    llm = ChatOpenAI()
    action = ClassifyIntentsAction(task=task, description=description, assignee=assignee, llm=llm)
    return action


# Now using pytest-mock's mocker fixture
def test_invoke_with_mocked_response_kek(mocker, action_fixture):
    # Use mocker to patch the create_completion method on the llm instance of ChatOpenAI
    mock_create_completion = mocker.patch.object(action_fixture.llm, 'create_completion', autospec=True)

    # Mock the response of create_completion
    mock_response = {
        "content": "{\"messages_with_intents\": [{\"message\": \"Test message\", \"intent\": \"Test intent\"}]}"
    }
    mock_create_completion.return_value = mock_response

    # Define your input
    input_data = SomeRoot(messages=["Hello, world!"]).json()

    # Invoke the method
    result = action_fixture.invoke(input_data)

    # Assertions to check if the result is as expected
    assert isinstance(result, MessagingHistoryWithIntents)
    assert len(result.messages_with_intents) > 0
    mock_create_completion.assert_called_once()  # Optional: Verify that the mock was called

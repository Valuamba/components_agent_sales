from pydantic import BaseModel, Field
from typing import Type, Any
from core.actions.base import BaseAction
from core.clients.google_sheet import GoogleSheet
from core.models.action import Action, ActionMetadata, Metadata
from core.bot import TelegramBotClient
from repositories import TaskRepository
from services import OpenAIClient, LoggingService
from models.deal import AgentTask, StatusType
from utility import select_json_block


class QueryBuilderOutput(BaseModel):
    query: str


class QueryBuilderAction(BaseAction):
    def __init__(self,
                 openai_client: OpenAIClient,
                 task_repository: TaskRepository,
                 telegram_bot: TelegramBotClient,
                 logger: LoggingService,
                 ghconv: GoogleSheet,
                 redis):
        super().__init__(task_repository, telegram_bot, logger, openai_client, redis)
        self.ghconv = ghconv

    @classmethod
    def get_action_name(cls):
        return "query_builder"

    def prepare_ui(self, output):
        return f"""
Query: {output.query}
"""

    def build_query(self, run_id: int, document_name, discount_messages: str, purchase_history: str) -> Action:
        sheet_data = self.ghconv.get_sheet_data(document_name)
        data = sheet_data

        # 1. Construct the Field Names section
        field_names_section = "#### 1. **Field Names**:\n"
        for i in range(len(data[0]) - 1):  # Skip the "instruction" column
            field_name = data[0][i]
            field_description = data[1][i]
            field_names_section += f"   - **\"{field_name}\"**: {field_description}\n"

        # 2. Construct the Possible Values section
        possible_values_section = "#### 2. **Possible Values**:\n"
        possible_values_section += "   - **TRUE**: The condition is met.\n"
        possible_values_section += "   - **FALSE**: The condition is not met.\n"
        possible_values_section += "   - **ANY**: The condition is not relevant or any value is acceptable.\n"

        # Combine sections to form the final instruction
        final_instruction = f"{field_names_section}\n{possible_values_section}"

        prompt = f"""
Build query for this input data.

Messages about discount at conversation:
{discount_messages}

{purchase_history}

### Querying Instructions:

{final_instruction}

#### 3. **Building a Query**:
   - Use only field names that listed at instruction with possible values
   - Use the `query()` method in Pandas to filter the table based on the conditions.
   - Format each condition as a string using the field names and their desired values.

#### 5. **Example Queries**:

```json
{{
    "query": "`Is margin still above 10%?` == 'TRUE' and `Is the same margin on product as previous?` == 'TRUE'"
}}
```
"""
        model = "gpt-4"
        action_version = 1
        return self.execute_action(run_id, prompt, model, QueryBuilderOutput, self.get_action_name(), action_version)

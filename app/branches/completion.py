from abc import abstractmethod

from agents import AgentType
from models.deal import StatusType, AgentTask
from repositories import TaskRepository
from services import OpenAIClient, LoggingService


class GPTCompletionResolver:

    def __init__(self, entity_to_response_map,
                openai_client: OpenAIClient,
                task_repository: TaskRepository,
                logger: LoggingService,
                 off_mapping: bool = False):
        self.entity_to_response_map = entity_to_response_map
        self.off_mapping = off_mapping
        self.openai_client = openai_client
        self.task_repository = task_repository
        self.logger = logger
        self.agents_logger = []

    def _create_completion(self, name: str, deal_id, messages, model, **kwargs):
        prompt = '\n\n'.join([f'{msg["role"]}:\n{msg["content"]}' for msg in messages])
        status: StatusType = None
        completion = None
        task_id = None  # Initialize task_id
        try:
            completion = self.openai_client.create_completion(
                model, messages, **kwargs
            )
            status = StatusType.Passed
        except Exception as e:
            self.logger.error(f"Failed to process completion: {str(e)}")
            status = StatusType.Failed

        finally:
            if status == StatusType.Passed and completion:
                task = AgentTask(
                    deal_id=deal_id,
                    prompt_tokens=completion.prompt_tokens,
                    output_tokens=completion.completion_tokens,
                    status=status,
                    prompt=prompt,
                    response=completion.content,
                    completion_cost=completion.usage_cost_usd,
                    agent_type=999
                )
            else:
                task = AgentTask(
                    deal_id=deal_id,
                    status=status,
                    prompt=prompt,
                    agent_type=999,
                )

            try:
                task_id = self.task_repository.create_task_for_deal(task)
                self.logger.info('Task was created', {'task_id': task_id})
            except Exception as db_error:
                self.logger.error(f"Failed to insert task into the database: {str(db_error)}")
                task_id = None  # Reset task_id to None if task creation fails

        return completion, task_id

    def create_completion(self, name: str, deal_id: str, messages, temperature,
                          model: str = 'gpt-4', **kwargs) -> str:
        self.logger.info(f'Start completion for {name}')
        mapped_response = self.entity_to_response_map.get(name, None)
        if mapped_response and not self.off_mapping:
            return mapped_response

        completion, task_id = self._create_completion(name, deal_id, messages, model=model, temperature=temperature, **kwargs)
        self.agents_logger.append({
            'step_name': name,
            'log': completion.content,
            'task_id': task_id
        })

        return completion.content
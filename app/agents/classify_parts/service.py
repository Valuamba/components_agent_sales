from agents.classify_parts.prompts import CLASSIFY_PARTS_PROMPT, DETAIL_CLASSIFICATION_EXAMPLES, FORMAT_RESPONSE, \
    SYSTEM_PROMPT
from core.bot import TelegramBotClient
from models import Deal
from models.deal import AgentTask, StatusType, PartInquiry, Message, FromType
from repositories import DetailInfoRepository, EmbeddingRepository
from repositories.deal_repository import DealRepository
from repositories.message import MessageRepository
from repositories.part_inquiry import PartInquiryRepository
from repositories.task import TaskRepository
from schemas.completion import ClassifiedMessageData
from schemas.v1.classify_part import ClassifyAgentResponse
from schemas.v1.part import ClassifyPartRequest
from services import OpenAIClient, LoggingService
from utility import select_json_block, content_hash


class ClassifyEmailAgent:
    def __init__(
            self,
            openai_client: OpenAIClient,
            logger: LoggingService,
            telegram_bot: TelegramBotClient,
            detail_info_repository: DetailInfoRepository,
            deal_repository: DealRepository,
            task_repository: TaskRepository,
            message_repository: MessageRepository,
            part_inquiry_repository: PartInquiryRepository,
            embeddings_repository: EmbeddingRepository,
    ):
        self.telegram_bot = telegram_bot
        self.openai_client = openai_client
        self.logger = logger
        self.detail_info_repository = detail_info_repository
        self.embeddings_repository = embeddings_repository
        self.deal_repository = deal_repository
        self.task_repository = task_repository
        self.message_repository = message_repository
        self.part_inquiry_repository = part_inquiry_repository

    async def classify_client_response(self, request: ClassifyPartRequest, model="gpt-4"):
        self.logger.info(f"Classify client request", {
            'deal_id': request.deal_id,
            'subject': request.subject,
            'from_client': request.from_client
        })
        prompt = CLASSIFY_PARTS_PROMPT.format(subject=request.subject, from_client=request.from_client,
            request_body=request.body, response_format=FORMAT_RESPONSE,
            few_shot_examples=DETAIL_CLASSIFICATION_EXAMPLES)

        deal = self.deal_repository.get_or_create_deal(request.deal_id, Deal(
                deal_id=request.deal_id,
                subject=request.subject))
        self.logger.info('Deal was or gotten created', {'deal_id': request.deal_id})

        actual_status = StatusType.InProgress
        task = AgentTask(status=actual_status.name, action='lead_classification', prompt=prompt, deal_id=request.deal_id)
        db_session = self.task_repository.session
        self.task_repository.create_task_for_deal(task)

        message_hash = content_hash(request.body)
        message = self.message_repository.append_message_to_chat_history_or_get(
            request.deal_id, message_hash, Message(
                deal_id=request.deal_id,
                from_type=FromType.Customer.value,
                body=request.body,
                hash=content_hash(request.body)
            ))

        self.logger.info('Message was appended', {'message_id': message.message_id, 'hash': message.hash})

        completion = None
        task_id = None
        order = None
        try:
            completion = self.openai_client.create_completion(
                model,
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0
            )

            task.response = completion.content  # Store raw output
            db_session.commit()

            classified_json_data = select_json_block(completion.content)
            order = ClassifyAgentResponse.model_validate(classified_json_data)

            task.status = StatusType.Passed.name
            task.prompt_tokens = completion.prompt_tokens
            task.output_tokens = completion.completion_tokens
            task.completion_cost = completion.usage_cost_usd
            task.action_time_ms = completion.completion_time_ms

            db_session.commit()

        except Exception as e:
            error_message = f"Failed to process completion: {str(e)}"
            self.logger.error(error_message)
            self.telegram_bot.notify_admins(error_message, **{
                'task_id': task.task_id,
                'deal_id': request.deal_id
            })

            task.status = StatusType.Failed.name
            task.error = str(e)
            db_session.commit()

        if order and completion:
            try:
                for part in order.parts:
                    part_inquiry = self.part_inquiry_repository.create_part_inquiry_for_deal(PartInquiry(
                        deal_id=request.deal_id,
                        brand_name=part.brand_name,
                        part_number=part.part_number,
                        amount=part.amount
                    ))

                order.deal_id = request.deal_id
                order.agent_task_id = task.task_id
                order.message_id = message.message_id
            except Exception as e:
                self.logger.error(f"Failed at parts classification: {str(e)}")
                self.telegram_bot.notify_admins(f"Failed at parts classification: {str(e)}", **{
                    'task_id': task.task_id,
                    'deal_id': request.deal_id
                })

                task.status = StatusType.Failed.name
                task.error = str(e)
                db_session.commit()

            return order, completion.usage_cost_usd
        return None, None


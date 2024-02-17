from agents.classify_parts.prompts import CLASSIFY_PARTS_PROMPT, DETAIL_CLASSIFICATION_EXAMPLES, FORMAT_RESPONSE, \
    SYSTEM_PROMPT
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
from utility import select_json_block


class ClassifyEmailAgent:
    def __init__(
            self,
            openai_client: OpenAIClient,
            logger: LoggingService,
            detail_info_repository: DetailInfoRepository,
            deal_repository: DealRepository,
            task_repository: TaskRepository,
            message_repository: MessageRepository,
            part_inquiry_repository: PartInquiryRepository,
            embeddings_repository: EmbeddingRepository,
    ):
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

        message_id = self.message_repository.append_message_to_deal(
            request.deal_id, Message(
                deal_id=request.deal_id,
                from_type=FromType.Customer.value,
                body=request.body,
            )
        )
        self.logger.info('Message was appended', {'message_id': message_id})

        classified_json_data = None
        completion = None
        task_id = None
        order = None
        status = None
        try:
            completion = self.openai_client.create_completion(
                model,
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )

            # Assuming `select_json_block` and `ClassifyAgentResponse.model_validate`
            # can raise exceptions if parsing fails or results are incorrect
            classified_json_data = select_json_block(completion.content)
            order = ClassifyAgentResponse.model_validate(classified_json_data)
            status = StatusType.Passed

        except Exception as e:
            # Log the error for debugging purposes
            self.logger.error(f"Failed to process completion: {str(e)}")
            status = StatusType.Failed

        finally:
            # Prepare task based on status
            if status == StatusType.Passed and classified_json_data and completion:
                task = AgentTask(
                    deal_id=request.deal_id,
                    prompt_tokens=completion.prompt_tokens,
                    output_tokens=completion.completion_tokens,
                    status=status,
                    prompt=prompt,
                    response=completion.content,
                    completion_cost=completion.usage_cost_usd,
                    agent_type=1
                )
            else:
                # Provide fallback values for failed cases or partial successes
                task = AgentTask(
                    deal_id=request.deal_id,
                    status=status,
                    prompt=prompt,
                    agent_type=1,
                    # Include fallback/default values for missing fields if necessary
                )

            # Insert task into the database
            try:
                task_id = self.task_repository.create_task_for_deal(task)
                self.logger.info('Task was created', {'task_id': task_id})
            except Exception as db_error:
                # Log database insertion failures, handling unexpected results or schema issues
                self.logger.error(f"Failed to insert task into the database: {str(db_error)}")
                # Consider handling this case (e.g., retry mechanism, alerting, etc.)

        if order and completion:
            for part in order.parts:
                part_inquiry = self.part_inquiry_repository.create_part_inquiry_for_deal(PartInquiry(
                    deal_id=request.deal_id,
                    brand_name=part.brand_name,
                    part_number=part.part_number,
                    amount=part.amount
                ))

            order.deal_id = request.deal_id
            order.agent_task_id = task_id
            order.message_id = message_id

            return order, completion.usage_cost_usd
        return None, None


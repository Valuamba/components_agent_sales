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
        prompt = CLASSIFY_PARTS_PROMPT.format(subject=request.subject, from_client=request.from_client,
            request_body=request.body, response_format=FORMAT_RESPONSE,
            few_shot_examples=DETAIL_CLASSIFICATION_EXAMPLES)

        deal = self.deal_repository.get_or_create_deal(request.deal_id, Deal(
                deal_id=request.deal_id,
                subject=request.subject))

        message = self.message_repository.append_message_to_deal(
            request.deal_id, Message(
                deal_id=request.deal_id,
                from_type=FromType.Customer.value,
                body=request.body,
            )
        )

        # self.logger.info(f"Classify prompt: {classify_prompt}")

        completion = self.openai_client.create_completion(
            model,
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        self.logger.info(
            f"Classification response: {completion.content}. Spent: {completion.usage_cost_usd}$"
        )

        classified_json_data = select_json_block(completion.content)
        order = ClassifiedMessageData.model_validate(classified_json_data)

        task = self.task_repository.create_task_for_deal(AgentTask(
            deal_id=request.deal_id,
            prompt_tokens=completion.prompt_tokens,
            output_tokens=completion.completion_tokens,
            status=StatusType.Passed,
            prompt=prompt,
            response=completion.content,
            completion_cost=completion.usage_cost_usd,
            agent_type=1
        ))

        for part in order.parts:
            part_inquiry = self.part_inquiry_repository.create_part_inquiry_for_deal(PartInquiry(
                deal_id=request.deal_id,
                brand_name=part.brand_name,
                part_number=part.part_number,
                amount=part.amount
            ))


        return order, completion.usage_cost_usd


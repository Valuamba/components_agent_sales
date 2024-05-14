import redis

from api.v2.api import Run, RunDetails, v2_group
from configs.config import AppSettings
from core.actions.discount.classify_discount_messages import ClassifyDiscountMessages
from core.actions.discount.discount_processing import DiscountProcessingAction
from core.actions.discount.document_selection import DocumentSelection, DocumentSelectionAction
from core.actions.discount.query_builder_action import QueryBuilderAction
from core.actions.discount.task_execution import TaskExecutionAction
from core.clients.famaga import FamagaClient
from core.clients.google_sheet import GoogleSheet

from typing import List
import re
import json

from typing import List

from fastapi import APIRouter, Depends
from fastapi.openapi.models import Response
from pydantic import BaseModel

from core.actions.classify_contacts import ClassifyContactsAction
from core.actions.classify_intents import ClassifyIntentsAction
from core.bot import TelegramBotClient
from core.dispatcher import Task, dispatch
from core.models.action import Action
from dependencies import get_run_repository, get_deal_repository, get_openai_client, get_task_repository, get_logger, \
    get_telegram_bot_client
from models.deal import LLMRun, StatusType, Deal
from repositories import DealRepository, TaskRepository
from repositories.run_repository import RunRepository
from services import OpenAIClient, LoggingService
from utils.html_messages_parser import get_messages_from_html_file, split_email_html_on_messages
from utils.sign import remove_sign_from_message

from utils.html_messages_parser import get_messages_from_html_file
import pandas as pd
import os

from configs.config import app_settings


discount = APIRouter()


def get_conversation_html(file_name: str):
    with open(f'./deals_html/discount_v3/{file_name}.html', 'r') as f:
        return f.read()


def parse_file_name(file_name: str):
    deal_id, message_id = file_name.split('_', 1)
    return deal_id, message_id


def get_conversation_messages(file_name: str) -> List[str]:
    return get_messages_from_html_file(f'./deals_html/discount_v3/{file_name}.html')


def messages_to_pretty_format(messages: List[str]):
    for idx, msg in enumerate(messages):
        print(f'Message: {len(messages) - idx}')
        print(f'```\n' + msg + '\n```\n\n')


def select_json_block(text: str):
    match = re.search(r"```json\n([\s\S]*?)\n```", text)
    if match:
        json_data = match.group(1)
    else:
        raise ValueError("No valid JSON data found in the string.")

    return json.loads(json_data)


def prepare_conversation_to_prompt(messages_from_latest):
    messages_str = ''
    for idx, msg in enumerate(messages_from_latest):
        messages_str += f'Message: {len(messages_from_latest) - idx}\n'
        if 'Offer-Nr.' in msg:
            messages_str += '<Offer from CRM>'
        messages_str += f'```\n' + msg + '\n```\n\n'
    return messages_str


def filter_messages(messages_from_latest, skip: int, lenght: int):
    return messages_from_latest[::-1][skip:skip + lenght][::-1]


class DiscountHandlingDto(BaseModel):
    run_uuid: str
    deal_id: str
    messages_html: str


class DiscountHandlingRawDto(BaseModel):
    run_uuid: str
    deal_id: str
    raw_text: str


@discount.post("/agent/discount/raw_text")
def make_decision_about_discount_raw(request: DiscountHandlingRawDto,
                                     openai_client: OpenAIClient = Depends(get_openai_client),
                                     logger: LoggingService = Depends(get_logger),
                                     telegram_bot: TelegramBotClient = Depends(get_telegram_bot_client),
                                     task_repository: TaskRepository = Depends(get_task_repository),
                                     run_repository: RunRepository = Depends(get_run_repository),
                                     deal_repository: DealRepository = Depends(get_deal_repository)
                                     ):
    redis_client = redis.Redis(host=app_settings.redis_host, port=6379, db=1)
    deal = deal_repository.get_or_create_deal(request.deal_id, Deal(deal_id=request.deal_id))

    run = run_repository.create_run(run=LLMRun(
        status=StatusType.InProgress.value,
        deal_id=deal.deal_id,
        uuid=request.run_uuid
    ))

    if app_settings.environment == 'local':
        project_root = '/Users/valuamba/projs/components_agent_sales/notebooks/famaga'

    else:
        project_root = os.environ.get('PYTHONPATH', os.getcwd())

    deal_id = deal.deal_id

    api_key = "YXBpZmFtYWdhcnU6RHpJVFd1Lk1COUV4LjNmdERsZ01YYlcvb0VFcW9NLw"
    session_id = "085qpt4eflu39a0dg7hjhr5mdu"
    client = FamagaClient(api_key, session_id)

    ghconv = GoogleSheet(
        spreadsheet='Famaga Knowledge Map',
        credentials_path=os.path.join(project_root, 'langchain-400510-06936d0d30b5.json'))

    classify_discount = ClassifyDiscountMessages(openai_client, task_repository, telegram_bot, logger, redis_client)
    document_selection = DocumentSelectionAction(openai_client, task_repository, telegram_bot, logger, redis_client)
    task_execution = TaskExecutionAction(openai_client, task_repository, telegram_bot, logger, ghconv, redis_client)
    query_builder = QueryBuilderAction(openai_client, task_repository, telegram_bot, logger, ghconv, redis_client)

    classify_result = classify_discount.classify_discount_messages(run, request.raw_text)

    discount_messages = ''
    for idx, msg in enumerate(classify_result.data):
        discount_messages += f'Message: {len(classify_result.data) - idx}\nSender: {msg['sender']}\n'
        discount_messages += f'```\n' + msg['message'] + '\n```\n\n'

    offer_info = client.list_offers_by_deal_id(deal_id)
    offer_id = offer_info['content'][0]['request']['id']
    client_id = offer_info['content'][0]['request']['firm']['id']

    purchase_history = client.get_client_purchase_history_formatted(client_id, int(deal_id))

    current_offer = client.list_current_offer_details(offer_id)

    document_selection_result = document_selection.document_selection(run,
                                          discount_messages=discount_messages,
                                          purchase_history=purchase_history,
                                          current_offer=current_offer)

    query_result = query_builder.build_query(run,
                              document_name=document_selection_result.data.document_name,
                              discount_messages=discount_messages,
                              purchase_history=purchase_history
                              )

    sheet_data = ghconv.get_sheet_data(document_selection_result.data.document_name)
    headers = sheet_data.pop(0)
    sheet_data.pop(0)
    df = pd.DataFrame(sheet_data, columns=headers)

    result = df.query(query_result.data.query)
    instruction = result['instruction'].iloc[0]

    task_execution_result = task_execution.execute_task(run,
                                instruction=instruction,
                                discount_messages=discount_messages,
                                purchase_history=purchase_history,
                                current_offer=current_offer
                                )

    run_data = Run(
        actions=[
            classify_result,
            document_selection_result,
            query_result,
            task_execution_result
        ],
        run=RunDetails(run_id=run.run_id),
        tasks=[
            Task(summary=task_execution_result.data.output)
        ]
    )

    return run_data


@discount.post("/agent/discount/html")
def make_decision_about_discount(request: DiscountHandlingDto,
                                 openai_client: OpenAIClient = Depends(get_openai_client),
                                 logger: LoggingService = Depends(get_logger),
                                 telegram_bot: TelegramBotClient = Depends(get_telegram_bot_client),
                                 task_repository: TaskRepository = Depends(get_task_repository),
                                 run_repository: RunRepository = Depends(get_run_repository),
                                 deal_repository: DealRepository = Depends(get_deal_repository)
                                 ):
    redis_client = redis.Redis(host=app_settings.redis_host, port=6379, db=1)
    deal = deal_repository.get_or_create_deal(request.deal_id, Deal(deal_id=request.deal_id))

    run = run_repository.create_run(run=LLMRun(
        status=StatusType.InProgress.value,
        deal_id=deal.deal_id,
        uuid=request.run_uuid
    ))

    if app_settings.environment == 'local':
        project_root = '/Users/valuamba/projs/components_agent_sales/notebooks/famaga'
        file_name = '410158_CAFidWpS2O2JN6fPtwQ0SiqdsSG+y9qDr0xEWeZj_c==rEhG62g@mail.gmail.com'
        deal_id, message_id = parse_file_name(file_name)
        messages = get_messages_from_html_file(f'/Users/valuamba/projs/components_agent_sales'
                                               f'/notebooks/famaga/deals_html/discount_v3/{file_name}.html')
        prepared_messages = filter_messages(messages, 8, 3)
        prepared_conversation = prepare_conversation_to_prompt(prepared_messages)
    else:
        project_root = os.environ.get('PYTHONPATH', os.getcwd())
        deal_id = deal.deal_id

        messages = split_email_html_on_messages(request.messages_html)
        prepared_conversation = prepare_conversation_to_prompt(messages)

    api_key = "YXBpZmFtYWdhcnU6RHpJVFd1Lk1COUV4LjNmdERsZ01YYlcvb0VFcW9NLw"
    session_id = "085qpt4eflu39a0dg7hjhr5mdu"
    client = FamagaClient(api_key, session_id)

    ghconv = GoogleSheet(
        spreadsheet='Famaga Knowledge Map',
        credentials_path=os.path.join(project_root, 'langchain-400510-06936d0d30b5.json'))

    discount_processing = DiscountProcessingAction(openai_client, task_repository, telegram_bot, logger, redis_client)
    document_selection = DocumentSelectionAction(openai_client, task_repository, telegram_bot, logger, redis_client)
    task_execution = TaskExecutionAction(openai_client, task_repository, telegram_bot, logger, ghconv, redis_client)
    query_builder = QueryBuilderAction(openai_client, task_repository, telegram_bot, logger, ghconv, redis_client)

    discount_result = discount_processing.discount_processing(run, prepared_conversation)

    discount_messages = ''
    for id in sorted(discount_result.data.messages_ids, reverse=True):
        discount_messages += f'Message: {id}\n'
        discount_messages += f'```\n' + messages[-id] + '\n```\n\n'

    offer_info = client.list_offers_by_deal_id(deal_id)
    offer_id = offer_info['content'][0]['request']['id']
    client_id = offer_info['content'][0]['request']['firm']['id']

    purchase_history = client.get_client_purchase_history_formatted(client_id, int(deal_id))

    current_offer = client.list_current_offer_details(offer_id)

    document_selection_result = document_selection.document_selection(run,
                                          discount_messages=discount_messages,
                                          purchase_history=purchase_history,
                                          current_offer=current_offer)

    query_result = query_builder.build_query(run,
                              document_name=document_selection_result.data.document_name,
                              discount_messages=discount_messages,
                              purchase_history=purchase_history
                              )

    sheet_data = ghconv.get_sheet_data(document_selection_result.data.document_name)
    headers = sheet_data.pop(0)
    sheet_data.pop(0)
    df = pd.DataFrame(sheet_data, columns=headers)

    result = df.query(query_result.data.query)
    instruction = result['instruction'].iloc[0]

    task_execution_result = task_execution.execute_task(run,
                                instruction=instruction,
                                discount_messages=discount_messages,
                                purchase_history=purchase_history,
                                current_offer=current_offer
                                )

    run_data = Run(
        actions=[
            discount_result,
            document_selection_result,
            query_result,
            task_execution_result
        ],
        run=RunDetails(run_id=run.run_id),
        tasks=[
            Task(summary=task_execution_result.data.output)
        ]
    )

    return run_data
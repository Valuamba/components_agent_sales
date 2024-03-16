from fastapi import APIRouter, Depends

from agents.pricing_manager.agent import PricingManagerAgent
from branches.branch import parse_branch
from branches.classify_request.actions.classify_parts import ClassifyPartsAction
from branches.classify_request.branch import ClassifyRequestBranch
from branches.completion import GPTCompletionResolver
from branches.discount.branch import DiscountBranch
from branches.dispatcher import action_dispatcher
from branches.utils import load_yaml
from dependencies import get_pricing_manager, get_openai_client, get_logger, get_task_repository, get_deal_repository
from models import Deal
from repositories import TaskRepository, DealRepository
from schemas.v1.agents_completion import AgentCompletionRequest, HandleMessagesRequest
from utility import extract_messages_from_body, extract_messages_from_raw_html
import os

agents_router = APIRouter()


@agents_router.post("/agent/completion/create")
def create_agent_completion(request: AgentCompletionRequest,
                            pricing_manager: PricingManagerAgent = Depends(get_pricing_manager)):
    return pricing_manager.classify_messages_metadata_and_intents(request.deal_id, request.deal_info)


@agents_router.post("/agent/handle_messages")
def handle_messages(request: HandleMessagesRequest,
                    deal_repository: DealRepository = Depends(get_deal_repository),
                    openai_client=Depends(get_openai_client),
                    logger=Depends(get_logger),
                    task_repository: TaskRepository = Depends(get_task_repository),
                    ):
    if os.name == 'nt':  # Windows
        project_root = os.getcwd()
    else:  # Linux and other Unix-like OS
        project_root = os.environ.get('PYTHONPATH', os.getcwd())

    deal = deal_repository.get_or_create_deal(request.deal_id, Deal(
        deal_id=request.deal_id,
        subject=f"{request.deal_id}"))
    logger.info('Deal was or gotten created', {'deal_id': request.deal_id})

    print(os.getcwd())
    messages = extract_messages_from_raw_html(request.messages_html)
    # source_path = '..\\..\\..\\agents'
    branches_dict = load_yaml(os.path.join(project_root, 'agents', 'branches.yml'))
    branches = []
    for branch_dict in branches_dict['branches']:
        data_path = os.path.join(project_root, 'agents', branch_dict['path'])
        data = load_yaml(data_path)
        branch = parse_branch(data, branch_dict['name'])
        if branch_dict.get('main', False):
            branch.main = True
        branches.append(branch)

    gpt_completion_resolver = GPTCompletionResolver({},
                                                    openai_client=openai_client, task_repository=task_repository,
                                                    logger=logger, off_mapping=True)

    discount_branch = next(branch for branch in branches if branch.name == 'discount')
    discount_branch = DiscountBranch(branch=discount_branch, branches=branches,
                                     gpt_completion_resolver=gpt_completion_resolver)

    classify_request_branch = next(branch for branch in branches if branch.name == 'classify_request')
    classify_request_branch = ClassifyRequestBranch(branch=classify_request_branch, branches=branches,
                                                    gpt_completion_resolver=gpt_completion_resolver)

    classify_parts_action = ClassifyPartsAction(gpt_completion_resolver)

    action_output = action_dispatcher(request.deal_id, messages, branches,
                                      logger=logger,
                                      classify_request_branch=classify_request_branch,
                                      discount_branch=discount_branch,
                                      classify_parts_action=classify_parts_action)

    return {
        **action_output,
        'logs': gpt_completion_resolver.agents_logger
    }

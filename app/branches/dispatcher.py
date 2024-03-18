from typing import List

from branches.branch import AgentIteration, Branch, AgentFinish, Action
from branches.classify_request.actions.classify_parts import ClassifyPartsAction
from branches.classify_request.branch import ClassifyRequestBranch
from branches.discount.branch import DiscountBranch
from branches.utils import parse_output
from services import LoggingService


def action_dispatcher(deal_id: int,
                      messaging_history: List[str],
                      branches,
                      logger: LoggingService,
                      classify_request_branch: ClassifyRequestBranch,
                      discount_branch: DiscountBranch,
                      classify_parts_action: ClassifyPartsAction):
    intermediate_steps = []
    start_from_latest_messaging = messaging_history[::-1]
    response = classify_request_branch.run(deal_id, start_from_latest_messaging)

    matched_obj = parse_output(response, classify_request_branch.branch, branches)

    intermediate_steps.append(AgentIteration(iter_obj=matched_obj))

    max_iters = 3
    iters = 0
    while iters < max_iters:
        logger.info(f'Agents iter {iters}')
        try:
            next_step = next(step for step in intermediate_steps if not step.state)
            iter_obj = next_step.iter_obj
            if isinstance(iter_obj, Branch):
                logger.info(f'Kek {iter_obj.branch}')
                if iter_obj.name == 'discount':
                    logger.info(f'Kek 2 {iter_obj.branch}')
                    response = discount_branch.run(deal_id, start_from_latest_messaging)
                    next_step_output = AgentIteration(iter_obj=parse_output(response, discount_branch.branch, branches))
                    # logs.append({
                    #     'step_name': iter_obj.name,
                    #     'log': response
                    # })

            elif isinstance(iter_obj, Action):
                if iter_obj.name == 'ask_about_desired_discount_or_price':
                    next_step_output = AgentFinish(output='ask_about_desired_discount_or_price', action=iter_obj.name)
                elif iter_obj.name == 'offer_2_percent_discount':
                    next_step_output = AgentFinish(output='offer_2_percent_discount', action=iter_obj.name)
                elif iter_obj.name == 'change_price_as_previous_bought':
                    next_step_output = AgentFinish(output='change_price_as_previous_bought', action=iter_obj.name)
                elif iter_obj.name == 'send_commercial_offer':
                    next_step_output = AgentFinish(output='send_commercial_offer', action=iter_obj.name)
                elif iter_obj.name == 'notify_sales_lead':
                    next_step_output = AgentFinish(output='notify_sales_lead', action=iter_obj.name)
                elif iter_obj.name == 'classify_parts':
                    next_step_output = classify_parts_action.classify_client_response(deal_id, start_from_latest_messaging[-1])
                else:
                    raise Exception(f'there is no handler for {iter_obj}')

                # logs.append({
                #     'step_name': iter_obj.name,
                #     'log': next_step_output.log
                # })

            # logger.info(f'Kek 3 {iters}')
            iters += 1
            if isinstance(next_step_output, AgentFinish):
                return {
                    'output': next_step_output.output,
                    'action': next_step_output.action
                    # 'logs': logs
                }

            next_step.state = True
            intermediate_steps.append(next_step_output)
        except Exception as exc:
            logger.error(str(exc))
            return {
                'status': 500,
                'error': str(exc)
                # 'logs': logs
            }

    return {
        'status': 500,
        'error': 'Exceeded maximum iteration limit without completing the task',
        # 'logs': logs
    }
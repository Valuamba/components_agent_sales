from typing import List

from fastapi import Depends, APIRouter
from configs.config import app_settings
from dependencies import get_classify_email_agent, get_logger, get_google_search
from services import ClassifyEmailAgent, GoogleSearch
from schemas.completion import EmailRequest, DetailRequest, GoogleSearchItems, GoogleSearchResponse, Detail

from fastapi.responses import JSONResponse


completion_router = APIRouter()


@completion_router.post("/request/classify", response_model=List[DetailRequest])
async def get_client_request_price(client_request: EmailRequest,
                                   classify_email_agent: ClassifyEmailAgent = Depends(get_classify_email_agent)):
    order, usage_cost_usd = await classify_email_agent.classify_client_response(client_request)

    # details_dicts = [detail.model_dump() for detail in details]

    headers = {'openai-usage-cost-usd': str(usage_cost_usd)}
    return JSONResponse(content=order.model_dump(), headers=headers)


@completion_router.post("/detail/get_from_famaga_table")
def get_detail_from_table(
        detail: DetailRequest,
        logger=Depends(get_logger),
        classify_email_agent: ClassifyEmailAgent = Depends(get_classify_email_agent)):
    presented_db_details, usage_cost_usd = classify_email_agent.search_detail_at_db(detail)

    mapped_details = [Detail(
        id=detail.id,
        part_number=detail.part_number,
        brand_name=detail.title,
        description=detail.description
    ) for detail in presented_db_details]

    if len(mapped_details):
        logger.info('<b>Details at company table</b>\n\n' + '\n\n'.join([
            f"<b>ID</b>: {detail.id}\n" +
            f"<b>Brand name:</b> {detail.brand_name}\n<b>Part number:</b> {detail.part_number}\n<b>Description:</b> {detail.description}"
            for detail in mapped_details]))

    details_dicts = [detail.model_dump() for detail in mapped_details]

    headers = {'openai-usage-cost-usd': str(usage_cost_usd)}
    return JSONResponse(content=details_dicts, headers=headers)


@completion_router.post("/detail/search_price_at_google", response_model=List[GoogleSearchItems])
def search_detail_at_google(
        detail: DetailRequest,
        google_search: GoogleSearch = Depends(get_google_search),
        classify_email_agent: ClassifyEmailAgent = Depends(get_classify_email_agent)
):
    restricted_websites_query = ' AND '.join(
        [f'-site:{domain}' for domain in app_settings.search_4price_restricted_websites])
    query = f'{detail.brand_name} {detail.part_number} AND {restricted_websites_query} AND -filetype:pdf'

    search_items = google_search.search(query, pages=2)
    suitable_items, usage_cost_usd, metadata = classify_email_agent.find_suitable_items(search_items, query, detail)

    google_search_items = []
    for suitable_item in suitable_items:
        full_item_info = search_items[suitable_item.id]

        google_search_items.append(GoogleSearchItems(
            title=full_item_info['title'],
            snippet=full_item_info['snippet'],
            link=full_item_info['link'],
            currency=full_item_info.get('currency', None),
            price=full_item_info.get('price', None),
            relevance=suitable_item.relevance
        ))

    filtered_google_search_items = sorted(google_search_items,
                                          key=lambda item: (0, item.price) if item.price is not None else (1,))

    response = GoogleSearchResponse(metadata=metadata, google_items=filtered_google_search_items)

    headers = {'openai-usage-cost-usd': str(usage_cost_usd)}
    return JSONResponse(content=response.model_dump(), headers=headers)

import os
import requests
import logging
import pandas as pd
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any


# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI()

# Define the API base URL
BASE_URL = "https://api.famaga.org"

# Define the decision types
class DecisionType:
    NO_DECISION = 0
    BILLED = 1
    BILL_PAID = 2
    PRICE = 3
    DELIVERY_TIME = 4
    REJECT_OTHER_REASON = 5
    TENDER = 6
    COLLECTING_OTHER_KP = 7
    THINK_OTHER_REASON = 8
    CONTRACT_SIGNING = 9
    OTHER_AGREEMENT = 10

YES_DECISIONS = [DecisionType.BILLED, DecisionType.BILL_PAID]
NO_DECISIONS = [DecisionType.PRICE, DecisionType.DELIVERY_TIME, DecisionType.REJECT_OTHER_REASON]
THINK_DECISIONS = [DecisionType.TENDER, DecisionType.COLLECTING_OTHER_KP, DecisionType.THINK_OTHER_REASON]
COORDINATION_DECISIONS = [DecisionType.CONTRACT_SIGNING, DecisionType.OTHER_AGREEMENT]

class APIClientV2:
    def __init__(self, token: str) -> None:
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def _handle_response(self, response: requests.Response) -> Dict:
        try:
            response.raise_for_status()
            print(f"Request to {response.url} succeeded with status code {response.status_code}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            raise

    def _get(self, endpoint: str, params: Dict = None, limit: int = 100, page: int = 1) -> Dict:
        url = f"{BASE_URL}{endpoint}"
        if params is None:
            params = {}
        params['limit'] = limit
        params['page'] = page
        response = requests.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(response)

    def _flatten_json(self, y: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        items = []
        for k, v in y.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_json(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    items.extend(self._flatten_json({f"{new_key}_{i}": item}).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def offers_by_client_id(self, client_id: int, limit: int = 100, page: int = 1) -> pd.DataFrame:
        data = self._get('/requisition', params={'client': client_id}, limit=limit, page=page)
        flattened_data = [self._flatten_json(content) for content in data["content"]]
        return pd.DataFrame(flattened_data)

    def offers_by_deal_id(self, deal_id: int, limit: int = 100, page: int = 1) -> pd.DataFrame:
        data = self._get('/requisition', params={'request': deal_id}, limit=limit, page=page)
        flattened_data = [self._flatten_json(content) for content in data["content"]]
        return pd.DataFrame(flattened_data)

    def get_deals(self, limit: int = 100, page: int = 1) -> pd.DataFrame:
        data = self._get('/requisition', params=None, limit=limit, page=page)
        flattened_data = [self._flatten_json(content) for content in data["content"]]
        return pd.DataFrame(flattened_data)

    def offer_products(self, offer_id: int, limit: int = 100, page: int = 1) -> pd.DataFrame:
        data = self._get(f'/requisition/{offer_id}/products', limit=limit, page=page)
        flattened_data = [self._flatten_json(product) for product in data]
        return pd.DataFrame(flattened_data)

    def get_notice_mail(self, request_id: int, limit: int = 100, page: int = 1) -> pd.DataFrame:
        data = self._get('/requisition-client-history', params={'request': request_id}, limit=limit, page=page)
        flattened_data = [self._flatten_json(content) for content in data["content"]]
        return pd.DataFrame(flattened_data)

    def _calculations_to_df(self, data):
        product_data = []

        for entry in data["content"]:
            if entry["version_data"]:
                calculation_id = entry["id"]
                request_id = entry["request"]["id"]
                created_at = entry["created_at"]

                for product in entry["version_data"]["products"]:
                    if isinstance(product, dict):
                        product_entry = {
                            "request_id": request_id,
                            "calculation_id": calculation_id,
                            "created_at": created_at,
                            **product
                        }
                        product_data.append(product_entry)

        product_df = pd.DataFrame(product_data)
        return product_df


    def get_calculation_history(self, request_id: int, limit: int = 100, page: int = 1) -> pd.DataFrame:
        data = self._get('/calculation-history', params={'request': request_id}, limit=limit, page=page)
        return self._calculations_to_df(data)

    def get_calculations(self, limit: int = 100, page: int = 1) -> pd.DataFrame:
        data = self._get('/calculation-history', params=None, limit=limit, page=page)
        return self._calculations_to_df(data)

    def to_dict(self):
        return {
            "token": self.token
        }


def get_final_calculation_price(calculations_df):
    df = calculations_df.copy()

    df['price_end'] = pd.to_numeric(df['price_end'], errors='coerce')
    df['price_sell_ru'] = pd.to_numeric(df['price_sell_ru'], errors='coerce')

    df['price_final'] = np.where((df['price_end'].isna()) | (df['price_end'] == 0) | (df['price_end'] == 0.00),
        df['price_sell_ru'], df['price_end'])

    return df

def prettify_customer_data(customer_data):
    if customer_data['desired_discount_per'] is not None or customer_data['desired_price'] is not None:
        customer_data['is_specified_desired_price'] = True
    else:
        customer_data['is_specified_desired_price'] = False

    prettified_data = [
        f"Desired Discount Percentage: {customer_data['desired_discount_per'] if customer_data['desired_discount_per'] is not None else 'Not specified'}",
        f"Desired Price: {customer_data['desired_price'] if customer_data['desired_price'] is not None else 'Not specified'}",
        f"Is Specified Desired Price: {'Yes' if customer_data['is_specified_desired_price'] else 'No'}",
        f"Is Customer Large Company: {'Yes' if customer_data['is_customer_large_company'] else 'No'}",
        f"Deals Without Purchase: {customer_data['deals_without_purchase']}",
        f"Deals With Purchases: {customer_data['deals_with_purchases']}"
    ]

    return '\n'.join(prettified_data)


def prettify_deal(deal_info_df, calculation_df, selected_deals, previously_bought_products_df):
    previously_bought_products_df = get_final_calculation_price(previously_bought_products_df)

    result_str = ""

    for request_id, deal_info in selected_deals.items():
        if request_id in deal_info_df['request_id'].values:
            deal_info_row = deal_info_df[deal_info_df['request_id'] == request_id].iloc[0]
            deal_date = pd.to_datetime(deal_info_row['created']).date()

            result_str += f"Deal #{request_id} {deal_date}:\n\n"

        if deal_info['products']:
            result_str += "Products:\n"
            for articul in deal_info['products']:
                product_row = previously_bought_products_df[previously_bought_products_df['articul'] == articul].iloc[0]
                brand_id = product_row['brand_id']
                result_str += f"({articul}) {brand_id} {product_row['count']} qty., {product_row['price_final']}€ (margin {product_row['margin_ru']}%)\n"
            result_str += "\n"

        if len(deal_info['calculations_product']) > 0:
            calculation_df['created_at'] = pd.to_datetime(calculation_df['created_at'])
            filtered_calculations = calculation_df[calculation_df['request_id'] == request_id]
            result_str += "Calculations:\n"

            for articul, calc_ids in deal_info['calculations_product'].items():
                filtered_calcs = filtered_calculations[
                    (filtered_calculations['articul'] == articul) &
                    (filtered_calculations['calculation_id'].isin(calc_ids))
                    ]

                sorted_calcs = filtered_calcs.sort_values(by='created_at', ascending=False)

                for _, calc_row in sorted_calcs.iterrows():
                    created_at = calc_row['created_at']
                    calculation_id = calc_row['calculation_id']
                    price = calc_row['price_end'] if pd.notna(calc_row['price_end']) else calc_row['price_sell_ru']

                    result_str += f"{created_at} {calculation_id} ({articul}) {price}\n"

        result_str += "\n---\n"

    return result_str


def get_requests_dict(previously_bought_products, discounted_deals):
    result_dict = {}

    if len(discounted_deals) > 0:
        grouped = discounted_deals.groupby('request_id')

        for request_id, group in grouped:
            request_dict = {
                "request_id": request_id,
                "products": [],
                "full_calculations": [],
                "calculations_product": {}
            }

            for idx, row in group.iterrows():
                articul = row['articul']
                calculations = [row['first_offer_calculation_id'], row['latest_offer_calculation_id']]

                if articul not in request_dict['calculations_product']:
                    request_dict['calculations_product'][articul] = []

                request_dict['calculations_product'][articul].extend(calculations)
                request_dict['calculations_product'][articul] = list(set(request_dict['calculations_product'][articul]))

            result_dict[request_id] = request_dict

    for _, row in previously_bought_products.iterrows():
        request_id = row['request_id']
        articul = row['articul']

        if request_id not in result_dict:
            result_dict[request_id] = {
                "request_id": request_id,
                "products": [],
                "full_calculations": [],
                "calculations_product": {}
            }

        if articul not in result_dict[request_id]['products']:
            result_dict[request_id]['products'].append(articul)

    return result_dict


def get_discounted_deals(calculations_df, unique_request_ids):
    all_discounted_requests = pd.DataFrame()

    for request_id in unique_request_ids:
        calc_deal_df = calculations_df[calculations_df['request_id'] == request_id]
        discounted_requests = get_disconted_requests(calc_deal_df)

        if len(discounted_requests) > 1:
            all_discounted_requests = pd.concat([all_discounted_requests, discounted_requests], ignore_index=True)
    return all_discounted_requests


def get_calculations(client, unique_request_ids):
    calculation_history_list = []
    for request_id in unique_request_ids:
        calculation_history_df = client.get_calculation_history(int(request_id))
        calculation_history_df['request_id'] = request_id
        calculation_history_list.append(calculation_history_df)
    common_calculation_history_df = pd.concat(calculation_history_list, ignore_index=True)
    return common_calculation_history_df


def get_products_history(client, unique_request_ids):
    offer_products_list = []
    for request_id in unique_request_ids:
        offer_products_df = client.offer_products(request_id)
        offer_products_df['request_id'] = request_id
        offer_products_list.append(offer_products_df)
    common_offer_products_df = pd.concat(offer_products_list, ignore_index=True)
    return common_offer_products_df


def get_disconted_requests(request_calcs):
    calc_deal_df = get_final_calculation_price(request_calcs)
    calc_deal_df['created_at'] = pd.to_datetime(calc_deal_df['created_at'])
    calc_deal_df = calc_deal_df.sort_values(by='created_at', ascending=False)

    discounted_calculations = []

    for index, row in calc_deal_df.groupby('articul'):
        if len(row) > 1:
            latest_offer = row.iloc[0]
            first_offer = row.iloc[-1]

            if first_offer['calculation_id'] != latest_offer['calculation_id'] \
                    and first_offer['articul'] == latest_offer['articul'] \
                    and first_offer['count'] == latest_offer['count'] \
                    and first_offer['price_final'] > latest_offer['price_final']:
                assert latest_offer['created_at'] > first_offer['created_at']
                assert latest_offer['calculation_id'] > first_offer['calculation_id']

                discounted_calculations.append({
                    'request_id': latest_offer['request_id'],
                    'articul': latest_offer['articul'],
                    'first_offer_calculation_id': first_offer['calculation_id'],
                    'latest_offer_calculation_id': latest_offer['calculation_id']
                })
                print(
                    f'({latest_offer["articul"]}) {latest_offer["calculation_id"]}) {latest_offer["price_final"]} - ({first_offer["articul"]}) {first_offer["price_final"]}')

    discounted_calcs_df = pd.DataFrame(discounted_calculations)
    return discounted_calcs_df


def get_gpt(content, model="gpt-4-1106-preview", temperature=0, max_tokens=1000, stream=True):
    messages = [{"role": "user", "content": content}]

    if stream:
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True
        )

        collected_messages = []
        for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end='')
                collected_messages.append(chunk.choices[0].delta.content)

        content_str = ''.join(collected_messages)
        return content_str
    else:
        completion = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return completion.model_dump()


def get_discount_decision(current_deal_str, purchase_history_str, customer_data):
    res = get_gpt(f"""
Here is an instruction:

1. **Customer previously purchased THIS product:** Try to offer the same price as last time if profitability allows. If not, set a 12% margin and explain that the supplier's price has changed, and this is the maximum possible discount.

2. **Customer has NOT previously purchased THIS product but specified a desired price:** Offer a discount if the margin allows. Otherwise, set a 10% margin and explain that this is the maximum possible discount.

3. **Customer has NOT purchased THIS product and has NOT specified a desired price, BUT has purchased other products:**

   a) **If the margin was unchanged in previous deals** (the price in the initial offer equals the price in the final offer for the same quantity within one quotation): Refuse the discount.

   b) **If the margin changed in previous deals** (the price in the initial offer does not equal the price in the final offer for the same quantity within one quotation):

      - If the price in the final offer is higher: Ignore the case (this is due to the supplier's price increase while the customer was deciding).
      - If a discount was given previously: Offer a 2% discount.

4. **Customer has NEVER purchased before and has NOT specified a desired price:** Check the total number of customer deals.

   a) **First quotation for a large company:** Offer a 2% discount and ask for the desired price.

   b) **First quotation for a non-large company:** Refuse the discount.

   c) **More than 10 quotations without any sales:** Set a 10% margin. This customer is a candidate for the blacklist; if they do not buy even with the maximum discount, we will likely not work with them in the future.

   d) **Several quotations with request dates differing by +/- 2 days (likely one project):** Propose a discount if the customer buys multiple quotations at once. Do not specify the exact price but ask for the desired price and hand it over to the manager for manual processing.

Additionally, remember the outcomes:

   a) **In case of a FULL discount refusal:** If the customer still buys, continue to refuse discounts. If the customer does not buy, offer a 2% discount next time and ask for the desired price.

   b) **In case of offering a 2% discount:** If the customer buys, continue offering 2% where possible. If the customer does not buy, offer a 3% discount next time (if margin allows) and continue to find the "acceptable discount" from deal to deal.

Margin formula:
 \text{{Margin}} = 100 \times \left(1 - \frac{{\text{{Total Purchase Price}}{{\text{{Total Selling Price}}\right) 

# Customer data

{customer_data}

## Current deal

{current_deal_str}

## Purchase history

{purchase_history_str}

Please make decision

    """, 'gpt-4o'
                  )
    return res


# client = APIClientV2('YXBpZmFtYWdhcnU6RHpJVFd1Lk1COUV4LjNmdERsZ01YYlcvb0VFcW9NLw')
#
#
# # Example usage
# deal_id = 512786
# current_deal = client.offers_by_deal_id(deal_id)
# current_deal_products = client.offer_products(deal_id)
#
# client_id = int(current_deal.loc[0]['request_firm_id'])
#
# all_customer_offers = client.offers_by_client_id(client_id)
#
# customer_offers = all_customer_offers[~(all_customer_offers['request_id'] == deal_id)]
# customer_offers = customer_offers[customer_offers['decision'].isin(YES_DECISIONS)]
#
# purchase_history_str = ''
# unique_request_ids = customer_offers['request_id'].unique()
# customer_calculations = None
#
# if len(unique_request_ids) > 0:
#     customer_products_df = get_products_history(unique_request_ids)
#     customer_calculations = get_calculations(unique_request_ids)
#
#     discounted_deals = get_discounted_deals(customer_calculations, unique_request_ids)
#
#     bought_earlier_products_df = customer_products_df[
#         customer_products_df['articul'].isin(current_deal_products['articul'])
#     ]
#
#     purchase_history_dict = get_requests_dict(bought_earlier_products_df, discounted_deals)
#
#     purchase_history_str = prettify_deal(customer_offers, customer_calculations, purchase_history_dict, customer_products_df)
#
# current_deal_dict = get_requests_dict(get_products_history(current_deal['request_id']), pd.DataFrame())
# current_deal_str = prettify_deal(current_deal, customer_calculations, current_deal_dict, current_deal_products)
#
# customer_data = {
#     'desired_discount_per': None,
#     'desired_price': None,
#     'is_specified_desired_price': False,
#     'is_customer_large_company': False,
#     'deals_without_purchase': all_customer_offers[~(all_customer_offers['decision'].isin(YES_DECISIONS))].drop_duplicates().shape[0],
#     'deals_with_purchases': all_customer_offers[(all_customer_offers['decision'].isin(YES_DECISIONS))].drop_duplicates().shape[0]
# }
#
# decision_resp = get_discount_decision(current_deal_str, purchase_history_str, prettify_customer_data(customer_data))
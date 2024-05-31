import requests

class FamagaClient:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.famaga.org"

    def list_offers_by_deal_id(self, deal_id):
        url = f"{self.base_url}/requisition?request={deal_id}"
        headers = {'Authorization': self.api_token}
        response = requests.get(url, headers=headers)
        return response.json()

    def get_client_purchase_history_formatted(self, client_id, deal_id):
        url = f"{self.base_url}/requisition?client={client_id}"
        headers = {'Authorization': self.api_token}
        response = requests.get(url, headers=headers)
        return response.json()

    def list_current_offer_details(self, offer_id):
        url = f"{self.base_url}/requisition/{offer_id}/products"
        headers = {'Authorization': self.api_token}
        response = requests.get(url, headers=headers)
        return response.json()

# Helper function to calculate margin
def calculate_margin(total_purchase_price, total_selling_price):
    return ((total_selling_price - total_purchase_price) / total_purchase_price) * 100

# Decision-making function
def determine_discount(deal_id, client):
    # client = FamagaClient("Bearer YXBpZmFtYWdhcnU6RHpJVFd1Lk1COUV4LjNmdERsZ01YYlcvb0VFcW9NLw")

    offer_info = client.list_offers_by_deal_id(deal_id)
    if not offer_info['content']:
        return "No offers found for this deal ID"

    offer_id = offer_info['content'][0]['request']['id']
    client_id = offer_info['content'][0]['request']['firm']['id']
    purchase_history = client.get_client_purchase_history_formatted(client_id, int(deal_id))
    current_offer = client.list_current_offer_details(offer_id)

    if not current_offer:
        return "No current offer details found"

    total_purchase_price = sum([float(product['price_buy_ru']) for product in current_offer])
    total_selling_price = sum([float(product['price_sell_ru']) for product in current_offer])
    current_margin = calculate_margin(total_purchase_price, total_selling_price)

    # Implement the discount logic
    has_purchased_current_product = any(deal['id'] == deal_id for deal in purchase_history['content'])
    if has_purchased_current_product:
        previous_offer = purchase_history['content'][0]
        previous_price = float(previous_offer['request']['cost'])
        if total_purchase_price <= previous_price:
            return f"Offer same price as last time: {previous_price}"
        else:
            new_price = total_purchase_price * 1.12
            return f"Set 12% margin price: {new_price}, explain manufacturer's price change"

    has_specified_desired_price = any(deal['target_price'] > 0 for deal in purchase_history['content'])
    if has_specified_desired_price:
        desired_price = next(deal['target_price'] for deal in purchase_history['content'] if deal['target_price'] > 0)
        if total_purchase_price <= desired_price:
            return f"Offer desired price: {desired_price}"
        else:
            new_price = total_purchase_price * 1.10
            return f"Set 10% margin price: {new_price}, explain maximum possible discount"

    if purchase_history['total'] > 0:
        if all(float(deal['request']['cost']) == total_purchase_price for deal in purchase_history['content']):
            return "Deny discount, margin did not change"
        else:
            previous_offers = [float(deal['request']['cost']) for deal in purchase_history['content']]
            if any(prev_price > total_purchase_price for prev_price in previous_offers):
                return "Ignore case, manufacturer's price increase while deciding"
            else:
                return "Give 2% discount due to previous discount"

    if purchase_history['total'] == 0:
        if purchase_history['content'][0]['request']['firm']['type'] == '1':
            return "Give 2% discount, ask for desired price"
        else:
            return "Deny discount, client is not a large company"

    if purchase_history['total'] > 10:
        return "Set 10% margin, candidate for blacklist if no purchase with max discount"

    if any(abs((deal['created'] - purchase_history['content'][0]['created']).days) <= 2 for deal in purchase_history['content']):
        return "Suggest discussing discount for multiple offers, pass to sales team for manual processing"

    return "No applicable discount found"

# Example usage
# deal_id = 432036  # Replace with actual deal_id
# discount_decision = determine_discount(deal_id)
# print(discount_decision)
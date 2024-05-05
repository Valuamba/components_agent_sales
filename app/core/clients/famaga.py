import requests
from collections import defaultdict
from datetime import datetime


class FamagaClient:
    def __init__(self, api_key, session_id):
        self.base_url = "https://api.famaga.org"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Cookie": f"PHPSESSID={session_id}"
        }

    def list_offers_by_deal_id(self, deal_id):
        """List offers by deal ID"""
        response = requests.get(f"{self.base_url}/requisition?request={deal_id}", headers=self.headers)
        return response.json()

    def parts_selected_at_offer(self, offer_id):
        """Fetch parts selected at a specific offer"""
        response = requests.get(f"{self.base_url}/requisition/{offer_id}/products", headers=self.headers)
        return response.json()

    def list_offers_by_client_id(self, client_id):
        """Retrieve offers by client ID"""
        response = requests.get(f"{self.base_url}/requisition?client={client_id}", headers=self.headers)
        return response.json()

    def list_current_offer_details(self, offer_id):
        """List details of the current offer in a specific format"""
        parts = self.parts_selected_at_offer(offer_id)
        formatted_parts = []
        for part in parts:
            formatted_part = f"({part['articul']} {part['brand_title']}) margin: {part['margin_ru']}%, sell: {part['price_end']}$ qty. {part['count']}"
            formatted_parts.append(formatted_part)
        return "\n".join(formatted_parts)

    def find_parts_client_bought_before(self, client_id, current_offer_parts):
        """Return the parts that a client has bought before"""
        all_offers = self.list_offers_by_client_id(client_id)
        past_parts = []
        for offer in all_offers.get('content', []):
            parts = self.parts_selected_at_offer(offer['request']['id'])
            past_parts.extend(parts)

        bought_before = []
        current_parts_articul = [part['articul'] for part in current_offer_parts]
        for part in past_parts:
            if part['articul'] in current_parts_articul:
                bought_before.append(part)

        return bought_before

    def get_client_purchase_history_formatted(self, client_id, exluded_deal: int = None):
        """Generate formatted purchase history for a client"""
        history_data = self.list_offers_by_client_id(client_id)
        purchases = defaultdict(list)

        for item in history_data.get('content', []):
            date_key = datetime.strptime(item['created'], '%Y-%m-%dT%H:%M:%S%z').date()
            request_id = int(item['request']['id'])
            if exluded_deal is None or request_id != exluded_deal:
                parts = self.parts_selected_at_offer(request_id)

                for part in parts:
                    line = f"{item['id']} ({part['articul']} {part['brand_title']}) margin: {part['margin_ru']}%, sell: {part['price_end']}$ qty. {part['count']}, request id {part['request_id']}"
                    purchases[date_key].append(line)

        # Formatting the result
        result = "[CLIENT PURCHASE HISTORY]\n**Client purchase history:**\n"
        for date in sorted(purchases):
            result += f"Date: {date}\n"
            result += "\n".join(purchases[date]) + "\n\n"
        result += "[/CLIENT PURCHASE HISTORY]"
        return result



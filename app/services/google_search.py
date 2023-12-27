from services.logger_service import LoggingService
import requests
import json


class GoogleSearch:
    def __init__(self, logger: LoggingService, serper_api_key):
        self.logger = logger
        self.serper_api_key = serper_api_key

    def _search(self, query: str, country = 'us', page: int = 1):
        self.logger.info(f'Google search params: page={page}, query: {query}')

        url = "https://google.serper.dev/search"
        
        payload = json.dumps({
        "q": query,
        "gl": country,
        "page": page
        })

        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return json.loads(response.text)

    def search(self, query: str, country = 'us', pages = 1):
        items = []
        for i in range(pages):
            items += self._search(query, country=country, page=i+1)['organic']    

        return items

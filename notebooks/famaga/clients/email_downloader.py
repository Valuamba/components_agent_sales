from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime

class EmailFrom(BaseModel):
    personal: str
    mailbox: str
    host: str
    mail: EmailStr
    full: str

class EmailBody(BaseModel):
    text: str
    html: str

class EmailContentItem(BaseModel):
    subject: str
    body: EmailBody
    from_: EmailFrom = Field(..., alias='from')  # Ensure this matches the structure
    date: datetime

class EmailResponse(BaseModel):
    content: List[EmailContentItem]
    total: int
    
class EmailDownloader:
    def __init__(self, base_url: str, bearer_token: str):
        self.base_url = base_url
        self.bearer_token = bearer_token
        self.headers = {
            "Authorization": f"Bearer {bearer_token}"
        }

    def download_email_content(self, deal_id: int):
        """
        Download email HTML content for a given deal ID.

        :param deal_id: The unique identifier for the deal
        :return: The HTML content of the email
        """
        download_url = f"{self.base_url}/deal/{deal_id}"
        response = requests.get(download_url, headers=self.headers)

        if response.status_code == 200:
            # return response.json()
            return EmailResponse(**response.json())
        else:
            raise Exception(f"Failed to download email content: {response.status_code} - {response.text}")

    def get_messages_from_content(self, data):
        """
        Extract messages from the email HTML content.

        :param data: The email content data
        :return: A list of extracted messages
        """
        if len(data['content']) == 0:
            print('There is no items')
            return []

        html_content = data['content'][-1]['body']['html']
        soup = BeautifulSoup(html_content, "html.parser")
        messages = []
        clone_body = copy.copy(soup)
        
        for nested_blockquote in clone_body.find_all("blockquote"):
            nested_blockquote.decompose()
            
        messages.append(clone_body.get_text(strip=True))
        blockquotes = soup.find_all("blockquote")
        
        for blockquote in blockquotes:
            clone = copy.copy(blockquote)
        
            for nested_blockquote in clone.find_all("blockquote"):
                nested_blockquote.decompose()
        
            messages.append(clone.get_text(strip=True))

        return messages

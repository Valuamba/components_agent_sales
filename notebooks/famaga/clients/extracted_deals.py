import sqlite3
import json
import os
import re


class ExtractedDealsRepository:
    def __init__(self, database_path):
        self.database_path = database_path

    def get_deals_with_keywords(self, keywords, exclude_phrases=None):
        if exclude_phrases is None:
            exclude_phrases = []
    
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            # Base query with placeholder for dynamic WHERE conditions
            query = """
            SELECT deal_id, parsed_messages
            FROM deals
            WHERE 1=1
            """
            
            # Initialize parameters list
            params = []
            
            # Dynamically add keyword conditions to the query and parameters list
            keyword_conditions = " OR ".join(["LOWER(parsed_messages) LIKE ?" for keyword in keywords])
            if keyword_conditions:
                query += f" AND ({keyword_conditions})"
                params.extend([f'%{keyword.lower()}%' for keyword in keywords])
            
            # Dynamically add exclusion phrases to the query and parameters list
            for phrase in exclude_phrases:
                query += " AND LOWER(parsed_messages) NOT LIKE ?"
                params.append(f'%{phrase.lower()}%')
            
            # Execute the query with dynamic parameters
            cursor.execute(query, params)
            
            rows = cursor.fetchall()
            
            return rows

    def get_deals_with_keywords_v2(self):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            query = """
            SELECT deal_id, parsed_messages
            FROM deals
            WHERE LOWER(parsed_messages) LIKE '%discount%'
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
        # Define regex patterns to exclude
        discount_regex = re.compile(r'discount', re.IGNORECASE)
        exclude_regex = re.compile(r'discount %|price incl\. discount', re.IGNORECASE)
        
        filtered_rows = []
        for row in rows:
            message = self.preprocess_text(row[1])
        
            # Find all instances of 'discount'
            discounts_found = discount_regex.findall(message)
            
            # Find all instances that match the exclusion criteria
            exclusions_found = exclude_regex.findall(message)
            
            # Include row if there are more 'discount' instances than exclusions or if no exclusions are found
            if len(discounts_found) > len(exclusions_found) or not exclusions_found:
                filtered_rows.append(row)
        
        return filtered_rows

    def get_deal_history(self, deal_id):
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()  
            query = "SELECT parsed_messages FROM deals WHERE deal_id = ?"
            cursor.execute(query, (deal_id,))
            result = cursor.fetchone()

            return json.loads(result[0])

    def get_messaging_html(self, deal_id):
        deal_id_to_extract = deal_id  
        
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()  
            query = "SELECT chat_history FROM deals WHERE deal_id = ?"
            cursor.execute(query, (deal_id_to_extract,))
            result = cursor.fetchone()
        
        if result:
            chat_history_json = result[0]
            chat_history = json.loads(chat_history_json)

            if chat_history['content']:
                html_content = chat_history['content'][-1]['body']['html']
                
                return html_content
            else:
                print("No content found.")

            return chat_history
        else:
            print(f"No deal found with ID {deal_id_to_extract}")

    def get_messaing_history_html(self, deal_id):
        deal_id_to_extract = deal_id  
        
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()  
            query = "SELECT chat_history FROM deals WHERE deal_id = ?"
            cursor.execute(query, (deal_id_to_extract,))
            result = cursor.fetchone()
        
        if result:
            chat_history_json = result[0]
            chat_history = json.loads(chat_history_json)

            return chat_history
        else:
            print(f"No deal found with ID {deal_id_to_extract}")


    def get_html_file(self, deal_id, folder='deals_html'):
        deal_id_to_extract = deal_id  
        
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()  
            query = "SELECT chat_history FROM deals WHERE deal_id = ?"
            cursor.execute(query, (deal_id_to_extract,))
            result = cursor.fetchone()
        
        if result:
            chat_history_json = result[0]
            chat_history = json.loads(chat_history_json)

            self.save_html_to_file(chat_history, dir_name=folder, file_name=f'{deal_id}.html')
        else:
            print(f"No deal found with ID {deal_id_to_extract}")

    @staticmethod
    def preprocess_text(text):
        normalized_text = re.sub(r'\s+', ' ', text.replace('\\r\\n', ' '))
        return normalized_text.lower()
    
    @staticmethod
    def filter_messages(rows, keywords):
        filtered_messages = []
        for deal_id, parsed_messages_json in rows:
            parsed_messages = json.loads(parsed_messages_json)
            messages_with_keywords = [
                message for message in parsed_messages if all(keyword.lower() in message.lower() for keyword in keywords)
            ]
            
            if messages_with_keywords:
                filtered_messages.append((deal_id, messages_with_keywords))
        
        return filtered_messages  

    @staticmethod
    def save_html_to_file(data, dir_name='htmls', file_name='content.html'):
        os.makedirs(dir_name, exist_ok=True)
        
        if data['content']:
            html_content = data['content'][-1]['body']['html']
            
            file_path = os.path.join(dir_name, file_name)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
            
            print(f"HTML content saved to {file_path}")
        else:
            print("No content found.")
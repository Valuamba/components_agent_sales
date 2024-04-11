import pandas as pd
import math


class ClientDealsHistoryRepository:
    def __init__(self, deals_history_path):
        df = pd.read_json(deals_history_path)
        
        df['amount'] = pd.to_numeric(df['amount'])
        df['price_sell'] = pd.to_numeric(df['price_sell'])
        df['price_buy'] = pd.to_numeric(df['price_buy']) 
        df['requisition_created'] = pd.to_datetime(df['requisition_created'])
        df['margin'] = 100 - (((df['price_buy'] * df['amount']) / (df['price_sell'] * df['amount'])) * 100)

        self.df = df

    def get_deals_by_id(self, deal_id):
        return self.df[self.df['id'] == deal_id]

    def print_purchase_history(self, purchase_history):
        purchase_history_str = ''
        for key in purchase_history.keys():
            print(f'Date: {key}')
            for item in purchase_history[key]:
                print(item)
            print('\n')

    def get_client_history(self, client_id):
        df = self.df
        ch = df[df['client_id'] == client_id]
        ch['price_sell'] = pd.to_numeric(ch['price_sell'])
        ch['price_buy'] = pd.to_numeric(ch['price_buy'])
        
        # Convert 'requisition_created' to datetime and sort
        ch['requisition_created'] = pd.to_datetime(ch['requisition_created'])
        ch.sort_values(by='requisition_created', inplace=True)
        
        # Calculate margin for each item
        ch['margin'] = 100 - (((ch['price_buy'] * ch['amount']) / (ch['price_sell'] * ch['amount'])) * 100)
        ch = ch[pd.notna(ch['margin'])]
        # ch['margin'] = ((ch['price_sell'] - ch['price_buy']) / ch['price_buy']) * 100
        
        grouped_by_date = ch.groupby(ch['requisition_created'].dt.date)
        
        # Iterate through each group and print the details
        purchase_history = {}
        for date, group in grouped_by_date:
            # print(f"Date: {str(date)}")
            purchase_history[date] = []
            for _, row in group.iterrows():
                id = row['id']
                brand_id = int(row['brand_id']) if not math.isnan(row['brand_id']) else None 
                # brand_id = int(row['brand_id'])
                articul = row['articul']
                brand_title = row['brand_title']
                articul = row['articul']
                margin = round(row['margin'], 2)
                sell_price = row['price_sell']
                qty = row['amount']
                purchase_history[date].append(row.to_dict())
                # purchase_history[date].append(f"{id} ({articul}) {brand_title} {articul} margin: {margin}%, sell: {sell_price}$ qty. {qty}")
                # print(f"{brand_title} {articul} margin: {margin}%, sell: {sell_price}$ qty. {qty}")
            # print('\n')
        return purchase_history

    def price_change_exceeds_5_percent(self, group, exceed_num):
        price_changes = group['price_sell'].pct_change().abs() > exceed_num
        return price_changes.any()
    
    def get_deals_with_exceeds_price(self, exceed_num=0.1):
        df = self.df
        df['price_sell'] = pd.to_numeric(df['price_sell'], errors='coerce')
        df = df[pd.notna(df['margin'])]
        
        grouped = df.sort_values(by='requisition_created').groupby(['articul', 'client_id'])
        clients_with_price_change = grouped.filter(lambda x: price_change_exceeds_5_percent(x, exceed_num))
        
        unique_clients = clients_with_price_change[['client_id', 'articul']].drop_duplicates()
        
        return unique_clients

    def price_change_exceeds_threshold(self, group, exceed_num):
        group['requisition_created'] = pd.to_datetime(group['requisition_created'])
        
        group = group.sort_values(by='requisition_created')
        group['day_diff'] = group['requisition_created'].diff().dt.days.abs()
        group['price_pct_change'] = group['price_sell'].pct_change().abs()
        price_changes = (group['price_pct_change'] > exceed_num) & (group['day_diff'] != 0)
        
        return price_changes.any()

    def get_deals_with_exceeds_price(self, exceed_num=0.1):
        df = self.df
        df['price_sell'] = pd.to_numeric(df['price_sell'], errors='coerce')
        df = df[pd.notna(df['margin'])]
        
        grouped = df.groupby(['articul', 'client_id'])
        clients_with_price_change = grouped.filter(lambda x: price_change_exceeds_threshold(x, exceed_num))
        
        unique_clients = clients_with_price_change[['client_id', 'articul']].drop_duplicates()
        
        return unique_clients
    
    def optimized_get_deals_with_exceeds_price(self, exceed_num=0.1):
        df = self.df
        df['price_sell'] = pd.to_numeric(df['price_sell'], errors='coerce')
        df['requisition_created'] = pd.to_datetime(df['requisition_created'])
        df = df[pd.notna(df['margin'])].sort_values(by=['articul', 'client_id', 'requisition_created'])
        
        df['day_diff'] = df.groupby(['articul', 'client_id'])['requisition_created'].diff().dt.days.abs()
        df['price_pct_change'] = df.groupby(['articul', 'client_id'])['price_sell'].pct_change().abs()
        
        condition = (df['price_pct_change'] > exceed_num) & (df['day_diff'] != 0)
        filtered_df = df[condition]
        
        unique_clients = filtered_df[['client_id', 'articul']].drop_duplicates()
    
        return unique_clients

    def optimized_get_deals_with_exceeds_price_with_gap(self, exceed_num=0.1, min_day_gap=30):
        df = self.df
        df['price_sell'] = pd.to_numeric(df['price_sell'], errors='coerce')
        df['requisition_created'] = pd.to_datetime(df['requisition_created'])
        df = df[df['articul'].notna() & (df['articul'] != '')]
        df = df[pd.notna(df['margin']) & df['articul'].notna() & (df['articul'] != '')]
        
        df = df.sort_values(by=['articul', 'client_id', 'requisition_created'], ascending=[True, True, True])
        
        df['day_diff'] = df.groupby(['articul', 'client_id'])['requisition_created'].diff().dt.days.abs()
        df['price_pct_change'] = df.groupby(['articul', 'client_id'])['price_sell'].pct_change().abs()
        
        condition = (df['price_pct_change'] > exceed_num) & (df['day_diff'] > min_day_gap)
        filtered_df = df[condition]
        
        unique_clients = filtered_df[['client_id', 'articul', 'id']].drop_duplicates()
    
        return unique_clients

    def group_by_clients(self):
        df = self.df
        grouped = df.groupby('client_id')['articul'].apply(list).reset_index()
        grouped['articuls'] = grouped['articul'].apply(lambda x: ', '.join(x))
        grouped = grouped[['client_id', 'articuls']].rename(columns={'articuls': 'articul'})
    
        return grouped
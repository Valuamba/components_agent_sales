from collections import defaultdict, Counter
from datetime import datetime
from math import sqrt


class ClientStatisticsService:
    @staticmethod
    def client_loyalty(purchase_history):
        data = sum(purchase_history.values(), [])
        for item in data:
            if isinstance(item['requisition_created'], str):
                item['requisition_created'] = datetime.strptime(item['requisition_created'], '%Y-%m-%d %H:%M:%S')

        client_transactions = defaultdict(list)
        for item in data:
            client_transactions[item['client_id']].append(item)

        client_loyalty_metrics = {}
        for client_id, transactions in client_transactions.items():
            transactions.sort(key=lambda x: x['requisition_created'])
            first_purchase_date = transactions[0]['requisition_created']
            last_purchase_date = transactions[-1]['requisition_created']
            duration_days = (last_purchase_date - first_purchase_date).days
            duration_years = duration_days / 365.25
            
            repeat_purchases = len(transactions) - 1
            client_loyalty_metrics[client_id] = {
                'Duration Years': duration_years,
                'Duration Days': duration_days,
                'Repeat Purchases': repeat_purchases
            }
        return client_loyalty_metrics

    @staticmethod
    def get_total_margin(purchase_history):
        data = sum(purchase_history.values(), [])
        total_profit = 0
        total_revenue = 0
        for item in data:
            profit_per_item = (item['price_sell'] - item['price_buy']) * item['amount']
            revenue_per_item = item['price_sell'] * item['amount']
            total_profit += profit_per_item
            total_revenue += revenue_per_item
        total_margin_percentage = (total_profit / total_revenue) * 100 if total_revenue else 0
        return total_margin_percentage

    @staticmethod
    def get_average_bill_per_deal(purchase_history):
        data = sum(purchase_history.values(), [])
        deals = defaultdict(list)
        for item in data:
            deals[item['id']].append(item)

        total_bills = [sum(item['price_sell'] * item['amount'] for item in items) for deal_id, items in deals.items()]
        average_bill_per_deal = sum(total_bills) / len(total_bills) if total_bills else 0
        return average_bill_per_deal

    @staticmethod
    def avg_interval_between_purchases(purchase_history):
        data = sum(purchase_history.values(), [])
        for item in data:
            if not isinstance(item['requisition_created'], datetime):
                item['requisition_created'] = datetime.strptime(item['requisition_created'], '%Y-%m-%d %H:%M:%S')
        data.sort(key=lambda x: x['requisition_created'])

        intervals = [(data[i]['requisition_created'] - data[i-1]['requisition_created']).days for i in range(1, len(data))]
        average_interval = sum(intervals) / len(intervals) if intervals else 0
        average_interval_months = average_interval / 30
        return average_interval, average_interval_months

    @staticmethod
    def purchase_volume_variability(purchase_history):
        data = sum(purchase_history.values(), [])
        purchase_amounts = [item['amount'] for item in data]
        mean_amount = sum(purchase_amounts) / len(purchase_amounts)
        variance = sum((x - mean_amount) ** 2 for x in purchase_amounts) / len(purchase_amounts)
        std_deviation = sqrt(variance)
        return std_deviation, mean_amount

    @staticmethod
    def analyze_product_and_brand_preferences(purchase_history, top_n=3):
        data = sum(purchase_history.values(), [])
        product_counts = Counter(item['articul'] for item in data)
        brand_counts = Counter(item['brand_title'] for item in data)

        most_common_product, product_count = product_counts.most_common(1)[0]
        most_common_brand, brand_count = brand_counts.most_common(1)[0]
        top_products = product_counts.most_common(top_n)
        top_brands = brand_counts.most_common(top_n)

        results = {
            'most_common_product': (most_common_product, product_count),
            'most_common_brand': (most_common_brand, brand_count),
            'top_products': top_products,
            'top_brands': top_brands
        }
        return results

    @staticmethod
    def get_total_purchases(purchase_history):
        total_purchases = sum(item['price_sell'] * item['amount'] for item in sum(purchase_history.values(), []))
        return total_purchases

    @staticmethod
    def get_purchase_history_str(purchase_history):
        purchase_history_str = '**Client purchase history:**\n'
        for key in purchase_history:
            purchase_history_str += f'Date: {key}\n'
            for item in purchase_history[key]:
                purchase_history_str += f"{item['id']} ({item['articul']} {item['brand_title']}) " + \
                                        f"margin: {round(item['margin'], 2)}%, sell: {item['price_sell']}$ qty. {item['amount']}\n"
            purchase_history_str += '\n'
        return purchase_history_str

    @staticmethod
    def summarize_client_metrics(purchase_history):
        average_bill_per_deal = ClientStatisticsService.get_average_bill_per_deal(purchase_history)
        total_margin_percentage = ClientStatisticsService.get_total_margin(purchase_history)
        average_interval, average_interval_months = ClientStatisticsService.avg_interval_between_purchases(purchase_history)
        total_purchases = ClientStatisticsService.get_total_purchases(purchase_history)
        std_deviation, mean_amount = ClientStatisticsService.purchase_volume_variability(purchase_history)
        products_analysis = ClientStatisticsService.analyze_product_and_brand_preferences(purchase_history, top_n=3)
        client_loyalty_metrics = ClientStatisticsService.client_loyalty(purchase_history)

        client_metrics = [
            "**Client Purchase and Profitability Overview:**",
            f"Total margin: {total_margin_percentage:.2f}%",
            f"Average bill per deal: {average_bill_per_deal:.2f}",
            f"Average interval between purchases: {average_interval:.2f} days (~{average_interval_months:.2f} months)",
            f"Total purchases: {total_purchases:.2f}",
        ]

        client_metrics.append('\n**Purchase volume variability:**')
        if std_deviation == 0:
            client_metrics.append("All purchases involve the same number of items. No variability.")
        elif std_deviation < mean_amount * 0.1:  # Arbitrary threshold for low variability
            client_metrics.append("Low variability. Purchase volumes are relatively consistent.")
        else:
            client_metrics.append("High variability. Purchase volumes vary significantly.")

        client_metrics.append('\n**Product and brand preferences:**')
        client_metrics.append(f"Most common product: {products_analysis['most_common_product'][0]} (Purchased {products_analysis['most_common_product'][1]} times)")
        client_metrics.append(f"Most common brand: {products_analysis['most_common_brand'][0]} (Purchased {products_analysis['most_common_brand'][1]} times)")

        client_metrics.append("\n**Top 3 products:**")
        for product, count in products_analysis['top_products']:
            client_metrics.append(f"{product}: {count} times")

        client_metrics.append("\n**Top 3 brands:**")
        for brand, count in products_analysis['top_brands']:
            client_metrics.append(f"{brand}: {count} times")

        client_metrics.append('\n**Client loyalty:**')
        for client_id, metrics in client_loyalty_metrics.items():
            client_metrics.append(f"Client ID {client_id}: Duration of Business Relationship: {metrics['Duration Years']:.2f} years ({metrics['Duration Days']} days)")
            client_metrics.append(f"Frequency of Repeat Purchases: {metrics['Repeat Purchases']} times")

        return '\n'.join(client_metrics)

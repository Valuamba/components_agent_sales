import requests


def send_message_to_telegram_group(message, thread_id):
    bot_token = '7091099686:AAHm31jtRiNHnUNOEiHa28tcnxJ33AGDTUQ'
    chat_id = '-1002129058709'
    send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    print(f'Thread: {thread_id}')

    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'message_thread_id': thread_id
    }

    response = requests.post(send_message_url, data=params)
    if response.status_code == 200:
        print('Message sent successfully')
    else:
        print(f'Failed to send message: {response.content}')
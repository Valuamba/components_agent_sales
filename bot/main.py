import asyncio
import logging
import os
import sys
import traceback
from os import getenv

import requests
from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from dotenv import load_dotenv

import logger

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

logger.setup_logger()


def format_response(details):
    """
    Formats the classification response into a more readable structure for the user,
    including emojis for visual feedback on the status of each action, and handles different
    types of actions differently.
    """
    # Emoji for status
    passed_emoji = "\U0001F7E2"  # Green circle
    failed_emoji = "\U0001F534"  # Red circle

    response_message = f"<b>Run ID</b>: {details['run']['run_id']}\n\n"
    response_message += "<b>Actions:</b>\n"

    for action in details['actions']:
        action_name = action['action']['action_name']
        action_id = action['action']['action_id']
        action_status = action['action']['action_status']
        status_emoji = passed_emoji if action_status == 1 else failed_emoji
        action_status_text = "Passed" if action_status == 1 else "Failed"

        if 'error' in action and action['error']:
            action_details = f"Error: {action['error']['message']}"
        elif action_name == "classify_intents" and 'data' in action and action['data']:
            # Format for classify_intents action
            intents = "\n".join([
                f"- Intent: {intent['intent']}\n  Sub-intent: {intent['sub_intent']}\n  Branch: {intent['branch']}"
                for intent in action['data']
            ])
            action_details = f"Details:\n<pre>{intents}</pre>"
        elif action_name == "classify_contacts" and 'data' in action:
            person = action['data']
            contact_info = person.get('contact', {})
            addresses_info = contact_info.get('addresses', [{}])[0]  # Safely get the first address

            # Compile contact details ensuring no None values slip through
            contacts_details = (
                f"- Name: {person.get('name', 'N/A')}\n"
                f"  Title: {person.get('title', 'N/A')}\n"
                f"  Company: {person.get('company', 'N/A')}\n"
                f"  Email: {contact_info.get('email', 'N/A')}\n"
                f"  Phone: {contact_info.get('office_phone', 'N/A')}\n"
                f"  Address: {addresses_info.get('street', 'N/A')}, {addresses_info.get('city', 'N/A')}"
            )
            action_details = f"Details:\n<pre>{contacts_details}</pre>"
        else:
            action_details = "No additional details available"

        response_message += f"\n<b>Action {action_id} - {action_name}</b> {status_emoji} {action_status_text}\n{action_details}\n"

    response_message += "\n<b>Tasks:</b>\n"
    for task in details['tasks']:
        response_message += f"Task: <code>{task['summary']}</code>\n"

    return response_message



# @dp.message(CommandStart())
# async def command_start_handler(message: types.Message) -> None:

@dp.message()
async def echo_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command.
    If the message is numeric, it processes it as a request ID to fetch an email message body.
    """
    if message.text.isdigit():  # Check if the message text is numeric
        request_id = int(message.text)  # Convert text to an integer as request ID
        logging.info(f"Received numeric request ID: {request_id}")
        try:
            # Fetch the email content associated with the request ID
            messaging_history = process_request(request_id)
            if 'content' in messaging_history and messaging_history['content']:
                body = messaging_history['content'][0]['body']  # Extract body from the first item
                logging.info("Email content successfully retrieved")

                try:
                    intents_details = classify_intents(request_id, body)
                    if 'error' in intents_details:
                        raise ValueError(intents_details['error']['message'])

                    formatted_response = format_response(intents_details)
                    await message.answer(formatted_response, parse_mode='HTML')
                except KeyError:
                    await message.answer(
                        "There was an error processing the intents. Please check the log for more details.")
                    logging.error("Key error in handling the response from classify_intents.")
            else:
                await message.answer("No content found for the provided request ID.")
        except Exception as e:
            tb = traceback.format_exc()
            logging.error(f"Failed to process request: {str(e)}\nTraceback: {tb}")
            await message.answer(f"Failed to process request: {str(e)}")
    else:
        await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

    # Function to fetch the email message body using the request ID


def process_request(request_id):
    url = f'https://api.famaga.org/imap/deal/{request_id}'
    headers = {
        'Authorization': 'Bearer YXBpZmFtYWdhcnU6RHpJVFd1Lk1COUV4LjNmdERsZ01YYlcvb0VFcW9NLw',
        'Cookie': 'PHPSESSID=8gv7kd7lne3dfu5jk7kqpkfj36'
    }
    logging.info(f"Sending request to URL: {url}")
    response = requests.get(url, headers=headers)
    logging.info(f"Response status code: {response.status_code}")
    return response.json()



def classify_intents(deal_id, body):
    url = f'{os.getenv('AGENT_URL')}/v2/agent/handle_messages/html'
    data = {
        "deal_id": str(deal_id),
        "messages_html": body
    }
    logging.info("Sending request for intent classification")
    response = requests.post(url, json=data)
    logging.info(f"Received response with status code: {response.status_code}")
    return response.json()




async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
import asyncio
import json
import logging
import os
import sys
import traceback
import uuid
from os import getenv

import aiohttp
import httpx
import requests
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery

from dotenv import load_dotenv

import redis.asyncio as redis

import logger
from utils import get_user_id

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)

REDIS_HOST = getenv("REDIS_HOST")
REDIS_URI = f'redis://{REDIS_HOST}:6379/1'


storage = MemoryStorage()  #
dp = Dispatcher(storage=storage)

logger.setup_logger()


class Form(StatesGroup):
    leave_feedback = State()

class FeedbackCallback(CallbackData, prefix="feedback"):
    run_uuid: str

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
        elif action['ui_message']:
            action_details = action['ui_message']
        else:
            action_details = "No additional details available"

        response_message += f"\n<b>Action {action_id} - {action_name}</b> {status_emoji} {action_status_text}\n{action_details}\n"

    response_message += "\n<b>Tasks:</b>\n"
    for task in details['tasks']:
        response_message += f"Task: <code>{task['summary']}</code>\n"

    return response_message


@dp.message(Command("help"))
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=
                                                          [
                                                              [InlineKeyboardButton(
                                                                  text=' 💬 Leave Feedback',
                                                                  callback_data=FeedbackCallback(
                                                                      run_id=118).pack())]

                                                          ]))


@dp.message(Command("start"))
async def send_start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.update_data({})
    await message.reply("Hi!\nPlease send me deal ID.")


CHAT_ID = '6102292898'


async def redis_listener(bot: Bot) -> None:
    redis_client = redis.from_url(REDIS_URI, encoding="utf-8")
    pubsub = redis_client.pubsub()

    try:
        logging.info(f"Redis subscribe: {REDIS_URI}")
        await pubsub.subscribe("workflow_updates")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    run_uuid = message["data"].decode("utf-8")
                    user_message_info = await redis_client.get(run_uuid)
                    user_id, message_id = map(int, user_message_info.decode("utf-8").split(":"))

                    # Retrieve the list of error messages
                    messages = await redis_client.lrange(f"{run_uuid}_actions", 0, -1)
                    combined_message = "\n".join(msg.decode("utf-8") for msg in messages)

                    markup = await get_inline_keyboard_markup(redis_client, run_uuid)
                    markup.inline_keyboard.append(
                        [InlineKeyboardButton(text=' 💬 Leave Feedback', callback_data=FeedbackCallback(run_uuid=run_uuid).pack())]
                    )

                    try:
                        await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=combined_message,
                                                    reply_markup=markup)
                        logging.info(f"Updated message for run_uuid {run_uuid}")
                    except Exception as e:
                        logging.error(f"Failed to update message for run_uuid {run_uuid}: {e}")

                    # await bot.send_message(chat_id=CHAT_ID, text=message["data"])
                    # logging.info(f"Message sent to chat {CHAT_ID}: {message['data']}")
                except Exception as e:
                    logging.error(f"Failed to send message to chat {CHAT_ID}: {e}")
    except Exception as e:
        logging.error(f"Failed to listen to Redis channel 'workflow_updates': {e}")
    finally:
        await redis_client.aclose()
        logging.info("Closed Redis connection")


# async def redis_listener(bot: Bot):
#     redis = await aioredis.from_url(REDIS_URI, encoding="utf-8")
#     res = await redis.subscribe("workflow_updates")
#     channel = res[0]
#     while await channel.wait_message():
#         msg = await channel.get()
#         await bot.send_message(chat_id=6102292898, text=msg)
        # await bot.edit_message_text(chat_id=CHAT_ID, message_id=MESSAGE_ID, text=f"{msg}\n")

async def store_email_subject_and_url(redis_client, run_uuid: str, subject, url, ttl_seconds):
    """
    Store email subject and URL in a Redis hash with TTL.

    Args:
    - subject: The email subject to store.
    - url: The URL corresponding to the email subject.
    - ttl_seconds: Time to live (TTL) in seconds for the Redis hash.
    """
    # Store email subject and URL in the Redis hash
    await redis_client.hset(f'{run_uuid}_subjects', subject, url)
    await redis_client.expire(f'{run_uuid}_subjects', ttl_seconds)


async def get_inline_keyboard_markup(redis_client, run_uuid: str) -> InlineKeyboardMarkup:
    email_subjects_urls = await redis_client.lrange(f'{run_uuid}_subjects_urls', 0, -1)
    inline_keyboard_buttons = []

    for subject_url in email_subjects_urls:
        data = json.loads(subject_url.decode())  # Parse the JSON
        inline_keyboard_buttons.append([InlineKeyboardButton(text=data['subject'], url=data['url'])])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard_buttons)


@dp.message(Form.leave_feedback)
async def handle_leave_feedback_query(message: Message,  bot: Bot, state: FSMContext):
    data = await state.get_data()
    await message.answer(text=f"Feedback leaved {data['run_uuid']}")
    send_feedback(data['run_uuid'], message.text, 0, [])
    await state.clear()
    await state.update_data({})
# @dp.message(CommandStart())
# async def command_start_handler(message: types.Message) -> None:


def send_feedback(run_uuid, feedback, is_like, issues):
    url = f'{os.getenv('AGENT_URL')}/v2/run/feedback/'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'run_uuid': run_uuid,
        'feedback': feedback,
        'is_like': is_like,
        'issues': issues
    }
    response = requests.post(url, headers=headers, json=data)
    return response

@dp.message()
async def echo_handler(message: Message, bot: Bot) -> None:
    redis_client = redis.from_url(REDIS_URI, encoding="utf-8")
    storage_domain = os.getenv("STORAGE_DOMAIN")
    """
    This handler receives messages with `/start` command.
    If the message is numeric, it processes it as a request ID to fetch an email message body.
    """
    # await message.answer("kek", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
    #     [
    #         InlineKeyboardButton(text="test", web_app=WebAppInfo(url="https://neon-dev.us/deals/397966"))
    #     ]
    # ]))

    if message.text.isdigit():  # Check if the message text is numeric
        request_id = int(message.text)  # Convert text to an integer as request ID
        logging.info(f"Received numeric request ID: {request_id}")
        try:
            # Fetch the email content associated with the request ID
            messaging_history = process_request(request_id)

            directory_path = os.getenv('MESSAGES_DIRECTORY_PATH', os.path.join(os.getcwd(), 'messages'))
            os.makedirs(directory_path, exist_ok=True)

            for email_msg in messaging_history['content']:
                file_path = os.path.join(directory_path, f'{email_msg["uid"]}.html')
                with open(file_path, 'w') as file:
                    file.write(email_msg['body'])

            if 'content' in messaging_history and messaging_history['content']:
                body = messaging_history['content'][0]['body']  # Extract body from the first item
                logging.info("Email content successfully retrieved")

                run_uuid = uuid.uuid4()

                for index, email_msg in enumerate(messaging_history['content']):
                    data = {"subject": email_msg['subject'], "url": f"{storage_domain}/deals/{email_msg['uid']}"}
                    await redis_client.rpush(f'{run_uuid}_subjects_urls', json.dumps(data))

                await redis_client.expire(f'{run_uuid}_subjects_urls', 3000)

                try:
                    msg = await message.reply("Start processing...", reply_markup=InlineKeyboardMarkup(inline_keyboard=
                                                        [
                           [
                               InlineKeyboardButton(text=email_msg['subject'] + (" ⭐️" if index == 0 else ""),
                                                 url=f"{storage_domain}/deals/{email_msg['uid']}")
                            ]
                                                                               for index, email_msg in
                                                                               enumerate(messaging_history['content'])
                                                                           ]
                                                                           ))

                    await redis_client.set(str(run_uuid), f"{get_user_id(message)}:{msg.message_id}")

                    intents_details = await discount_processing(run_uuid, request_id, body)
                    if 'error' in intents_details:
                        raise ValueError(intents_details['error']['message'])

                    formatted_response = format_response(intents_details)

                    # markup = await get_inline_keyboard_markup(redis_client, str(run_uuid))
                    # markup.inline_keyboard.append([InlineKeyboardButton(
                    #     text=' 💬 Leave Feedback',
                    #     callback_data=FeedbackCallback(run_id=intents_details['run']['run_id']).pack())])
                    #
                    # await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=msg.message_id,
                    #                                     reply_markup=markup)
                    # await message.answer(formatted_response, parse_mode='HTML',
                    #                      reply_markup=InlineKeyboardMarkup(inline_keyboard=
                    #                                     [
                    #                                                            [InlineKeyboardButton(
                    #                                                                text=email_msg['subject'] + (
                    #                                                                    " ⭐️" if index == 0 else ""),
                    #                                                                url=f"{storage_domain}/deals/{email_msg['uid']}"
                    #                                                            )]
                    #                                                            for index, email_msg in
                    #                                                            enumerate(messaging_history['content'])
                    #                                                        ] + [
                    #                                                            [InlineKeyboardButton(
                    #                                                                text=' 💬 Leave Feedback',
                    #                                                                callback_data=FeedbackCallback(run_id=intents_details['run']['run_id']).pack())]
                    #                                                        ]
                    #                                                        ))
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


# @dp.message(Form.leave_feedback)
# async def handle_leave_feedback_query(ctx: Message,  bot: Bot, state: State):
#     ctx.


@dp.callback_query(FeedbackCallback.filter())
async def handle_feedback_message(ctx: CallbackQuery, callback_data: FeedbackCallback, bot: Bot, state: FSMContext):
    await state.update_data(run_uuid=callback_data.run_uuid)
    await state.set_state(Form.leave_feedback)
    # logger.info(f'User: {get_user_id(ctx)}. Handler: feedback message.')
    await bot.send_message(get_user_id(ctx), "Please leave feedback or input /start to cancel.")
                           # reply_markup=InlineKeyboardMarkup(inline_keyboard=
                           #      [
                           #          [InlineKeyboardButton(text=' 💬 Submit', callback_data="feedback:")],
                           #          [InlineKeyboardButton(text=' 💬 Cancel', callback_data="canceled")],
                           #      ]))
    # ctx.


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


async def discount_processing(run_uuid, deal_id, body):
    url = f'{os.getenv("AGENT_URL")}/v2/agent/discount/html'
    data = {
        "run_uuid": str(run_uuid),
        "deal_id": str(deal_id),
        "messages_html": body
    }

    logging.info("Sending request for intent classification")

    async with httpx.AsyncClient(timeout=httpx.Timeout(300)) as client:
        response = await client.post(url, json=data)
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e}")
            # Handle HTTP error here, e.g., return an error response
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            # Handle other exceptions here, e.g., return an error response


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    listener_task = asyncio.create_task(redis_listener(bot))
    await dp.start_polling(bot)
    await listener_task


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

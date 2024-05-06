from aiogram.types import CallbackQuery, Message, PreCheckoutQuery


def get_user_id(update):
    if isinstance(update, CallbackQuery):
        return update.from_user.id
    elif isinstance(update, Message):
        return update.from_user.id
    elif isinstance(update, PreCheckoutQuery):
        return update.from_user.id

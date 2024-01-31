from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, InlineKeyboardButton,
                           InlineKeyboardMarkup)

kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Текущий баланс')],
                                    [KeyboardButton(text='Текущий курс')],
                                    [KeyboardButton(text='Изменить баланс')]])

def get_inline_kb_get(codes):
    buttons = []
    for code in codes:
        buttons.append(InlineKeyboardButton(
            text=code,
            callback_data=f'get_{code.lower()}'
        ))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

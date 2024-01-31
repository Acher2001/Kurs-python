from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, InlineKeyboardButton,
                           InlineKeyboardMarkup)

kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Текущий баланс')],
                                    [KeyboardButton(text='Текущий курс')],
                                    [KeyboardButton(text='Изменить баланс')]])

def get_inline_kb(codes, method):
    buttons = [[]]
    for code in codes:
        buttons[0].append(InlineKeyboardButton(
            text=code,
            callback_data=f'{method}_{code.lower()}'
        ))
    if method == 'post':
        buttons.append([InlineKeyboardButton(text='Отмена',
                        callback_data='post_cancel')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

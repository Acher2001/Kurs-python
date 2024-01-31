from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)

kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Текущий баланс')],
                                    [KeyboardButton(text='Текущий курс')],
                                    [KeyboardButton(text='Изменить баланс')]])

import aiohttp
import asyncio
import logging
import argparse
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config
from currency import Currency, BaseCurrency, display_currencies
from bot_features.keyboards import kb, get_inline_kb

CODES = ['RUB', 'EGP', 'EUR']
curr_code = None

#----------API modules------------------------
async def web_get_currency(request):
    global valutes, valutes_dict
    if request.match_info.get('name').upper() in valutes_dict:
        cur = valutes_dict[request.match_info.get('name').upper()]
    else:
        return web.Response(body='unknown currency code')
    if cur.code == 'RUB':
        return web.Response(body=f'rub: {cur.amount}')
    else:
        return web.Response(body=f'{cur.code.lower()}: {cur.amount}\n{valutes[0].get_rel_rate(cur)[1]}')

async def web_get_amount(request):
    global valutes
    return web.Response(body=display_currencies(valutes))

async def web_set_amount(request):
    global valutes_dict
    data = await request.json()
    for key in data:
        if key.upper() in valutes_dict:
            valutes_dict[key.upper()].set_amount(data[key])

async def web_modify(request):
    global valutes_dict
    data = await request.json()
    for key, val in data.items():
        if key.upper() in valutes_dict:
            valutes_dict[key.upper()].set_amount(valutes_dict[key.upper()].amount + val)


async def init_app():
    app = web.Application()
    app.router.add_routes([
        web.get('/amount/get', web_get_amount),
        web.get('/{name}/get', web_get_currency),
        web.post('/amount/set', web_set_amount),
        web.post('/modify', web_modify),
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
#--------------------------------------------

#-----------Telegram bot---------------------
def config_bot():
    config = load_config()
    bot = Bot(config.bot.token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    return bot, dp

class FSMPutData(StatesGroup):
    get_method = State()
    set_val = State()
    modify_val = State()
    set_amount = State()
    modify_amount = State()

bot, dp = config_bot()

@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer(text='Привет!\nЭтот бот создан для того, чтобы сообщать о текущих курсах валют\nОтпарвь команду /help, чтобы узнать что он может.',
                         reply_markup=kb)


@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(
        'Напиши мне что-нибудь и в ответ '
        'я пришлю тебе твое сообщение'
    )

@dp.message(F.text == 'Текущий баланс')
async def process_get_amount(message:Message):
    global valutes
    await message.answer(display_currencies(valutes))

@dp.message(F.text == 'Текущий курс')
async def process_get_amount(message:Message):
    global valutes
    await message.answer(text='Курс какой валюты вы хотите узнать?',
                         reply_markup=get_inline_kb(CODES, 'get'))

@dp.callback_query(F.data.in_([f'get_{code.lower()}' for code in CODES]))
async def process_get_cur(callback:CallbackQuery):
    await callback.answer()
    code = callback.data[4:].upper()
    cur = valutes_dict[code]
    if cur.code == 'RUB':
        await callback.message.answer(text=f'rub: {cur.amount}')
    else:
        await callback.message.answer(text=f'{cur.code.lower()}: {cur.amount}\n{valutes[0].get_rel_rate(cur)[1]}')

@dp.callback_query(F.data == 'post_cancel', ~StateFilter(default_state))
async def process_cancel(callback:CallbackQuery, state:FSMContext):
    global curr_code
    await callback.message.delete()
    curr_code = None
    await state.set_state(default_state)

@dp.message(F.text == 'Изменить баланс', StateFilter(default_state))
async def process_post_req(message:Message, state:FSMContext):
    await message.answer(text='Выберите способ изменения',
                         reply_markup=get_inline_kb(['Добавить', 'Обновить'], method='post'))
    await state.set_state(FSMPutData.get_method)

@dp.callback_query(F.data == 'post_добавить', StateFilter(FSMPutData.get_method))
async def process_post_modify(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await callback.message.edit_text(text='Выберите изменяемую валюту',
                                  reply_markup=get_inline_kb(CODES, 'post'))
    await state.set_state(FSMPutData.modify_val)

@dp.callback_query(F.data == 'post_обновить', StateFilter(FSMPutData.get_method))
async def process_post_set(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await callback.message.edit_text(text='Выберите изменяемую валюту',
                                  reply_markup=get_inline_kb(CODES, 'post'))
    await state.set_state(FSMPutData.set_val)

@dp.callback_query(F.data.in_([f'post_{code.lower()}' for code in CODES]), StateFilter(FSMPutData.modify_val))
async def process_post_modify_val(callback:CallbackQuery, state:FSMContext):
    global curr_code
    code = callback.data[5:]
    curr_code = code.upper()
    await callback.message.edit_text(text=f'Введите добавляемое к {code} число',
                                     reply_markup=get_inline_kb([], 'post'))
    await state.set_state(FSMPutData.modify_amount)

@dp.callback_query(F.data.in_([f'post_{code.lower()}' for code in CODES]), StateFilter(FSMPutData.set_val))
async def process_post_set_val(callback:CallbackQuery, state:FSMContext):
    global curr_code
    code = callback.data[5:]
    curr_code = code.upper()
    await callback.message.edit_text(text=f'Введите новое значение {code}',
                                     reply_markup=get_inline_kb([], 'post'))
    await state.set_state(FSMPutData.set_amount)

@dp.message(StateFilter(FSMPutData.modify_amount), F.text.isdigit())
async def process_post_modify_amount(message:Message, state:FSMContext):
    global valutes_dict, curr_code
    amount = int(message.text)
    valutes_dict[curr_code].set_amount(valutes_dict[curr_code].amount+amount)
    await message.answer(text='Успешно')
    await state.set_state(default_state)
    curr_code = None

@dp.message(StateFilter(FSMPutData.set_amount), F.text.isdigit())
async def process_post_modify_amount(message:Message, state:FSMContext):
    global valutes_dict, curr_code
    amount = int(message.text)
    valutes_dict[curr_code].set_amount(amount)
    await message.answer(text='Успешно')
    await state.set_state(default_state)
    curr_code = None

@dp.message(StateFilter(FSMPutData.set_amount, FSMPutData.modify_amount))
async def process_post_not_digit(message:Message):
    await message.answer('Пожалуйста введите число')
#--------------------------------------------


async def fetch_data(period, lock, url='https://www.cbr-xml-daily.ru/daily_utf8.xml'):
    """Получаем данные о курсе валют в формате xml"""
    global data
    while True:
        await lock.acquire()
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.text()
        lock.release()
        await asyncio.sleep(60*period)

async def console(valutes, lock):
    """Асинхронный поток для вывода данных в консоль"""
    force = True
    global data
    while True:
        await lock.acquire()
        for cur in valutes[1:]:
            cur.process_rates(data)
        if any([cur.is_changed() for cur in valutes]) or force:
            print(display_currencies(valutes))
        force = False
        lock.release()
        await asyncio.sleep(60)


async def test():
    while True:
        print('works')
        await asyncio.sleep(2)

async def main():
    """Запускаем сервисы в цикл"""
    global valutes, args, data
    period = args.period
    data_lock = asyncio.Lock()
    tasks = [dp.start_polling(bot), fetch_data(period, data_lock), console(valutes, data_lock), init_app()]
    await asyncio.gather(*tasks)


def parse_args():
    parser = argparse.ArgumentParser(description='Currency exchange rates')
    parser.add_argument('--rub', type=float, default=1.0, help='Initial amount in RUB')
    parser.add_argument('--egp', type=float, default=1.0, help='Initial amount in EGP')
    parser.add_argument('--eur', type=float, default=1.0, help='Initial amount in EUR')
    parser.add_argument('--period', type=int, default=10, help='Period in minutes')
    parser.add_argument('--debug', default=False, action='store_true', help='Enable debug mode')
    return parser.parse_args()

if __name__ == '__main__':
    data = None
    args = parse_args()
    rub = BaseCurrency(code='RUB', name='Российский рубль', amount=args.rub)
    egp = Currency(code='EGP', amount=args.egp)
    eur = Currency(code='EUR', amount=args.eur)
    valutes = [rub, egp, eur]
    valutes_dict = {'RUB':rub, 'EGP':egp, 'EUR':eur}
    asyncio.run(main())

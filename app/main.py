import aiohttp
import asyncio
import logging
import argparse
from aiohttp import web

from currency import Currency, BaseCurrency, display_currencies

#----------API modules------------------------
async def web_get_currency(request):
    global valutes
    for cur in valutes:
        if cur.code.lower() == request.match_info.get('name'):
            currency = cur
            break
    if cur.code == 'RUB':
        return web.Response(body=f'rub: {cur.amount}')
    else:
        return web.Response(body=f'{cur.code.lower()}: {cur.amount}\n{valutes[0].get_rel_rate(cur)[1]}')

async def init_app():
    app = web.Application()
    app.router.add_routes([
        web.get('/{name}/get', web_get_currency)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
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
    tasks = [fetch_data(period, data_lock), console(valutes, data_lock), init_app()]
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
    asyncio.run(main())

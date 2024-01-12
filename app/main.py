import aiohttp
import asyncio
import logging

from currency import Currency, BaseCurrency

async def fetch_data(url='https://www.cbr-xml-daily.ru/daily_utf8.xml'):
    """Получаем данные о курсе валют в формате xml"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

def display_currencies(valutes):
    """Возвращает строку с курсом валют"""
    result = ''
    for i, cur1 in enumerate(valutes[:-1]):
        for cur2 in valutes[i+1:]:
            result += cur1.get_rel_rate(cur2)[1] + '\n'
    return result

async def main():
    """Запускаем сервисы в цикл"""
    global data, valutes
    old_data = data
    data = await fetch_data()
    for cur in valutes[1:]:
        cur.process_rates(data)
    print(display_currencies(valutes))


if __name__ == '__main__':
    data = None
    rub = BaseCurrency(code='RUB', name='Российский рубль')
    egp = Currency(code='EGP')
    eur = Currency(code='EUR')
    valutes = [rub, egp, eur]
    asyncio.run(main())

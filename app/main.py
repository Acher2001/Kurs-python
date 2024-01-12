import aiohttp
import asyncio
import logging

from currency import Currency, BaseCurrency

async def fetch_data(url='https://www.cbr-xml-daily.ru/daily_utf8.xml'):
    """Получаем данные о курсе валют в формате xml"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def main():
    """Запускаем сервисы в цикл"""
    pass

if __name__ == '__main__':
    asyncio.run(main())

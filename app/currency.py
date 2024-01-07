import aiohttp
import xml.etree.ElementTree as ET
import asyncio

class Currency:
    def __init__(self, code, debug=False, amount=1, url='https://www.cbr-xml-daily.ru/daily_utf8.xml'):
        self.code = code
        self.debug = debug
        self.amount = amount
        self.url = url
        self.name = None
        asyncio.run(self.process_rates())

    async def fetch_rates(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                return await response.text()


    async def process_rates(self):
        data = await self.fetch_rates()
        root = ET.fromstring(data)
        currency = None
        for cur in root.findall('.//Valute'):
            code = cur.find('CharCode').text
            if code == self.code:
                currency = cur
                break
        if not currency:
            raise ValueError('Неверный код валюты')
        if not self.name:
            self.name = cur.find('Name').text
        self.value = float(cur.find('Value').text.replace(',', '.'))
        if self.debug:
            return currency.text

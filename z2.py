import asyncio
import argparse
import aiohttp
from xml.etree import ElementTree as ET

async def fetch_exchange_rate(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

def parse_exchange_rate(xml_data, currency_code):
    root = ET.fromstring(xml_data)
    if currency_code == 'RUB':
        return 1.0  # Если валюта RUB, возвращаем 1.0, так как это базовая валюта
    for rate in root.findall(".//Valute"):
        char_code = rate.find("CharCode").text
        if char_code == currency_code:
            value = rate.find("Value").text
            return float(value.replace(',', '.'))
    return None

async def main(period, url, currencies, initial_balances):
    balances = {currency: initial_balances.get(currency, 0.0) for currency in currencies}

    while True:
        xml_data = await fetch_exchange_rate(url)

        for currency in currencies:
            exchange_rate = parse_exchange_rate(xml_data, currency)
            if exchange_rate is not None:
                balances[currency] *= exchange_rate
                print(f"Баланс {currency}: {balances[currency]:.2f} RUB")
            else:
                print(f"Не удалось получить курс {currency}")

        await asyncio.sleep(period * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Получение данных о курсе валют каждые N минут.")
    parser.add_argument("--period", type=int, help="Период обновления в минутах", required=True)
    parser.add_argument("--url", type=str, default="https://www.cbr-xml-daily.ru/daily_utf8.xml", help="URL источника данных")
    parser.add_argument("--currencies", nargs='+', help="Список валют для отслеживания", required=True)
    parser.add_argument("--initial_balances", nargs='*', type=float, help="Начальный баланс для каждой валюты")
    args = parser.parse_args()

    if args.initial_balances is not None and len(args.currencies) != len(args.initial_balances):
        print("Ошибка: Количество валют должно соответствовать количеству начальных балансов.")
        exit()

    asyncio.run(main(args.period, args.url, args.currencies, dict(zip(args.currencies, args.initial_balances))))

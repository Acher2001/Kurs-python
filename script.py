import argparse
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import logging

async def fetch_currency_rates(url, debug=False):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if debug:
                logging.debug(f"Request URL: {url}")
                logging.debug(f"Response Status: {response.status}")
                logging.debug(f"Response Content: {await response.text()}")
            return await response.text()

async def process_currency_rates(period, url, initial_values, debug=False):
    while True:
        xml_data = await fetch_currency_rates(url, debug)
        root = ET.fromstring(xml_data)

        base_currency_code = "RUB"
        base_currency_value = 1.0

        for currency in root.findall('.//Valute'):
            code = currency.find('CharCode').text
            name = currency.find('Name').text
            value = float(currency.find('Value').text.replace(',', '.'))

            if code == base_currency_code:
                base_currency_value = value

        currencies_to_display = ["EUR", "EGP"]
        print("RUB (рубль): 1.0")
        for currency_code in currencies_to_display:
            for currency in root.findall('.//Valute'):
                if currency.find('CharCode').text == currency_code:
                    name = currency.find('Name').text
                    value = float(currency.find('Value').text.replace(',', '.'))
                    print(f"{currency_code} ({name}): {value / base_currency_value:.6f} ({initial_values[currency_code]} {currency_code})")

        if not debug:
            total_amount = sum(value * initial_values[code] / base_currency_value for code, value in initial_values.items())
            logging.info(f"Total amount in RUB: {total_amount:.6f}")

        await asyncio.sleep(period * 60)

def parse_args():
    parser = argparse.ArgumentParser(description='Currency Exchange Rate Checker')
    parser.add_argument('--rub', type=float, default=1.0, help='Initial amount in RUB')
    parser.add_argument('--egp', type=float, default=1.0, help='Initial amount in EGP')
    parser.add_argument('--eur', type=float, default=1.0, help='Initial amount in EUR')
    parser.add_argument('--period', type=int, default=10, help='Period in minutes')
    parser.add_argument('--debug', default=False, action='store_true', help='Enable debug mode')
    return parser.parse_args()

async def main():
    args = parse_args()
    initial_values = {
        'RUB': args.rub,
        'EGP': args.egp,
        'EUR': args.eur,
    }
    currency_url = "https://www.cbr-xml-daily.ru/daily_utf8.xml"
    period = args.period

    if period <= 0:
        print("Период должен быть положительным числом.")
        return

    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Application started.")

    await process_currency_rates(period, currency_url, initial_values, args.debug)

if __name__ == "__main__":
    asyncio.run(main())

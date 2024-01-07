import xml.etree.ElementTree as ET

class Currency:
    def __init__(self, data, code, amount=1, debug=False):
        self.code = code
        self.debug = debug
        self.amount = amount
        self.name = None
        self.process_rates(data)


    def process_rates(self, data):
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

    def get_rel_rate(self, another):
        rel_rate = round(another.value / self.value, 2)
        return rel_rate, f'{self.code.lower()}-{another.code.lower()}: {rel_rate}'

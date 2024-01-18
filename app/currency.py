import xml.etree.ElementTree as ET


class BaseCurrency:
    def __init__(self, code, amount=1, debug=False, name=None):
        self.code = code
        self.debug = debug
        self.amount = amount
        self.name = name
        self.value = 1
        self.old_amount = self.amount

    def get_rel_rate(self, another):
        rel_rate = round(another.value / self.value, 2)
        return rel_rate, f'{self.code.lower()}-{another.code.lower()}: {rel_rate}'

    def get_sum(self, another):
        result = 0
        for cur in another:
            result += cur.amount * self.get_rel_rate(cur)[0]
        result += self.amount
        return result

    def is_changed(self):
        if self.amount != self.old_amount:
            self.old_amount = self.amount
            return True
        return False

    def set_amount(self, amount):
        self.old_amount = self.amount
        self.amount = amount

class Currency(BaseCurrency):
    def __init__(self, code, data=None, amount=1, debug=False):
        super().__init__(code=code, amount=amount, debug=debug)
        self.old_value = self.value
        if data:
            self.process_rates(data=data)



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
        self.old_value = self.value
        self.value = float(cur.find('Value').text.replace(',', '.'))
        if self.debug:
            return currency.text

    def is_changed(self):
        amount_changed = super().is_changed()
        value_changed = True if self.value != self.old_value else False
        self.old_value = self.value
        return amount_changed or value_changed

def display_currencies(valutes):
    """Возвращает строку с курсом валют"""
    result = ''
    for cur in valutes:
        result += f'{cur.code}: {cur.amount}\n'
    result += '\n'
    for i, cur1 in enumerate(valutes[:-1]):
        for cur2 in valutes[i+1:]:
            result += cur1.get_rel_rate(cur2)[1] + '\n'
    result += '\n'
    sums = []
    for i, cur in enumerate(valutes):
        another = valutes[:i] + valutes[i+1:]
        sums.append(f'{round(cur.get_sum(another),2)}: {cur.code.lower()}')
    result += 'sum: ' + ' / '.join(sums)
    return result

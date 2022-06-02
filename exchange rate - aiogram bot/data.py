import requests
from lxml import html
from settings import URL
from decimal import Decimal


class CurrencyData:

    def __init__(self):
        self.rus_names = {}
        self.available_rus = {}
        self.available_iso = {}

    # русские названия валют, с iso-кодами и странами
    def get_rus_names(self) -> dict:

        # парсит с сайта общероссийских классификаторов
        url = URL['iso']
        response = requests.get(url)
        tree = html.fromstring(response.content)
        currencies = tree.xpath('/html/body/div/div[4]/div[10]/div/table/tbody')[0]

        for currency in currencies:

            # убирает исключённые позиции
            if currency.xpath('./@class') == ['annulled']:
                continue

            name = currency.xpath('./td[1]/text()')
            iso_code = currency.xpath('./td[2]/text()')

            self.rus_names[iso_code[0]] = name

        return self.rus_names

    # доступные для конвертации валюты с русскими названиями
    def get_available(self, dict_keys: str) -> dict:
        # база данных Европейской комиссии
        url = URL['api'] + '/lastest'
        response = requests.get(url)
        names_from_api = response.json()
        details = self.get_rus_names()

        for iso_code in names_from_api['rates']:
            if iso_code in details:
                self.available_rus[details[iso_code][0].lower()] = iso_code.lower()
                self.available_iso[iso_code.lower()] = details[iso_code][0].lower()

        # два варианта словаря: с ключами по iso или по русским названиям
        if dict_keys == 'rus':
            return self.available_rus
        elif dict_keys == 'iso':
            return self.available_iso


# производит конвертацию валюты
class ExchangeRate:

    def __init__(self, convert_from: str, to: str, amount: Decimal):
        self.convert_from = convert_from
        self.convert_to = to
        self.amount = amount
        self.url = URL['api'] + '/convert?'

    def converter(self) -> Decimal:

        url = self.url + f'from={self.convert_from}&to={self.convert_to}&amount={self.amount}'
        response = requests.get(url)
        data = response.json()
        result = Decimal(data['result']).quantize(Decimal('1.00'))

        return result


if __name__ == '__main__':

    d = CurrencyData()
    for di in d.get_available('iso'), d.get_available('rus'):
        for item in di.items():
            print(*item)

    req1 = ExchangeRate('USD', 'EUR', Decimal('10.4654181681'))
    print(req1.converter())

from decimal import Decimal, InvalidOperation
from data import CurrencyData


# ошибка отрицательного количества
class ImpossibleAmount(ValueError):

    def __init__(self, amount):
        self.amount = amount

    def __str__(self):
        return f'Кол-во валюты: {self.amount} — отрицательное значение недопустимо'


# ошибка недоступной валюты
class UnknownCurrency(Exception):

    def __init__(self, eng: bool = True):
        self.eng = eng

    def __str__(self):
        if not self.eng:
            error_message = 'Не могу найти. Используйте полные русские названия валют'
        else:
            error_message = 'Мне неизвестна эта валютная пара\n'
        return error_message


class CheckRequest:

    # принимает только сообщение от пользователя
    def __init__(self, message: str):
        self.message = message
        self.convert_from = ''
        self.convert_to = ''
        self.amount = ''
        self.errors = set()

    # возвращает текст ошибки либо приводит валюты к рабочему виду
    def check_arguments(self) -> str:
        try:
            from_, to_, amount = map(str.strip, self.message.split('/'))
        # срабатывает, если неверное количество аргументов или ввод не через /
        except ValueError:
            return (f'Не могу обработать запрос.\n'
                    f'Убедитесь, что вы ввели через / две валюты и количество.')

        try:
            d_rus = CurrencyData().get_available('rus')
            d_iso = CurrencyData().get_available('iso')
            from_ = from_.lower()
            to_ = to_.lower()

            # переводит русские названия в iso
            if 'а' <= from_[0] <= 'я':
                from_ = d_rus.get(from_, '')
            if 'а' <= to_[0] <= 'я':
                to_ = d_rus.get(to_, '')

            # проверяет, если ли такие валюты в API
            if from_ not in d_iso or to_ not in d_iso:
                raise UnknownCurrency()

        except UnknownCurrency:
            return str(UnknownCurrency(from_ and to_))

        else:
            self.convert_from = from_
            self.convert_to = to_
            self.amount = amount

    # возвращает текст ошибки либо приводит количество к рабочему виду
    def check_amount(self) -> str:
        try:
            self.amount = Decimal(self.amount.replace(',', '.')).quantize(Decimal('1.00'))
            if self.amount < 0:
                raise ImpossibleAmount(self.amount)
        # неправильный формат ввода
        except InvalidOperation:
            return 'Ошибка при вводе количества.'
        # отрицательное число
        except ImpossibleAmount:
            return str(ImpossibleAmount(self.amount))

    # основная функция проверки
    def do_check(self) -> dict:
        self.errors.add(self.check_arguments())
        if self.errors == {None}:
            self.errors.add(self.check_amount())

        return {'from': self.convert_from,
                'to': self.convert_to,
                'amount': self.amount,
                'errors': self.errors}


if __name__ == '__main__':
    user = CheckRequest('доллар сша/eur/5')
    result = user.do_check()
    print(result)

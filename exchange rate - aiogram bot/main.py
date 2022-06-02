import logging
from aiogram import *
from settings import TG_TOKEN
from data import ExchangeRate, CurrencyData
from random import sample
from exceptions import *


# объект бота
bot = Bot(token=TG_TOKEN)
# диспетчер бота
dp = Dispatcher(bot)
# логгирование сообщений
logging.basicConfig(level=logging.INFO)


class BotExchanger:

    @classmethod
    def launch(cls):

        @dp.message_handler(commands='start')
        async def cmd_special_buttons(message: types.Message):

            keyboard = types.ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True)
            keyboard.add(types.KeyboardButton(text='Помощь'))

            await message.answer(f'Вас приветствует бот для конвертации валют! '
                                 f'Это учебный проект с курса SkillFactory. '
                                 f'Мой создатель: @pu6yc')
            await message.answer(f'Чтобы получить инструкцию, введите /help '
                                 f'или нажмите на кнопку "Помощь"',
                                 reply_markup=keyboard)

        @dp.message_handler(commands='help')
        @dp.message_handler(text='Помощь')
        async def show_help(message: types.Message):

            keyboard_example = types.InlineKeyboardMarkup()
            keyboard_example.row(
                types.InlineKeyboardButton(
                    'Нажмите, чтобы попробовать!',
                    callback_data='example'))
            keyboard_example.row(
                types.InlineKeyboardButton(
                    'Показать часто используемые валюты',
                    callback_data='common'))

            await message.answer(
                f'Чтобы конвертировать одну валюту в другую, '
                f'введите через / по порядку: название исходной валюты, '
                f'название валюты, в которую вы хотите конвертировать, и количество.\n'
                f'Вы можете использовать, как трёхбуквенные обозначения валют:\n'
                f'<b>USD/EUR/10</b>\n'
                f'так и их русские названия:\n'
                f'<b>Доллар США/Евро/10</b>',
                reply_markup=keyboard_example, parse_mode='HTML')

        # показать пример запроса и результат
        @dp.callback_query_handler(text='example')
        async def show_example(call: types.CallbackQuery):
            from_, to_ = sample(log.most_common, 2)
            cur_iso = CurrencyData().get_available('iso')
            res = ExchangeRate(from_, to_, Decimal('4.2'))
            from_rus = cur_iso.get(from_).title()
            to_rus = cur_iso.get(to_).title()

            await call.message.answer(f"<b>Запрос:</b>\n{from_}/{to_}/4.2", parse_mode='HTML')
            await call.message.answer(f"{Decimal('4.2')} {from_rus} ({from_.upper()}) = "
                                      f"{res.converter()} {to_rus} ({to_.upper()})")

        # показать часто используемые валюты
        @dp.callback_query_handler(text='common')
        async def get_common(call: types.CallbackQuery):
            cur_iso = CurrencyData().get_available('iso')
            common_list = []

            for currency in log.most_common:
                common_list.append(f'🔸 {cur_iso.get(currency).title()} ({currency.upper()})')

            await call.message.answer('\n'.join(common_list))

        # принимает запрос пользователя и показывает результат
        @dp.message_handler(content_types='text')
        async def user_request(message: types.Message):
            r = CheckRequest(message.text).do_check()

            if r['errors'] == {None}:
                cur_iso = CurrencyData().get_available('iso')
                res = ExchangeRate(r['from'], r['to'], r['amount'])
                from_rus = cur_iso.get(r['from']).title()
                to_rus = cur_iso.get(r['to']).title()

                await message.answer(f"{r['amount']} {from_rus} ({r['from'].upper()}) = "
                                     f"{res.converter()} {to_rus} ({r['to'].upper()})")
                # обновить часто используемые валюты
                log.most_common = r['from'], r['to']
            else:
                await message.answer('\n'.join(r['errors']))

        log = ConverterLog()
        executor.start_polling(dp, skip_updates=True)


class ConverterLog:

    def __init__(self):
        self.common = {}

    @property
    def most_common(self):
        if not self.common:
            base_currency = ('usd', 'eur', 'rub', 'jpy', 'gbp', 'chf')
            for currency in base_currency:
                self.common[currency] = 10
        return sorted(self.common, reverse=True, key=self.common.get)[:10]

    @most_common.setter
    def most_common(self, currency_used: tuple):
        for c in currency_used:
            self.common[c] = self.common.get(c, 0) + 1


if __name__ == '__main__':
    BotExchanger.launch()

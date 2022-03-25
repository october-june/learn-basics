'''
Морской бой 10х10
Домашнее задание
SkillFactory, курс PDEV-9, блок C2
Дедлайн нарушал: Аркадий :)
'''

from time import sleep
from random import choice, randrange


class Colors:
    reset = '\033[0;0m'
    red = '\033[0;31m'
    blue = '\033[0;34m'
    yellow = '\033[1;93m'
    bold = '\033[1m'


class Cell:
    '''
    Класс определяет внешний вид всех клеток в зависимости от содержимого.
    Используются разные моноширинные символы и цвета.
    '''
    def set_color(symbol, color):
        return color + symbol + Colors.reset

    def set_bold(symbol):
        return Colors.bold + symbol + Colors.reset

    empty = ' '.center(3)
    miss = '•'.center(3)
    ship_fine = set_color('■'.center(3), Colors.blue)
    ship_damaged = set_color('□'.center(3), Colors.yellow)
    ship_sunk = set_color('X'.center(3), Colors.red)


class Ship():
    '''
    Класс для создания кораблей.
    В свойствах указаны все характеристики и положение.
    '''
    def __init__(self, x, y, direction, length):

        self.x = x
        self.y = y
        self.direction = direction
        self.length = length
        self.hp = length
        self.name = Game.ship_names[length]

    def set_position(self, x, y, direction):
        '''
        Используется для расстановки кораблей.
        '''
        self.x = x
        self.y = y
        self.direction = direction

        if direction == 'vertical':
            self.height = self.length
            self.width = 1
        elif direction == 'horizontal':
            self.height = 1
            self.width = self.length

    def rotate(self, x, y):
        '''
        Используется в анализе поля
        для определения наиболее вероятного места расположения вражеских судов.
        '''
        self.x = x
        self.y = y
        rotations = ((self.length, 1), (1, self.length), (1 - self.length, 1), (1, 1 - self.length))

        for rotation in rotations:
            yield rotation

    def __str__(self):
        '''
        В клетках поля будут хранится сами корабли, как объекты.
        Изменяю строковое представление, чтобы на поле отображались только значки кораблей.
        '''
        return Cell.ship_fine

    def __repr__(self):
        '''
        Использовал в качестве отладочной информации
        для проверки инициализации кораблей.
        '''
        return f'Корабль: {self.name}, размер: {self.length}, здоровье: {self.hp}\n' \
               f'Координаты: x = {self.x}, y = {self.y}\n' \
               f'Расположение: {self.direction} (высота = {self.height}, ширина = {self.width})'


class Field():
    '''
    Игровое поле состоит из частей: своя акватория, радар для атаки
    и неотображаемое в ходе игры поле с рассчётом мест,
    где вероятнее всего может оказаться вражеское судно.
    Используется ИИ для атаки; также использовалось для отладки.
    '''
    def __init__(self, size):

        self.size = size
        self.map = [[Cell.empty for _ in range(size)] for _ in range(size)]
        self.radar = [[Cell.empty for _ in range(size)] for _ in range(size)]
        self.analysis = [[0 for _ in range(size)] for _ in range(size)]

    def get_zone(self, zone):

        if zone == 'map':
            return self.map

        elif zone == 'radar':
            return self.radar

        elif zone == 'analysis':
            return self.analysis

    def print_field_zone(self, zone):
        '''
        Каждая зона игрового поля отрисовывает отдельно.
        В -1 печатается координатная сетка.
        Внутри самого игрового поля просто выводится соодержимое клеток.
        '''
        field = self.get_zone(zone)

        for row in range(-1, self.size):
            for col in range(-1, self.size):

                if row == -1 and col == -1:
                    print(' '.center(3), end='')
                elif row == -1:
                    print(Cell.set_bold(f'{col + 1}'.center(3)), end='')
                elif col == -1:
                    print(Cell.set_bold(f'{Game.letters[row]}'.center(3)), end='')
                else:
                    if zone == 'analysis':
                        if not field[row][col]:
                            print(Cell.empty, end='')
                        else:
                            print(f'{field[row][col]}'.center(3), end='')
                    else:
                        print(field[row][col], end='')

            print()
        print()

    def is_avaliable_place(self, ship, zone):
        '''
        Проверка, определяет, можно ли разместить судно в указанных координатах.
        '''
        field = self.get_zone(zone)

        x = ship.x
        y = ship.y
        height = ship.height
        width = ship.width

        # вмещается ли в поле
        if x + height > self.size or y + width > self.size or x + height < 0 or y + width < 0:
            return False

        for x_coord in range(x - 1, x + height + 1):
            for y_coord in range(y - 1, y + width + 1):
                # исключает проверку за границей поля
                if x_coord < 0 or y_coord < 0 or x_coord >= self.size or y_coord >= self.size:
                    continue
                # если в клетке промах
                if x_coord in range(x, x + height) and y_coord in range(y, y + width) and field[x_coord][y_coord] == Cell.miss:
                    return False
                # если в клетке судно
                if isinstance(field[x_coord][y_coord], Ship):
                    return False

        # если все проверки пройдены, судно вмещается
        return True

    def field_analysis(self, ships_afloat):
        '''
        Анализ игрового поля.
        Каждой клетке присваивается значение.
        Чем выше вероятность найти там вражеское судно, тем больше значение.
        '''
        # каждый раз рассчитывается заново
        self.analysis = [[1 for _ in range(self.size)] for _ in range(self.size)]

        # ищет раненые суда
        for x in range(self.size):
            for y in range(self.size):

                if self.radar[x][y] == Cell.ship_damaged:
                    '''
                    Если судно подбито, в первую очередь его нужно добить.
                    Приоритет выстрелам сверху-снизу, справа-слева.
                    По клеткам, лежащим по диагонали от подбитых, огонь не ведётся никогда. 
                    '''

                    if x - 1 >= 0:
                        if y - 1 >= 0:
                            self.analysis[x - 1][y - 1] = 0
                        self.analysis[x - 1][y] *= 40  # именно такой порядок!
                        if y + 1 < self.size:
                            self.analysis[x - 1][y + 1] = 0

                    if y - 1 >= 0:
                        self.analysis[x][y - 1] *= 40
                    if y + 1 < self.size:
                        self.analysis[x][y + 1] *= 40

                    if x + 1 < self.size:
                        if y - 1 >= 0:
                            self.analysis[x + 1][y - 1] = 0
                        self.analysis[x + 1][y] *= 40
                        if y + 1 < self.size:
                            self.analysis[x + 1][y + 1] = 0

        for ship_type in ships_afloat:
            '''
            Какие суда остались у соперника — известно.
            Чем больше кораблей из оставшихся влазят в проверяемое поле,
            тем вероятнее что-то там подбить.
            '''
            ship = Ship(x=0, y=0, direction=None, length=ship_type)

            for x in range(self.size):
                for y in range(self.size):

                    for rotation in ship.rotate(x, y):
                        ship.height, ship.width = rotation
                        if self.is_avaliable_place(ship, 'radar'):
                            self.analysis[x][y] += 1

                    # исключить стрельбу по битым полям
                    if self.radar[x][y] == Cell.ship_sunk or self.radar[x][y] == Cell.ship_damaged or self.radar[x][y] == Cell.miss:
                        self.analysis[x][y] = 0

    def get_analysis_result(self):
        '''
        Получает результаты анализа.
        Возвращает список с кортежами координат с наибольшим приоритетом.
        '''
        best_shot_variants = {}
        best_shot = 0

        for x in range(self.size):
            for y in range(self.size):
                if self.analysis[x][y] >= best_shot:
                    # не лучшие выстрелы больше не записываются
                    best_shot = self.analysis[x][y]
                    best_shot_variants.setdefault(best_shot, []).append((x, y))

        return best_shot_variants[best_shot]

    # устанавливает корабль на поле
    def set_ship(self, ship, zone):

        field = self.get_zone(zone)

        x = ship.x
        y = ship.y
        height = ship.height
        width = ship.width

        for x_coord in range(x, x + height):
            for y_coord in range(y, y + width):
                field[x_coord][y_coord] = ship

    # отмечает потопленный корабль и расставляет промохи по контуру
    def mark_sunk(self, ship, zone):

        field = self.get_zone(zone)

        x = ship.x
        y = ship.y
        height = ship.height
        width = ship.width

        for x_coord in range(x - 1, x + height + 1):
            for y_coord in range(y - 1, y + width + 1):

                if x_coord in range(x, x + height) and y_coord in range(y, y + width):
                    field[x_coord][y_coord] = Cell.ship_sunk
                elif x_coord in range(self.size) and y_coord in range(self.size):
                    field[x_coord][y_coord] = Cell.miss


class Player():
    '''
    Один класс для игрока и ИИ.
    У каждого игрока свои поля, суда, лог сообщений.
    Поля и сообщения ИИ не отображаются.
    Атрибут auto_deploy отвечает за автоматическую расстановку кораблей.
    По умолчанию, True для ИИ и False для игрока.
    '''
    def __init__(self, name, is_ai, auto_deploy):

        self.name = name
        self.is_ai = is_ai
        self.auto_deploy = auto_deploy
        self.log = []
        self.ships = []
        self.enemy_ships = Game.ship_collection.copy()
        self.field = Field(Game.field_size)
        self.enemy_field = Field(Game.field_size)

    def get_input(self, type):
        '''
        Ввод данных.
        Установка кораблей и выстрелы.
        Не зависит от регистра и наличия пробелов.
        '''
        if type == 'set':

            if self.auto_deploy:

                x, y, direct = choice(Game.letters), randrange(1, 11), choice(('Г', 'В'))

            else:

                while True:
                    try:
                        coordinates = input().replace(' ', '').upper()
                        x, y, direct = coordinates[0], int(coordinates[1:-1]), coordinates[-1]
                        assert x in Game.letters and y in range(1, 11) and direct in ('Г', 'В')
                    except IndexError:
                        print('Адмирал, нам неясен приказ!')
                    except ValueError:
                        print('Координаты вне акватории, адмирал!')
                    except AssertionError:
                        print('Координаты вне акватории, адмирал!')
                    else:
                        break

            x = Game.letter_coordinates[x]
            y -= 1
            direct = ('horizontal', 'vertical')[direct == 'В']

            return x, y, direct

        elif type == 'shot':

            # ИИ использует анализ поля для осмысленной стрельбы
            if self.is_ai:

                x, y = choice(self.field.get_analysis_result())

            else:

                while True:
                    try:
                        coordinates = input().replace(' ', '').upper()
                        x, y = coordinates[0], int(coordinates[1:])
                        assert x in Game.letters and y in range(1, 11)
                    except IndexError:
                        print('Адмирал, нам неясен приказ!')
                    except ValueError:
                        print('Координаты вне акватории, адмирал!')
                    except AssertionError:
                        print('Координаты вне акватории, адмирал!')
                    else:
                        break

                x = Game.letter_coordinates[x]
                y -= 1

            return x, y

    def make_shot(self):

        while True:
            try:
                x, y = self.get_input('shot')
                assert self.field.radar[x][y] == Cell.empty
            except AssertionError:
                if not self.is_ai:
                    print(f'Адмирал {self.name}, эта область уже обстреляна!')
            else:
                # оппонент сообщает результаты выстрела
                shot_result = game.next_player.take_shot(x, y)
                break

        # стреляющий отмечает результат выстрела на своём радаре
        if shot_result == 'miss':
            self.field.radar[x][y] = Cell.miss

        elif shot_result =='hit':
            self.field.radar[x][y] = Cell.ship_damaged

        else:
            ship = shot_result
            self.field.mark_sunk(ship, 'radar')
            self.enemy_ships.remove(ship.length)

        # после каждого выстрела поле анализируется заново
        self.field.field_analysis(self.enemy_ships)

        return shot_result

    # принимающий выстрел делает пометку на своём поле и возвращает стреляющему результат
    def take_shot(self, x, y):

        if isinstance(self.field.map[x][y], Ship):
            ship = self.field.map[x][y]
            ship.hp -= 1

            if ship.hp <= 0:
                self.field.mark_sunk(ship, 'map')
                self.ships.remove(ship)
                # возвращает потопленное судно
                return ship

            self.field.map[x][y] = Cell.ship_damaged
            return 'hit'

        else:
            self.field.map[x][y] = Cell.miss
            return 'miss'


class Game():

    # константы
    letters = 'АБВГДЕЖЗИК'
    field_size = len(letters)
    letter_coordinates = dict(zip(letters, range(field_size)))
    ship_collection = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
    ship_names = {4: 'линкор', 3: 'крейсер', 2: 'эсминец', 1: 'торпедный катер'}

    def __init__(self):

        self.current_player = None
        self.next_player = None

    def preparing(self):
        '''
        Назначается очерёдность хода.
        Игроки размещают свои корабли.
        '''
        self.current_player = gamer
        self.next_player = ai

        for player in [gamer, ai]:
            self.deploy_ships(player)
            player.field.field_analysis(player.enemy_ships)

    def switch_turn(self):
        self.current_player, self.next_player = self.next_player, self.current_player

    def deploy_ships(self, player):

        # корабли устанавливаются, начиная с самого большого
        for ship_type in Game.ship_collection:

            ship = Ship(x=0, y=0, direction=None, length=ship_type)

            for _ in range(50):
                '''
                Число попыток ограничено.
                Не допускает бесконечного цикла, если возникла ситуация,
                когда последние корабли не влазят.
                В таком случае поле очищается, функция перезапускается.
                '''
                if not player.auto_deploy:
                    self.clear_screen()
                    player.field.print_field_zone('map')
                    player.log.append(f'Куда разместить {self.ship_names[ship_type]} ({ship_type}), адмирал?')
                    self.show_log()
                else:
                    print(f'{player.name} размещает флот...')

                try:
                    x, y, direct = player.get_input('set')
                    ship.set_position(x, y, direct)
                    # print(repr(ship))  #  использовалось при отладке
                    assert player.field.is_avaliable_place(ship, 'map')
                except AssertionError:
                    player.log.append('В указанных координатах недосточно места!')
                else:
                    player.field.set_ship(ship, 'map')
                    player.ships.append(ship)
                    break

            else:
                player.field.map = [[Cell.empty for _ in range(Game.field_size)] for _ in range(Game.field_size)]
                self.deploy_ships(player)
                break

        player.log.clear()
        player.log.append(f'Адмирал {player.name}, прикажете открыть огонь? Ждём координаты для первого удара!')

    # выводит на экран игровое поле и лог сообщений
    def show_field(self):

        if not self.current_player.is_ai:
            self.current_player.field.print_field_zone('map')
            self.current_player.field.print_field_zone('radar')
            # self.current_player.field.print_field_zone('analysis')  # отладочное поле

        self.show_log()

    # лог нужен, чтобы сообщения всегда отображались ниже игрового поля
    def show_log(self):

        if not self.current_player.is_ai:
            for message in self.current_player.log:
                print(message)
                sleep(0.7)

        self.current_player.log.clear()

    def check_gamestate(self):

        if not self.current_player.enemy_ships:
            return True

    def clear_screen(self):
        print('\n' * 50)


if __name__ == '__main__':

    # подготовка
    game = Game()
    gamer = Player(name=input('Как ваше имя, адмирал?\n'), is_ai=False, auto_deploy=False)
    ai = Player(name='AI', is_ai=True, auto_deploy=True)
    gamer.log.append(f"Чтобы установить корабль, укажите координатами, куда установить нос корабля (буква и число), и задайте направление: Г (горизонтально) или В (вертикально).\nПример: {choice(Game.letters)} {randrange(1, 11)} {choice(('Г', 'В'))}\n")
    game.preparing()

    # обмен выстрелами
    while True:

        game.clear_screen()

        if game.check_gamestate():
            break

        game.show_field()
        move = game.current_player.make_shot()

        if move == 'miss':
            game.next_player.log.append(f'{game.current_player.name} промахнулся!')
            game.next_player.log.append('Куда нанести удар?')
            game.current_player.log.append(f'Мимо! {game.next_player.name} делает ответный выстрел.')
            # смена хода только при промахе
            game.switch_turn()
            continue

        if move == 'hit':
            game.next_player.log.append('Наш корабль подбит!')
            game.current_player.log.append('Цель поражена! Куда произвести следующий выстрел?')
            continue

        if isinstance(move, Ship):
            ship = move
            game.next_player.log.append(f'Адмирал, противник потопил наш {ship.name}.')
            game.current_player.log.append(f'Нам удалось уничтожить вражеский {ship.name}! Ждём дальнейших распоряжений.')
            pass

    # вывод финального состояния
    game.current_player.field.print_field_zone('map')
    game.next_player.field.print_field_zone('map')

    # поздравления и прощание
    print(f'Адмирал {game.current_player.name} отправил на дно последний корабль и выиграл этот матч!')
    print('Спасибо за игру!')
    input()

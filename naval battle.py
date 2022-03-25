'''
Морской бой
SkillFactory
'''

from time import sleep
from random import choice, randrange
import re


#  для оформления
class ColoredText:
    reset = '\033[0;0m'
    red = '\033[0;31m'
    blue = '\033[0;34m'
    yellow = '\033[1;93m'


#  стиль игровых символов
class Cell:
    def set_color(symbol, color):
        return color + symbol + ColoredText.reset

    empty = ' '.ljust(3)
    miss = '⦁'.ljust(3)
    ship_fine = set_color('■'.ljust(3), ColoredText.blue)
    ship_damaged = set_color('▧'.ljust(3), ColoredText.yellow)
    ship_sunk = set_color('✖'.ljust(3), ColoredText.red)


class Ship():
    def __init__(self, x, y, direction, length):
        self.x = x
        self.y = y
        self.direction = direction
        self.length = length
        self.hp = length

    #  определяет направление судна
    def set_place(self, x, y, direction):
        self.x = x
        self.y = y
        if direction == 'горизонтально':
            self.width = self.length
            self.height = 1
        if direction == 'вертикально':
            self.width = 1
            self.height = self.length


    def __str__(self):
        return Cell.ship_fine


class Field(object):
    '''
    игровое поле
    зона map для своих кораблей
    зона radar для поиска вражеских
    '''

    #  инициализация игровых зон
    def __init__(self, size):
        self.size = size
        self.map = [[Cell.empty for _ in range(size)] for __ in range(size)]
        self.radar = [[Cell.empty for _ in range(size)] for __ in range(size)]

    #  геттер, возвращает игровую зону
    def get_zone(self, zone):
        if zone == 'map':
            return self.map
        if zone == 'radar':
            return self.radar

    #  печатает указанную игровую зону
    def print_field(self, zone):
        field = self.get_zone(zone)

        for x in range(-1, self.size):
            for y in range(-1, self.size):
                if x == y == -1:
                    print(' '.ljust(3), end='')
                elif x == -1:
                    print(f'{y + 1}'.ljust(3), end='')
                elif y == -1:
                    print(f'{Field.letters[x]}'.ljust(3), end='')
                else:
                    print(f'{field[x][y]}', end='')
            print('')
        print('')

    #  проверяет, помещается ли корабль
    def place_avaliable(self, ship, zone):
        field = self.get_zone(zone)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        #  сразу отсевает корабли, выходящие за границу
        if x + width >= self.size or y + height >= self.size:
            return False

        #  отсеивает, если корабль попадает на место, где есть промах
        for x_letter in range(x, x + width):
            for y_digit in range(y, y + height):
                if field[x_letter][y_digit] == Cell.miss:
                    return False

        #  отсеивает, если в радиусе одной клетки есть другой корабль
        for x_letter in range(x - 1, x + width + 1):
            for y_digit in range(y - 1, y + height + 1):
                #  корабли могут стоять на самом краю, проверка исключает IndexError: out of range
                if x_letter == -1 or y_digit == -1 or x_letter == field.size or y_digit == field.size:
                    continue
                elif field[x_letter][y_digit] in (Cell.ship_fine, Cell.ship_damaged, Cell.ship_sunk):
                    return False

        #  проверки пройдены, корабль влазит
        return True

    #  устанавливает корабль на поле
    def set_ship(self, ship, zone):
        field = self.get_zone(zone)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        #  ставит в клетку не значок, а сам корабль как объект
        for x_letter in range(x, x + width):
            for y_digit in range(y, y + height):
                field[x_letter][y_digit] = ship


    #  помечает потопленный корабль
    def mark_sunk(self, ship, zone):
        field = self.get_zone(zone)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        #  ставит промахи везде в радиусе одной клетки (корабль затирается)
        for x_letter in range(x - 1, x + width + 1):
            for y_digit in range(y - 1, y + height + 1):
                field[x_letter][y_digit] = Cell.miss

        #  отмечает потопленный корабль там, где он находился
        for x_letter in range(x, x + width):
            for y_digit in range(y, y + height):
                field[x_letter][y_digit] = Cell.ship_sunk

    #  функция для ИИ, определяет лучший ход
    def get_best_moves():
        pass


class Player(object):
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.field = None
        self.ships = []
        self.enemy_ships = []

    #  возвращает координаты, введённые пользователем
    def get_coordinate_input(self):
        input_pattern = f'[{Game.letters}]' + '\d{,2}[ГВ]?'

        while True:
            try:
                coordinate_input = input().upper().replace(' ', '')
                assert re.fullmatch(rf'{input_pattern}', coordinate_input)
            except AssertionError:
                print('Координаты вне акватории, адмирал!')
            else:
                break

        #  если последний символ — буква, значит, координаты для установки корабля
        #  в противном случае — выстрел
        if coordinate_input[-1].isalpha():
            x, y, d = coordinate_input[0], coordinate_input[1:-1], coordinate_input[-1]
            return Game.letter_coordinates[x], int(y) - 1, ('горизонтально', 'вертикально')[d == 'В']
        else:
            x, y = coordinate_input[0], coordinate_input[1:]
            return Game.letter_coordinates[x], int(y) - 1

    #  делает выстрел, координаты будут запрошены у пользователя
    def make_shot(self, target):
        while True:
            try:
                if self.is_ai:
                    shot_x, shot_y = randrange(self.field.size), randrange(self.field.size)
                else:
                    shot_x, shot_y = self.get_coordinate_input()
                    assert self.field.radar[shot_x][shot_y] == Cell.empty
            except AssertionError:
                print(f'Адмирал {self.name}, эта область уже обстреляна!')
            #  делаем выстрел — нам отвечают, что случилось
            else:
                shot_result = target.shot_effect(shot_x, shot_y)
                break
        
        if shot_result == 'miss':
            self.field.radar[shot_x][shot_y] = Cell.miss
        elif shot_result == 'hit':
            self.field.radar[shot_x][shot_y] = Cell.ship_damaged
        #  когда говорят "убит!", возвращается целый корабль
        #  отмечаем его на поле, убираем из списка живых
        else:
            ship = shot_result
            self.field.mark_sunk(ship, 'radar')
            self.enemy_ships.remove(ship.size)
            shot_result = 'sink'
        
        return shot_result

    def shot_effect(self, shot_x, shot_y):
        if isinstance(self.field.map[shot_x][shot_y], Ship):
            ship = self.field.map[shot_x][shot_y]
            ship.hp -= 1

            if not ship.hp:
                self.field.mark_sunk(ship, 'map')
                self.ships.remove(ship)
                return ship

            else:
                self.field.map[shot_x][shot_y] = Cell.ship_damaged
                return 'hit'

        else:
            self.field.map[shot_x][shot_y] = Cell.miss
            return 'miss'


class Game(object):
    letters = 'АБВГДЕЖЗИК'
    field_size = len(letters)
    letter_coordinates = dict(zip(letters, range(field_size)))
    ship_collection = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
    ship_names = {4: 'линкор', 3: 'крейсер', 2: 'эсминец', 1: 'торпедный катер'}

    def __init__(self):
        self.current_player = None
        self.next_player = None

    def add_player(self, player):
        player.field = Field(Game.field_size)
        player.enemy_ships = Game.ship_collection.copy()
        self.deploy_ships(player)
        
    def deploy_ships(self, player):
        for ship_type in self.ship_collection:
            ship = Ship(x=0, y=0, direction=None, length=ship_type)
            
            for _ in range(50):
                self.clear_screen()
                player.field.print_field('map')
                print(f'Куда разместить {self.ship_names[ship_type]}, адмирал?')
                
                try:
                    x, y, direction = player.get_coordinate_input()
                    ship.set_place(x, y, direction)
                    assert player.field.place_avaliable(ship, 'map')
                except AssertionError:
                    print('В указанных координатах недосточно места!')
                else:
                    player.field.set_ship(ship, 'map')
                    break
            else:
                player.field.map = [[Cell.empty for _ in range(self.field_size)] for __ in range(self.field_size)]
                self.deploy_ships(player)

    def draw_field(self):
        if not self.current_player.is_ai:
            self.current_player.field.print_field('map')
            self.current_player.field.print_field('radar')
    
    def set_first_player(self):
        first_turn = input(f'Адмирал {player.name}! Желаете нанести первый выстрел? да/нет\n').casefold()
        if first_turn in ('да', 'yes'):
            self.current_player, self.next_player = player, ai
        else:
            self.current_player, self.next_player = ai, player
            
    def switch_turn(self):
        self.current_player, self.next_player = self.next_player, self.current_player

    def check_game_state(self):
        if not self.current_player.enemy_ships:
            f'{self.current_player.name} победил!'
        elif not self.next_player.enemy_ships:
            f'{self.next_player.name} победил!'
        else:
            return False

    def clear_screen():
        print('\n' * 50)


if __name__ == '__main__':
    print(' Добро пожаловать в Морской бой! '.center(50, '—'))
    sleep(0.5)
    gamer = Player(name=input('Как ваше имя, адмирал?\n'))
    ai = Player(name='AI', is_ai=True)
    game = Game()

    while True:
        exit()

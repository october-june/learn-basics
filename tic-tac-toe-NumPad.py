from time import sleep
from random import randint

PLAYERS = {
    'o': [],
    'x': []
}

WIN_CONDITIONS = (
    {7, 8, 9}, {4, 5, 6}, {1, 2, 3},  # rows
    {7, 4, 1}, {8, 5, 2}, {9, 6, 3},  # columns
    {7, 5, 3}, {1, 5, 9}              # diagonals
)

# NumPad coordinates
MOVES = {
    7: (1, 0), 8: (1, 1), 9: (1, 2),
    4: (2, 0), 5: (2, 1), 6: (2, 2),
    1: (3, 0), 2: (3, 1), 3: (3, 2)
}

class TEXT:
    bold = '\033[1m'
    yellow = '\033[43m'
    inverse = '\033[37m\033[40m'
    end = '\033[0;0m'

    def make_frame(self):
        return TEXT.bold + TEXT.inverse + self.center(19) + TEXT.end

    def winner(self):
        return TEXT.yellow + self.center(5) + TEXT.end


# Cleans the console
def clean():
    print('\n' * 50)


# Human vs AI: X or O
def choose_char():
    while True:
        try:
            human = input('Сыграть за "x" или "o"?\n').casefold()
            assert human in ('x', 'х', 'o', 'о')
        except AssertionError:
            print('Ошибка ввода.')
        else:
            if human in ('x', 'х'):
                return 'x', 'o'
            else:
                return 'o', 'x'


def get_answer(question):
    answer = input(f'{question}:\n').casefold()
    return answer in ('да', 'lf', 'yes')


# Create board with title
def create_field():
    field = [[' '] * 3 for i in range(4)]
    field[0] = TEXT.make_frame('Tic-Tac-Toe')
    return field



# Print field with rows and columns
def print_field():
    # Title
    divider = '┌─────┬─────┬─────┐'
    print(f'{field[0]}\n{divider}')

    # Body
    for row in field[1:]:
        print('', end='│')
        for c in row:
            print(f'{c.center(5)}', end='│')

        if row is field[-1]:
            divider = '└─────┴─────┴─────┘'
        else:
            divider = '├─────┼─────┼─────┤'

        print('\n' + divider)


# Check the input is correct
def get_coord():
    while True:
        try:
            move = int(input('Введите координаты:\n'))
            assert 1 <= move <= 9
        except (AssertionError, ValueError):
            print('Неверные координаты!')
        else:
            return move


# Check the cell is free
def valid_move(move):
    x, y = MOVES[move]
    return True if (field[x][y] == ' ') else False


def check_win_cond(char):
    # Check player reached any wining combination
    for condition in WIN_CONDITIONS:
        if condition.issubset(PLAYERS[char]):
            
            # Highlights winner's row
            for coord in condition:
                x, y = MOVES[coord]
                field[x][y] = TEXT.winner(char.center(3))
            return True

    return False


# Primitive AI makes move
def ai_turn(char1, char2):
    # Move to win or save
    for condition in WIN_CONDITIONS:
        if sum(cell in PLAYERS[char1] for cell in condition) == 2 \
        or sum(cell in PLAYERS[char2] for cell in condition) == 2:
            for cell in condition:
                if valid_move(cell):
                    return cell
    # Random move
    else:
        cell = 5
        while not valid_move(cell):
            cell = randint(1, 9)
        return cell


# MAIN FUNCTION
def play():
    winner = False
    turn = 0

    while not winner:
        # Show gamestate
        clean()
        turn += 1
        char = ('o', 'x')[turn % 2]
        print_field()
        print(f'Ход №{turn}.\nИгрок ставит "{char}".\n')

        # Make move
        while True:
            try:
                if ai == char:
                    coord = ai_turn(ai, human)
                else:
                    coord = get_coord()
                    assert valid_move(coord)
            except AssertionError:
                print('Поле уже занято!')
            else:
                x, y = MOVES[coord]
                field[x][y] = char
                PLAYERS[char].append(coord)
                if ai == char:
                    sleep(1)
                break

        # End with win or tie
        if turn >= 5:
            winner = check_win_cond(char)
        if turn == 9:
            break

    # Congrats
    clean()
    print_field()
    print(('Ничья!\n', f'Победил "{char}"!\n')[winner])
    sleep(1)


# Greetings
print(' Добро пожаловать в крестики-нолики! '.center(50, '—'))
sleep(0.5)
print('''
    Инструкция:
Вы делаете ходы по очереди. Начинает "x".
Чтобы сделать ход, используйте числа на NumPad от 1 до 9.\n
    Хорошей игры!\n''')
sleep(0.5)

# Play vs AI or vs human
if get_answer('Введите "да", если хотите сыграть с компьютером'):
    human, ai = choose_char()
else:
    ai = False

# Reset moves, field and play again
answer = True
while answer:
    PLAYERS['o'].clear()
    PLAYERS['x'].clear()
    field = create_field()
    play()
    print('Сыграете ещё раз?')
    answer = get_answer('Введите "да", если хотите сыграть снова')

# Bye
print('Спасибо за игру!')

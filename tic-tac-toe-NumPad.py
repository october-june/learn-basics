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
    7: (0, 0), 8: (0, 1), 9: (0, 2),
    4: (1, 0), 5: (1, 1), 6: (1, 2),
    1: (2, 0), 2: (2, 1), 3: (2, 2)
}

class txt:
    bold = '\033[1m'
    yellow = '\033[43m'
    inverse = '\033[37m\033[40m'
    end = '\033[0;0m'

    def make_title(self):
        return txt.bold + txt.inverse + self.center(19) + txt.end

    def winner(self):
        return txt.yellow + self.center(5) + txt.end


# Cleans the console
def clean():
    print('\n' * 50)


# Human vs AI: X or O
def choose_char():
    while True:
        try:
            human = input('Сыграть за "x" или "o"?\n').casefold()
            assert human in ('x', 'х', 'o', 'о')  # cyrillic or latin
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


# Create dict for game score
# Depend on game type: vs human or vs AI
def create_score_table(P1, P2):
    scores = {'draw:': 0, 'round:': 1}
    scores[(f'{P1}:', 'win:')[bool(ai)]] = 0
    scores[(f'{P2}:', 'lose:')[bool(ai)]] = 0
    return scores


# Print field with rows and columns
def print_field():
    # Title with scores
    print(txt.make_title('round: ' + str(game_score['round:'])))
    score_line = ' '.join(key + str(value) for key, value in game_score.items() if key != 'round:')
    print(txt.make_title(score_line))

    # Body
    print('┌─────┬─────┬─────┐')

    for row in field:
        print('', end='│')
        for c in row:
            print(f'{c.center(5)}', end='│')
        if row is not field[-1]:
            print('\n├─────┼─────┼─────┤')

    print('\n└─────┴─────┴─────┘')


# Check the input is correct
def get_coord():
    while True:
        try:
            move = int(input('Введите координаты:\n'))
            assert 1 <= move <= 9
        except (AssertionError, ValueError, KeyError):
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
                field[x][y] = txt.winner(char.center(3))
            return True

    return False


# Primitive AI makes move
def ai_turn(ai_char, human_char):
    # Move to win (primarily) or save
    cell = None
    for condition in WIN_CONDITIONS:
        if sum(point in PLAYERS[ai_char] for point in condition) == 2:
            for c in condition:
                if valid_move(c):
                    cell = c
        elif sum(point in PLAYERS[human_char] for point in condition) == 2:
            for c in condition:
                if not cell and valid_move(c):
                    cell = c
    if cell:
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

        # End with win or draw
        if turn >= 5:
            winner = check_win_cond(char)
        if turn == 9:
            break

    # Scores update
    if winner:
        if ai:
            game_score[('win:', 'lose:')[ai == char]] += 1
        else:
            game_score[(f'{player1}:', f'{player2}:')[char == 'o']] += 1
    else:
        game_score['draw:'] += 1

    # Congrats
    clean()
    print_field()
    print(('Ничья!\n', f'Победил "{char}"!\n')[winner])
    game_score['round:'] += 1
    sleep(1)


# Greetings
print(' Добро пожаловать в крестики-нолики! '.center(50, '—'))
sleep(0.5)
print('''
    Инструкция:
Вы делаете ходы по очереди. Начинает "x".
Чтобы сделать ход, используйте числа на NumPad от 1 до 9.
И разверните консоль пошире ;)\n
    Хорошей игры!\n''')
sleep(0.5)

# Play vs AI or vs human
if get_answer('Введите "да", если хотите сыграть с компьютером'):
    human, ai = choose_char()
else:
    ai = False
    player1 = input('Введите имя первого игрока:\n')[:3]
    player2 = input('Введите имя второго игрока:\n')[:3]

# Keep statistics
game_score = create_score_table(player1, player2)

# Start, reset moves, field and play again
answer = True
while answer:
    PLAYERS['o'].clear()
    PLAYERS['x'].clear()
    field = [[' '] * 3 for _ in range(3)]
    play()
    print('Сыграете ещё раз?')
    answer = get_answer('Введите "да", если хотите сыграть снова')

# Bye
print('Спасибо за игру!')

import telebot
from telebot import types
from random import randint
from board_and_heroes import *
from board_and_heroes import Board
from config import TOKEN
from data_base import *
from bigfoot_cards import *
from medusa_cards import *

bot = telebot.TeleBot(TOKEN)
pygame.init()
sc = pygame.display.set_mode((1800, 1000))


def start_bot():
    update_database()
    bot.infinity_polling(none_stop=True)


@bot.message_handler(commands=['help'])
def helping(message):
    bot.send_message(message.chat.id, 'Добро пожаловать !\nС помощью меня можно играть в настольную игру Unmatched\n'
                     '\nСписок команд:\n/rules - правила игры\n/register - регистрация '
                     '(нужна для начала игры)\n/game_start - начало игры, выбор противника и персонажей\n'
                     '/turn - выполнить действие (в свой ход)\n/board - показать игровго поля\n/hp - показаь ваше здоровья'
                     '\n/concede - закночить игру, \n/change_nickname - изменить никнейм')


@bot.message_handler(commands=['board'])
def show_board(message):
    users_nicknames = {users_id[x]: x for x in users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id not in heroes:
        bot.send_message(message.chat.id, 'Вы не находитесь в игре, создайте игру командой /game_start')
        return
    hero = heroes[message.chat.id]
    main_hero = hero.main_hero
    board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
    bot.send_photo(hero.id, board_img)
    board_img.close()


@bot.message_handler(commands=['hp'])
def show_heroes_hp(message):
    users_nicknames = {users_id[x]: x for x in users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id not in heroes:
        bot.send_message(message.chat.id, 'Вы не находитесь в игре, создайте игру командой /game_start')
        return
    hero = heroes[message.chat.id]
    hero.show_hp()


@bot.message_handler(commands=['rules'])
def show_rules(message):
    markup = types.InlineKeyboardMarkup()
    btn_my_site = types.InlineKeyboardButton(text='Правила', url='https://pre.gaga.ru/wp-content/uploads/2020/08/'
                                                        'unmatched-bol-1_rulebook_ru_v1.pdf?ysclid=lb44bcb1x2524589211')
    markup.add(btn_my_site)
    bot.send_message(message.chat.id, "Нажми на кнопку чтобы прочитать правила.", reply_markup=markup)


@bot.message_handler(commands=['concede'])
def concede(message):
    users_nicknames = {users_id[x]: x for x in users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id not in heroes:
        bot.send_message(message.chat.id, 'Вы не находитесь в игре, создайте игру командой /game_start')
        return
    end_game(message)
    print(heroes)


def end_game(message):
    hero = heroes[message.chat.id]
    del heroes[hero.id]
    del heroes[hero.enemy.id]


@bot.message_handler(commands=['register'])
def registration(message):
    users_nicknames = {users_id[x]: x for x in users_id}
    print(users_nicknames)
    print(type(message))
    if message.chat.id in users_nicknames:
        nickname = users_nicknames[message.chat.id]
        bot.send_message(message.chat.id, 'Ваш никнейм ' + str(nickname))
        return
    bot.send_message(message.chat.id, 'Введите ваш никнейм')
    bot.register_next_step_handler(message, registr_in_database)


def registr_in_database(message):
    if message.text not in users_id:
        users_id[message.text] = message.chat.id
        users_message[message.chat.id] = message
        update_database()
        wins_count[message.chat.id] = 0
        bot.send_message(message.chat.id, 'Вы успешно зарегистрированы')
    else:
        bot.send_message(message.chat.id, 'Такой никнейм уже зарегистрирован, выберите другой')


@bot.message_handler(commands=['change_nickname'])
def change_nickname(message):
    users_nicknames = {users_id[x]: x for x in users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы')
        return
    old_nickname = users_nicknames[message.chat.id]
    del users_id[old_nickname]
    bot.send_message(message.chat.id, 'Ваш старый никнейм ' + str(old_nickname) + '\nВведите новый')
    bot.register_next_step_handler(message, change_in_data_base)


def change_in_data_base(message):
    new_nickname = message.text
    users_id[new_nickname] = message.chat.id
    bot.send_message(users_id[new_nickname], 'Ваш никнейм успешно изменен')


@bot.message_handler(commands=['game_start'])
def checking_current_games(message):
    users_nicknames = {users_id[x]: x for x in users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id in heroes:
        bot.send_message(message.chat.id, 'Вы не можете начать новую партию, так как не окончили предыдущую, '
                                          'воспользуйтесь командой /concede')
        return
    bot.send_message(message.chat.id, 'Введите никнейм вашего противника')
    bot.register_next_step_handler(message, search_opponent)


def search_opponent(message):
    opponent = message.text
    if opponent not in users_id:
        bot.send_message(message.chat.id, 'Ваш противник не зарегистрирован, либо вы неправильно ввели его никнейм')
        return
    if opponent in heroes:
        bot.send_message(message.chat.id, 'Ваш противник сейчас в игре, дождитесь окончания партии')
        return
    if users_id[opponent] == message.chat.id:
        bot.send_message(message.chat.id, 'Вы не можете играть сами с собой')
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    medusa_button = types.KeyboardButton('Медуза')
    bigfoot_button = types.KeyboardButton('Бигфут')
    markup.add(medusa_button, bigfoot_button)
    bot.send_message(message.chat.id, 'Выберите персонажа из списка', reply_markup=markup)
    bot.register_next_step_handler(message, lambda message: pick_heroes(message, users_id[opponent]))


def pick_heroes(message, opponent_id):
    if message.text == 'Медуза':
        first_hero = randint(0,1)
        create_hero('медуза', message.chat.id)
        create_hero('бигфут', opponent_id)
        medusa = heroes[message.chat.id]
        bigfoot = heroes[opponent_id]
        if first_hero:
            # medusa.your_turn = True
            medusa.current_cell = 30
            bigfoot.current_cell = 22
            medusa.places = {medusa: 30, bigfoot: 22}
            bot.send_message(message.chat.id, 'Вы ходите первым')
            medusa.main_hero = medusa
            bigfoot.main_hero = medusa
        else:
            # bigfoot.your_turn = True
            bigfoot.current_cell = 30
            medusa.current_cell = 22
            bigfoot.places = {medusa: 22, bigfoot: 30}
            bot.send_message(message.chat.id, 'Ваш противник ходит первым')
            medusa.main_hero = bigfoot
            bigfoot.main_hero = bigfoot
        bigfoot.id = opponent_id
        medusa.id = message.chat.id
        medusa.enemy_id = opponent_id
        medusa.enemy = bigfoot
        bigfoot.enemy_id = message.chat.id
        bigfoot.enemy = medusa
        medusa.main_hero.board = Board(sc, medusa.main_hero)
        shuffle_deck(medusa)
        shuffle_deck(bigfoot)
        bot.send_message(message.chat.id, f'Ваш персонаж {medusa.str}, персонаж вашего противника {bigfoot.str}'.format(medusa, bigfoot))

    elif message.text == 'Бигфут':
        first_hero = randint(0, 1)
        create_hero('бигфут', message.chat.id)
        create_hero('медуза', opponent_id)
        bigfoot = heroes[message.chat.id]
        medusa = heroes[opponent_id]
        if first_hero:
            # bigfoot.your_turn = True
            bigfoot.current_cell = 30
            medusa.current_cell = 22
            bigfoot.places = {medusa: 22, bigfoot: 30}
            bot.send_message(message.chat.id, 'Вы ходите первым')
            medusa.main_hero = bigfoot
            bigfoot.main_hero = bigfoot
        else:
            # medusa.your_turn = True
            medusa.current_cell = 30
            bigfoot.current_cell = 22
            medusa.places = {medusa: 30, bigfoot: 22}
            bot.send_message(message.chat.id, 'Ваш противник ходит первым')
            medusa.main_hero = medusa
            bigfoot.main_hero = medusa
        medusa.id = opponent_id
        bigfoot.id = message.chat.id
        medusa.enemy_id = message.chat.id
        medusa.enemy = bigfoot
        bigfoot.enemy_id = opponent_id
        bigfoot.enemy = medusa
        medusa.main_hero.board = Board(sc, medusa.main_hero)

        shuffle_deck(medusa)
        shuffle_deck(bigfoot)
        bot.send_message(message.chat.id, f'Ваш персонаж {bigfoot.str}, пресонаж вашего противника {medusa.str}'.format(bigfoot, medusa))
    else:
        bot.send_message(message.chat.id, 'Такого персонажа еще нет')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        medusa_button = types.KeyboardButton('Медуза')
        bigfoot_button = types.KeyboardButton('Бигфут')
        markup.add(medusa_button, bigfoot_button)
        bot.send_message(message.chat.id, 'Выберите персонажа', reply_markup=markup)
        bot.register_next_step_handler(message, lambda message: pick_heroes(message, opponent_id))
        return

    bot.send_message(medusa.main_hero.enemy.id, 'Карты в вашей руке:')
    bot.send_message(medusa.main_hero.id, 'Карты в вашей руке:')
    for i in range(5):
        medusa.draw_card()
        bigfoot.draw_card()
    bot.send_message(medusa.main_hero.enemy.id, 'Ваш противник выбирает куда поставить помощников')
    placing_supports(users_message[medusa.main_hero.id], medusa.main_hero)
    """placing_supports(message, medusa.main_hero.enemy)
    medusa.main_hero.board.render()
    board_img = open(f"pictures/boards_in_game/current_board{medusa.main_hero.id}.jpg".format(medusa.main_hero.id), 'rb')
    bot.send_photo(medusa.id, board_img)
    bot.send_photo(bigfoot.id, board_img)
    board_img.close()
    bot.send_message(medusa.id, 'Подготовка к игре завершена, можно начинать !')
    bot.send_message(bigfoot.id, 'Подготовка к игре завершена, можно начинать !')"""


def create_hero(hero, your_id):
    if hero == 'медуза':
        medusa_cards = [MomentaryGlance, ClutchingClaws, Dash, Fient, GazeOfStone, HissAndSlither, Regroup,
                        Snipe, SecondShot, TheHoundsOfMightyZeus]
        heroes[your_id] = Medusa(medusa_cards, bot)
    elif hero == 'бигфут':
        bigfoot_cards = [CrashThroughTheTrees, Disengage, FientBigfoot, Hoax, ItsJustYourImagination,
                         JackalopeHorns, LargerThenLife, MomentousShift, RegroupBigfoot, Savagery]
        heroes[your_id] = Bigfoot(bigfoot_cards, bot)


def shuffle_deck(current_hero):
    cards = current_hero.deck
    open_cards = []
    for i in range(len(cards)):
        open_cards.append(cards[i](current_hero, current_hero.enemy, bot))
    deck = []
    while len(open_cards) != 0:
        curr_card = randint(0, len(cards) - 1)
        deck.append(cards[curr_card](current_hero, current_hero.enemy, bot))
        if open_cards[curr_card].count_in_deck == 1:
            cards.pop(curr_card)
            open_cards.pop(curr_card)
        else:
            cards[curr_card].count_in_deck -= 1

    current_hero.deck = deck


def show_hand(hero):
    hand = hero.hand
    for card in hand:
        card.show_card()


def show_deck(hero):
    deck = hero.hand + hero.deck
    print(deck)
    x = deck[0]
    for card in deck:
        card.show_card()


def placing_supports(message, hero):
    main_hero = hero.main_hero
    main_hero.board.render()
    board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
    bot.send_photo(hero.id, board_img)
    board_img.close()
    cell = hero.current_cell
    zone = []
    for x in main_hero.board.cells_color[cell]:
        zone += main_hero.board.color_directions[x]
    if hero.str == 'medusa':
        bot.send_message(hero.id, 'Укажите ячейки, в которые хотите поставить своих гарпий, номера ячеек разделяйте '
                                  'пробелом')
        bot.register_next_step_handler(message, lambda message: placing_harpies(message, hero, zone))
    elif hero.str == 'bigfoot':
        bot.send_message(hero.id, 'Укажите ячейку, в которую хотите поставить помощника')
        bot.register_next_step_handler(message, lambda message: placing_jackalope(message, hero, zone))
    else:
        bot.send_message(hero.id, f'Неверное имя персонажа, произошла ошибка внутри программы функция \npick_heroes('
                                  f')\nplacing_supports{hero}'.format(hero))
    """board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
    bot.send_photo(hero.id, board_img)
    board_img.close()
    return 1"""


def placing_harpies(message, hero, zone):
    try:
        cells = [int(x) for x in message.text.split()]
    except:
        bot.send_message(hero.id, 'Отправьте НОМЕРА клеток')
        bot.register_next_step_handler(message, lambda message: placing_harpies(message, hero, zone))
        return
    cells = [int(x) for x in message.text.split()]
    if len(set(cells)) == len(cells) and all(x in zone for x in cells) and all(x != hero.current_cell for x in cells) and len(cells) == 3:
        main_hero = hero.main_hero
        main_hero.places[hero.harpy1] = cells[0]
        main_hero.places[hero.harpy2] = cells[1]
        main_hero.places[hero.harpy3] = cells[2]
        hero.harpy1.current_cell = cells[0]
        hero.harpy2.current_cell = cells[1]
        hero.harpy3.current_cell = cells[2]
        main_hero.board.render()
        board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
        bot.send_photo(hero.id, board_img)
        board_img.close()
        if hero.id == hero.main_hero.id:
            bot.send_message(hero.id, 'Теперь очередь вашего противника')
            placing_supports(users_message[hero.enemy.id], hero.enemy)
        else:
            board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
            bot.send_photo(hero.enemy.id, board_img)
            board_img.close()
            main_hero.your_turn = True
            bot.send_message(hero.id, 'Подготовка к игре завершена, можно начинать !')
            bot.send_message(hero.enemy.id, 'Подготовка к игре завершена, можно начинать !')
            bot.send_message(hero.main_hero.id, 'Ваш ход ! Воспользуйтесь командой /turn чтобы выбрать действие')
            bot.send_message(hero.main_hero.enemy.id, 'Сейчас ход вашего противника')

    elif all(x in zone for x in cells) and all(x != hero.current_cell for x in cells) and len(cells) == 3:
        bot.send_message(hero.id, 'Нельзя ставить несколько персонажей на одну ячейку, попробуйте заново')
        bot.register_next_step_handler(message, lambda message: placing_harpies(message, hero, zone))
    elif len(set(cells)) == len(cells) and  all(x != hero.current_cell for x in cells) and len(cells) == 3:
        bot.send_message(hero.id, 'Нужно поставить всех помощников в одну зону с главным героем, попробуйте заново')
        bot.register_next_step_handler(message, lambda message: placing_harpies(message, hero, zone))
    elif len(set(cells)) == len(cells) and all(x in zone for x in cells) and len(cells) == 3:
        bot.send_message(hero.id, 'Нельзя ставить помощников на одну ячейкку с героем')
        bot.register_next_step_handler(message, lambda message: placing_harpies(message, hero, zone))
    elif len(set(cells)) == len(cells) and all(x in zone for x in cells) and  all(x != hero.current_cell for x in cells):
        bot.send_message(hero.id, 'Укажите клетки для всех персонажей сразу')
        bot.register_next_step_handler(message, lambda message: placing_harpies(message, hero, zone))
    else:
        bot.send_message(hero.id, 'Вы совершили несколько ошибок в расстановке персонажей, прочтите правила /rules')
        bot.register_next_step_handler(message, lambda message: placing_harpies(message, hero, zone))


def placing_jackalope(message, hero, zone):
    try:
        cells = [int(x) for x in message.text.split()]
    except:
        bot.send_message(hero.id, 'Отправьте НОМЕРА клеток')
        bot.register_next_step_handler(message, lambda message: placing_jackalope(message, hero, zone))
        return
    cells = [int(x) for x in message.text.split()]
    if len(cells) == 1 and cells[0] in zone and cells[0] != hero.current_cell:
        main_hero = hero.main_hero
        main_hero.places[hero.jackalope] = cells[0]
        hero.jackalope.current_cell = cells[0]
        main_hero.board.render()
        board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
        bot.send_photo(hero.id, board_img)
        board_img.close()
        if hero == hero.main_hero:
            bot.send_message(hero.id, 'Теперь очередь вашего противника')
            placing_supports(users_message[hero.enemy.id], hero.enemy)
        else:
            board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
            bot.send_photo(hero.enemy.id, board_img)
            board_img.close()
            main_hero.your_turn = True
            bot.send_message(hero.id, 'Подготовка к игре завершена, можно начинать !')
            bot.send_message(hero.enemy.id, 'Подготовка к игре завершена, можно начинать !')
            bot.send_message(hero.main_hero.id, 'Ваш ход ! Воспользуйтесь командой /turn чтобы выбрать действие')
            bot.send_message(hero.main_hero.enemy.id, 'Сейчас ход вашего противника')
    elif cells[0] in zone and cells[0] != hero.current_cell:
        bot.send_message(hero.id, 'Вы должны ввести номре одной клетки, попробуйте заново')
        bot.register_next_step_handler(message, lambda message: placing_jackalope(message, hero, zone))
    elif len(cells) == 1 and cells[0] != hero.current_cell:
        bot.send_message(hero.id, 'Нужно выбрать клетку в зоне вашего героя, попробуйте заново')
        bot.register_next_step_handler(message, lambda message: placing_jackalope(message, hero, zone))
    elif len(cells) == 1 and cells[0] in zone:
        bot.send_message(hero.id, 'Нельзя ставить помощника на одну клетку с героем, попробуйте заново')
        bot.register_next_step_handler(message, lambda message: placing_jackalope(message, hero, zone))
    else:
        bot.send_message(hero.id, 'Вы совершили несколько ошибок в расстановке персонажей, прочтите правила /rules')
        bot.register_next_step_handler(message, lambda message: placing_jackalope(message, hero, zone))


@bot.message_handler(commands=['hand'])
def show_hand_command(message):
    users_nicknames = {users_id[x]: x for x in users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id not in heroes:
        bot.send_message(message.chat.id, 'Вы не находитесь в игре, создайте игру командой /game_start')
        return
    bot.send_message(message.chat.id, 'Карты на вашей руке:')
    show_hand(heroes[message.chat.id])


@bot.message_handler(commands=['turn'])
def start_turn(message):
    users_nicknames = {users_id[x]: x for x in users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id not in heroes:
        bot.send_message(message.chat.id, 'Вы не находитесь в игре, создайте игру командой /game_start')
        return
    hero = heroes[message.chat.id]
    if not hero.your_turn:
        bot.send_message(hero.id, 'Сейчас не ваш ход, дождитесь окончания хода противника')
        return
    if check_actions(hero, False): return
    if check_deth(hero): return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    maneuver_button = types.KeyboardButton('Маневр')
    scheme_button = types.KeyboardButton('Прием')
    attack_button = types.KeyboardButton('Атака')
    markup.add(maneuver_button, scheme_button, attack_button)
    bot.send_message(hero.id, 'Выберите действие', reply_markup=markup)
    bot.register_next_step_handler(message, choose_action)


def check_deth(hero):
    if hero.hp == 0:  # на случай смерти от фатига
        bot.send_message(hero.id, 'Вы проиграли')
        bot.send_message(hero.enemy.id, 'Вы выиграли')
        message = users_message[hero.id]
        end_game(message)
        return True
    return False


def check_actions(hero, show=True):
    if hero.actions == 2:
        if hero.str == 'bigfoot':
            hero.effect()
            hero.enemy.effect()
            while not hero.enemy.effect_done:
                if not randint(0, 100):
                    print('hero effect')
        hero.your_turn = False
        hero.enemy.your_turn = True
        hero.actions = 0
        bot.send_message(hero.id, 'Ваш ход окончен')
        check_cards_in_hand(hero)
        bot.send_message(hero.enemy.id, 'Ваш ход !\nВоспользуйтесь командой /turn, чтобы выбрать действие')
        return True
    if hero.actions == 1 and show:
        bot.send_message(hero.id, 'У вас есть еще 1 действие, воспользуйтесь коммандой /turn чтобы продолжить ход')
        return False
    '''if hero.str == 'medusa' and hero.actions == 0 and hero.do_effect:
        hero.effect()
        while not hero.effect_done:
            if not randint(0, 100):
                print('hero effect')
        hero.do_effect = False'''
    if hero.actions == 0:
        for character in hero.characters:
            character.last_cell = character.current_cell
    return False


def check_cards_in_hand(hero):
    count = len(hero.hand)
    if count <= 7:
        return
    else:
        count -= 7
        if count == 1:
            bot.send_message(hero.id, 'У вас на руке слишком много карт, выберите карту, которую хотите сбросить и '
                                      'отправьте ее номер')
        else:
            bot.send_message(hero.id, 'У вас на руке слишком много карт, выберите карты, которые хотите сбросить и '
                                      'отправьте их номера\n' f'карты пронумерованы сверху вниз начиная с 1, вам нужно '
                                      f'сбросить {count} карт'.format(count))
        show_hand(hero)
        message = users_message[hero.id]
        bot.register_next_step_handler(message, lambda message: choose_discard_cards(message, count))


def choose_discard_cards(message, count):
    hero = heroes[message.chat.id]
    try:
        [int(num) for num in message.text.split()]
    except:
        bot.send_message(hero.id, 'Отправьте НОМЕРА карт')
        bot.register_next_step_handler(message, lambda message: choose_discard_cards(message, count))
        return
    discarding_cards = [int(num) for num in message.text.split()]
    if len(discarding_cards) != count:
        bot.send_message(hero.id, f'Вам нужно сбросить {count} карт, а вы выбрали {len(discarding_cards)} карт'.format(
            count, len(discarding_cards)))
        bot.register_next_step_handler(message, lambda message: choose_discard_cards(message, count))
        return
    for num in message.text.split():
        hero.discard_card(int(num) - 1)


def choose_action(message):
    hero = heroes[message.chat.id]
    hero.do_effect = True
    if message.text == 'Маневр':
        bot.send_message(hero.enemy.id, 'Ваш противник совершает маневр')
        hero.draw_card()
        bot.send_message(hero.id, 'Отправьте номер карты, которой хотите сбросить для усиления маневра\nВ вашей руке '
                                  'карты пронумерованы сверху вниз начиная с 1\nОтправь 0 если не хочешь усилять маневр')
        bot.register_next_step_handler(message, increase_maneuver)
    elif message.text == 'Прием':
        bot.send_message(hero.enemy.id, 'Ваш противник играет карту приема')
        check_scheme(message)
    elif message.text == 'Атака':
        bot.send_message(hero.enemy.id, 'Ваш противник атакует вас !')
        check_attack(hero)
    else:
        bot.send_message(hero.enemy.id, 'Ваш противник придурок')
        bot.send_message(message.chat.id, 'Неизвестная комманда')


def check_scheme(message):
    hero = heroes[message.chat.id]
    hand = hero.hand
    pool = []
    for card in hand:
        if card.type == 'scheme':
            bot.send_message(message.chat.id, str(hand.index(card) + 1))
            card.show_card()
            pool.append(card)
    if len(pool) == 0:
        bot.send_message(hero.id, 'У вас нет карт приемов')
        return
    bot.send_message(hero.id, 'Выберите карту, которую хотите разыграть и отправьте ее номер')
    bot.register_next_step_handler(message, play_scheme)


def play_scheme(message):
    hero = heroes[message.chat.id]
    hand = hero.hand
    try:
        int(message.text)
    except:
        bot.send_message(hero.id, 'Отправьте НОМЕР карты')
        bot.register_next_step_handler(message, play_scheme)
        return
    num = int(message.text) - 1
    if 0 > num or num >= len(hand):
        bot.send_message(hero.id, 'У вас в руке нет карты с таким номером')
        bot.register_next_step_handler(message, play_scheme)
        return
    if hand[num].type != 'scheme':
        bot.send_message(hero.id, 'Выбранная карта не является картой маневра')
        bot.register_next_step_handler(message, play_scheme)
        return
    hand[num].effect()
    while not hero.effect_done:
        if not randint(0,100):
            print('waiting for playing scheme')
    hero.effect_done = False
    hero.actions += 1
    hand[num].show_card(hero.enemy)
    hand.pop(num)
    bot.send_message(hero.enemy.id, f'Ваш противник разыграл карту приема, это было его {hero.actions}е действие'.format(hero.actions))
    check_actions(hero)
    check_deth(hero.enemy)


########################################################################################################################


def increase_maneuver(message):
    if message.text == '0':
        play_maneuver(message, 0)
        return
    hero = heroes[message.chat.id]
    hand = hero.hand
    try:
        int(message.text)
    except:
        bot.send_message(hero.id, 'Отправьте НОМЕР карты')
        bot.register_next_step_handler(message, increase_maneuver)
        return
    num = int(message.text) - 1
    if 0 > num or num >= len(hand):
        bot.send_message(hero.id, 'У вас в руке нет карты с таким номером')
        bot.register_next_step_handler(message,increase_maneuver)
        return
    bot.send_message(hero.id, 'Сбрасываю карту')
    increasing = hero.discard_card(num)
    print(increasing)
    play_maneuver(message, increasing)


def play_maneuver(message, increasing):
    hero = heroes[message.chat.id]
    board = hero.main_hero.board
    variants = [[] for i in range(len(hero.characters))]
    for character in hero.characters:
        hero.main_hero.places[character] = None
    places = hero.main_hero.places.values()
    board_img = open(f"pictures/boards_in_game/current_board{hero.main_hero.id}.jpg".format(hero.main_hero.id), 'rb')
    bot.send_photo(hero.id, board_img)
    board_img.close()
    for i, character in enumerate(hero.characters):
        board.move_options = []
        print(increasing)
        print(hero.move_value + increasing)
        board.search_ways(character.current_cell, hero.move_value + increasing)
        board.move_options = list(set(board.move_options))
        while any(x in places for x in board.move_options):
            for j in range(len(board.move_options)):
                if board.move_options[j] in places:
                    board.move_options.pop(j)
                    break
        bot.send_message(hero.id, 'Выберите клетку на которую встанет ' + character.str + f'\n{board.move_options}'.format(board.move_options))
        variants[i] = board.move_options
    bot.send_message(hero.id, 'Отправьте номера клеток в том порядке, в котором получили варинты ходов, номера отделяйте побелом')
    bot.register_next_step_handler(message, lambda message: move_characters(message, variants))


def move_characters(message, variants):
    hero = heroes[message.chat.id]
    try:
        cells = [int(x) for x in message.text.split()]
    except:
        bot.send_message(hero.id, 'Отправьте НОМЕРА клеток')
        bot.register_next_step_handler(message, lambda message: move_characters(message, variants))
        return
    cells = [int(x) for x in message.text.split()]
    if len(cells) > len(hero.characters):
        bot.send_message(hero.id, 'Выбрано слишком много клеток, попробуйте заново')
        bot.register_next_step_handler(message, lambda message: move_characters(message, variants))
        return
    if len(set(cells)) == len(cells) and all(x in variants[i] for i, x in enumerate(cells)) and len(cells) == len(hero.characters):
        main_hero = hero.main_hero
        places = main_hero.places
        for i, character in enumerate(hero.characters):
            places[character] = cells[i]
            character.current_cell = cells[i]
        hero.main_hero.board.render()
        board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
        bot.send_photo(hero.id, board_img)
        board_img.close()
        board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
        hero.actions += 1
        bot.send_message(hero.enemy.id, f'Ваш противник закончил маневр, это было его {hero.actions}е действие'.format(hero.actions))
        check_actions(hero)
        bot.send_photo(hero.enemy.id, board_img)
        board_img.close()
    elif all(x in variants[i] for i, x in enumerate(cells)) and len(cells) == len(hero.characters):
        bot.send_message(hero.id, 'Нельзя ставить несколько персонажей на одну ячейку, попробуйте заново')
        bot.register_next_step_handler(message, lambda message: move_characters(message, variants))
    elif len(set(cells)) == len(cells) and len(cells) == len(hero.characters):
        for i, x in enumerate(cells):
            if x not in variants[i]:
                bot.send_message(hero.id, 'Персонаж ' + hero.characters[i].str + ' не может дойти до клетки ' + str(cells[i]))
        bot.send_message(hero.id, 'Попробуйте еще раз')
        bot.register_next_step_handler(message, lambda message: move_characters(message, variants))
    elif len(set(cells)) == len(cells) and all(x in variants[i] for i, x in enumerate(cells)):
        bot.send_message(hero.id, 'Укажите клетки для всех персонажей сразу')
        bot.register_next_step_handler(message, lambda message: move_characters(message, variants))
    else:
        bot.send_message(hero.id, 'Вы совершили несколько ошибок в расстановке персонажей, прочтите правила /rules')
        bot.register_next_step_handler(message, lambda message: move_characters(message, variants))


def check_attack(hero):
    variants = {}
    places = hero.main_hero.places
    board = hero.main_hero.board
    reverse_places = {places[x]: x for x in places}
    for character in hero.characters:
        if character.type == 'melee':
            directions = board.cells_ways[character.current_cell]
            for enemy_cell in directions:
                if enemy_cell in reverse_places:
                    enemy = reverse_places[enemy_cell]
                    if enemy in hero.enemy.characters:
                        bot.send_message(hero.id, 'Ваш ' + character.str + ' может атаковать ' + enemy.str + ' противника')
                        variants[character] = enemy
        if character.type == 'distance':
            directions = []
            for color in board.cells_color[character.current_cell]:
                directions += board.color_directions[color]
            for enemy_cell in directions:
                if enemy_cell in reverse_places:
                    enemy = reverse_places[enemy_cell]
                    if enemy in hero.enemy.characters:
                        bot.send_message(hero.id, 'Ваш ' + character.str + ' может атаковать ' + enemy.str + ' противника')
                        variants[character] = enemy
    if len(variants) == 0:
        bot.send_message(hero.id, 'Вам некого атаковать, поэтому ваша атака заменена на маневр с передвижением на '
                                  '0 ячеек')
        hero.draw_card()
        hero.actions += 1
        bot.send_message(hero.enemy.id, 'Ваш противник не смог никого атаковать и вместо атаки совершил маневр с '
                                        f'передвижением на 0 ячеек, это было его {hero.actions} действие'.format(hero.actions))
        check_actions(hero)
        return
    if all(card.who != 'all' and card.who != attacking.str for card in hero.hand if card.type != 'scheme'
                                                                and card.type != 'defence' for attacking in variants):
        bot.send_message(hero.id, 'У вас нет карт для атаки в таком положении, поэтому ваша атака заменена на маневр с передвижением на '
                                  '0 ячеек')
        hero.draw_card()
        hero.actions += 1
        bot.send_message(hero.enemy.id, 'Ваш противник не смог атаковать и вместо атаки совершил маневр с '
                                        f'передвижением на 0 ячеек, это было его {hero.actions} действие'.format(hero.actions))
        check_actions(hero)
        return
    bot.send_message(hero.id, 'Выберите персонажа, которым будете атаковать и противника, которого будете атаковать\n'
                              'через пробел сначала напишите имя своего персонажа, потом имя персонажа протиника.'
                              'Указывать надо имена персонажей в таком же формате как в вышеперечисленных вариантах')
    bot.register_next_step_handler(users_message[hero.id], lambda message: choose_attack_character(message, variants))


def choose_attack_character(message, variants):
    hero = heroes[message.chat.id]
    ans = message.text.split()
    if len(ans) != 2:
        bot.send_message(hero.id, 'Оправьте ДВА слова: имя вашего атакующего персонажа и имя персонажа противника, '
                                  'которого будете атаковать, попробуйте еще раз')
        bot.register_next_step_handler(message, lambda message: choose_attack_character(message, variants))
        return
    friends_str = [x.str for x in variants.keys()]
    enemies_str = [x.str for x in variants.values()]
    if ans[0] not in friends_str and ans[1] not in enemies_str:
        bot.send_message(hero.id, 'Имена персонажей отправлены некоректно\nУказывать имена персонажей надо в таком же '
                                  'формате как в вышеперечисленных вариантах, попробуйте еще раз')
        bot.register_next_step_handler(message, lambda message: choose_attack_character(message, variants))
        return
    if ans[0] not in friends_str:
        bot.send_message(hero.id, 'Имя вашего атакующего персонажа указано неверно\nУказывать имена персонажей надо в '
                                  'таком же формате как в вышеперечисленных вариантах, попробуйте еще раз')
        bot.register_next_step_handler(message, lambda message: choose_attack_character(message, variants))
        return
    if ans[1] not in enemies_str:
        bot.send_message(hero.id, 'Имя персонажа противника, которого вы хотите атаковать указано неверно\nУказывать '
                                  'имена персонажей надо в таком же формате как в вышеперечисленных вариантах, '
                                  'попробуйте еще раз')
        bot.register_next_step_handler(message, lambda message: choose_attack_character(message, variants))
        return
    attacking = None
    defending = None
    for x in variants:
        if x.str == ans[0] and variants[x].str == ans[1]:
            attacking = x
            defending = variants[x]
    if attacking is None or defending is None:
        bot.send_message(hero.id, 'Эти персонажи не могут биться друг с другом, выберите других персонажей')
        bot.register_next_step_handler(message, lambda message: choose_attack_character(message, variants))
        return
    bot.send_message(hero.enemy.id, f'Ваш противник атакует {defending.str} своим {attacking.str}'.format(defending.str, attacking.str))
    defending.hero.is_defence = defending
    bot.send_message(hero.id, f'Отлично, персонаж {attacking.str} атакует персонажа {defending.str} '.format(defending.str, attacking.str))
    show_hand(hero)
    bot.send_message(hero.id, 'Отправьте номер карты, которой хотите атаковать')
    bot.register_next_step_handler(message, lambda message: choose_attack_card(message, attacking, defending))


def choose_attack_card(message, attacking, defending):
    hero = heroes[message.chat.id]
    hand = hero.hand
    try:
        int(message.text)
    except:
        bot.send_message(hero.id, 'Отправьте НОМЕР карты')
        bot.register_next_step_handler(message, lambda message: choose_attack_card(message, attacking, defending))
        return
    num = int(message.text) - 1
    if 0 > num or num >= len(hand):
        bot.send_message(hero.id, 'У вас в руке нет карты с таким номером, попробуйте еще раз')
        bot.register_next_step_handler(message, lambda message: choose_attack_card(message, attacking, defending))
        return
    card = hand[num]
    if card.type != 'attack' and card.type != 'versatile':
        bot.send_message(hero.id, 'Выбранная карта не является картой атаки или универсальной картой, попробуйте еще раз')
        bot.register_next_step_handler(message, lambda message: choose_attack_card(message, attacking, defending))
        return
    if card.who != attacking.str and card.who != 'all':
        bot.send_message(hero.id, f'Вы не можете использовать эту карту за {attacking.str}, эта карта для {card.who}'.format(attacking.str, card.who))
        bot.register_next_step_handler(message, lambda message: choose_attack_card(message, attacking, defending))
        return
    hero.played_card = card
    hero.hand.pop(num)
    bot.send_message(hero.id, 'Карта выбрана, ждем пока ваш противник выберет карту')
    enemy_message = users_message[hero.enemy.id]
    show_hand(hero.enemy)
    bot.send_message(hero.enemy.id, 'Отправьте номер карты, которой хотите защищаться, отправьте 0 если не хотите защищаться')
    bot.register_next_step_handler(enemy_message, lambda enemy_message: choose_defence_card(enemy_message, attacking, defending))


def choose_defence_card(message, attacking, defending):
    hero = heroes[message.chat.id]
    hand = hero.hand
    try:
        int(message.text)
    except:
        bot.send_message(hero.id, 'Отправьте НОМЕР карты')
        bot.register_next_step_handler(message, lambda message: choose_defence_card(message, attacking, defending))
        return
    num = int(message.text) - 1
    if num == -1:
        hero.played_card = None
        hero.is_defence = None
        playing_battle(hero.enemy, attacking, defending)
        return

    if 0 > num or num >= len(hand):
        bot.send_message(hero.id, 'У вас в руке нет карты с таким номером, попробуйте еще раз')
        bot.register_next_step_handler(message, lambda message: choose_defence_card(message, attacking, defending))
        return
    card = hand[num]
    if card.type != 'defence' and card.type != 'versatile':
        bot.send_message(hero.id,
                         'Выбранная карта не является картой защиты или универсальной картой, попробуйте еще раз')
        bot.register_next_step_handler(message, lambda message: choose_defence_card(message, attacking, defending))
        return
    if card.who != defending.str and card.who != 'all':
        bot.send_message(hero.id,
                         f'Вы не можете использовать эту карту за {defending.str}, эта карта для {card.who}'.format(
                             attacking.str, card.who))
        bot.register_next_step_handler(message, lambda message: choose_defence_card(message, attacking, defending))
        return
    hero.played_card = card
    hero.hand.pop(num)
    hero.is_defence = None
    playing_battle(hero.enemy, attacking, defending)


def playing_battle(hero, attacking, defending):
    hero.hero.hero_in_battle = attacking
    hero.hero.enemy.hero_in_battle = defending
    if defending.hero.played_card is None:
        bot.send_message(hero.id, 'Ваш противник не защищается')
        bot.send_message(hero.enemy.id, 'Вскрываем карты !')
        attack_card = hero.played_card
        attack_card.show_card(hero.enemy)
        attack_card.show_card()
        if 1 <= attack_card.effect_moment <= 2:
            attack_card.effect()
            while not attacking.hero.effect_done:
                if not randint(0, 100):
                    print('attacking effect')
        hero.win = True
        hero.enemy.win = False
        damage = attack_card.value
        bot.send_message(hero.enemy.id, 'Вы проиграли в бою')
        bot.send_message(hero.id, 'Вы победили в бою !')
        defending.deal_damage(damage)
        bot.send_message(hero.enemy.id, f'Ваш персонаж {defending.str} получил {damage} урона'.format(damage))
        '''if attack_card.effect_moment == 3 and attacking.hp > 0:
            attack_card.effect()
            while not attacking.hero.effect_done:
                ...'''
    else:
        attack_card = hero.played_card
        defence_card = hero.enemy.played_card
        bot.send_message(hero.id, 'Вскрываем карты !')
        attack_card.show_card()
        defence_card.show_card(hero)
        bot.send_message(hero.enemy.id, 'Вскрываем карты !')
        attack_card.show_card(hero.enemy)
        defence_card.show_card()
        if defence_card.effect_moment == 1 and hero.enemy.do_effect:
            defence_card.effect()
            while not defending.hero.effect_done:
                ...
        if attack_card.effect_moment == 1 and hero.do_effect:
            attack_card.effect()
            while not attacking.hero.effect_done:
                ...
        if defence_card.effect_moment == 2 and hero.enemy.do_effect:
            defence_card.effect()
            while not defending.hero.effect_done:
                ...
        if attack_card.effect_moment == 2 and hero.do_effect:
            attack_card.effect()
            while not attacking.hero.effect_done:
                ...
        damage = 0 if attack_card.value <= defence_card.value else attack_card.value - defence_card.value
        if damage == 0:
            hero.enemy.win = True
            bot.send_message(hero.id, 'Вы проиграли в бою')
            bot.send_message(hero.enemy.id, 'Вы победили в бою !')
        else:
            hero.win = True
            bot.send_message(hero.enemy.id, 'Вы проиграли в бою')
            bot.send_message(hero.id, 'Вы победили в бою !')
        defending.deal_damage(damage)
        bot.send_message(hero.enemy.id, f'Ваш персонаж {defending.str} получил {damage} урона'.format(damage))
        if defence_card.effect_moment == 3 and hero.enemy.do_effect:
            defence_card.effect()
            while not defending.hero.effect_done:
                ...
    if attack_card.effect_moment == 3 and hero.do_effect:
        attack_card.effect()
        while not attacking.hero.effect_done:
            ...

    hero.do_effect = True
    hero.enemy.do_effect = True
    hero.played_card = None
    hero.enemy.played_card = None
    hero.win = False
    hero.enemy.win = False
    hero.hero.hero_in_battle = None
    hero.hero.enemy.hero_in_battle = None
    hero.effect_done = False
    hero.enemy.effect_done = False
    hero.actions += 1
    bot.send_message(hero.enemy.id, f'Ваш противник закончил атаку, это было его {hero.actions} действие'.format(hero.actions))
    bot.send_message(hero.id, f'Это было ваше {hero.actions} действие'.format(hero.actions))
    check_actions(hero)
    check_deth(hero.enemy)

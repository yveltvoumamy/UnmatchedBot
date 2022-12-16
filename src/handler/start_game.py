from src.game_box.board import Board
from src.game_box.bigfoot import Bigfoot, Jackalope
from src.game_box.medusa import Medusa, Harpy
from src.game_box.bigfoot_cards import *
from src.game_box.medusa import *
from telebot import types
from src.auxiliary_objects.command_parent import Commands
from src.game_box.medusa_cards import *
from random import randint


class StartGame(Commands):

    def pick_heroes(self, message, opponent_id):
        if message.text == 'Медуза':
            medusa, bigfoot = self.first_hero_medusa(message, opponent_id)
        elif message.text == 'Бигфут':
            medusa, bigfoot = self.first_hero_bigfoot(message, opponent_id)
        else:
            self.bot.send_message(message.chat.id, 'Такого персонажа еще нет')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            medusa_button = types.KeyboardButton('Медуза')
            bigfoot_button = types.KeyboardButton('Бигфут')
            markup.add(medusa_button, bigfoot_button)
            self.bot.send_message(message.chat.id, 'Выберите персонажа', reply_markup=markup)
            self.bot.register_next_step_handler(message, lambda message: self.pick_heroes(message, opponent_id))
            return

        self.bot.send_message(medusa.main_hero.enemy.id, 'Карты в вашей руке:')
        self.bot.send_message(medusa.main_hero.id, 'Карты в вашей руке:')
        for i in range(5):
            medusa.draw_card()
            bigfoot.draw_card()
        self.bot.send_message(medusa.main_hero.enemy.id, 'Ваш противник выбирает куда поставить помощников')
        self.placing_supports(self.users_message[medusa.main_hero.id], medusa.main_hero)

    def first_hero_medusa(self, message, opponent_id):
        first_hero = randint(0, 1)
        self.create_hero('медуза', message.chat.id)
        self.create_hero('бигфут', opponent_id)
        medusa, bigfoot = self.heroes[message.chat.id], self.heroes[opponent_id]
        if first_hero:
            medusa.current_cell, bigfoot.current_cell = 30, 22
            medusa.places = {medusa: 30, bigfoot: 22}
            self.bot.send_message(message.chat.id, 'Вы ходите первым')
            medusa.main_hero, bigfoot.main_hero = medusa, medusa
        else:
            bigfoot.current_cell, medusa.current_cell = 30, 22
            bigfoot.places = {medusa: 22, bigfoot: 30}
            self.bot.send_message(message.chat.id, 'Ваш противник ходит первым')
            medusa.main_hero, bigfoot.main_hero = bigfoot, bigfoot
        bigfoot.id, medusa.id = opponent_id, message.chat.id
        medusa.enemy_id, medusa.enemy = opponent_id, bigfoot
        bigfoot.enemy_id, bigfoot.enemy = message.chat.id, medusa
        medusa.main_hero.board = Board(self.sc, medusa.main_hero)
        self.shuffle_deck(medusa)
        self.shuffle_deck(bigfoot)
        self.bot.send_message(message.chat.id,
                              f'Ваш персонаж {medusa.str}, персонаж вашего противника {bigfoot.str}'.format(medusa,
                                                                                                            bigfoot))
        return medusa, bigfoot

    def first_hero_bigfoot(self, message, opponent_id):
        first_hero = randint(0, 1)
        self.create_hero('бигфут', message.chat.id)
        self.create_hero('медуза', opponent_id)
        bigfoot, medusa = self.heroes[message.chat.id], self.heroes[opponent_id]
        if first_hero:
            bigfoot.current_cell, medusa.current_cell = 30, 22
            bigfoot.places = {medusa: 22, bigfoot: 30}
            self.bot.send_message(message.chat.id, 'Вы ходите первым')
            medusa.main_hero, bigfoot.main_hero = bigfoot, bigfoot
        else:
            medusa.current_cell, bigfoot.current_cell = 30, 22
            medusa.places = {medusa: 30, bigfoot: 22}
            self.bot.send_message(message.chat.id, 'Ваш противник ходит первым')
            medusa.main_hero, bigfoot.main_hero = medusa, medusa
        medusa.id, bigfoot.id = opponent_id, message.chat.id
        medusa.enemy_id, medusa.enemy = message.chat.id, bigfoot
        bigfoot.enemy_id, bigfoot.enemy = opponent_id, medusa
        medusa.main_hero.board = Board(self.sc, medusa.main_hero)
        self.shuffle_deck(medusa)
        self.shuffle_deck(bigfoot)
        self.bot.send_message(message.chat.id,
                              f'Ваш персонаж {bigfoot.str}, пресонаж вашего противника {medusa.str}'.format(bigfoot,
                                                                                                            medusa))
        return medusa, bigfoot

    def create_hero(self, hero, your_id):
        if hero == 'медуза':
            medusa_cards = [MomentaryGlance, ClutchingClaws, Dash, Fient, GazeOfStone, HissAndSlither, Regroup,
                            Snipe, SecondShot, TheHoundsOfMightyZeus]
            self.heroes[your_id] = Medusa(medusa_cards, self.bot)
        elif hero == 'бигфут':
            bigfoot_cards = [CrashThroughTheTrees, Disengage, FientBigfoot, Hoax, ItsJustYourImagination,
                             JackalopeHorns, LargerThenLife, MomentousShift, RegroupBigfoot, Savagery]
            self.heroes[your_id] = Bigfoot(bigfoot_cards, self.bot)

    def shuffle_deck(self, current_hero):
        cards = current_hero.deck
        open_cards = []
        for i in range(len(cards)):
            open_cards.append(cards[i].add_attr(current_hero, current_hero.enemy, self.bot))
        deck = []
        while len(open_cards) != 0:
            curr_card = randint(0, len(cards) - 1)
            deck.append(cards[curr_card].add_attr(current_hero, current_hero.enemy, self.bot))
            print(open_cards[curr_card])
            if open_cards[curr_card].count_in_deck == 1:
                cards.pop(curr_card)
                open_cards.pop(curr_card)
            else:
                cards[curr_card].count_in_deck -= 1

        current_hero.deck = deck

    def placing_supports(self, message, hero):
        main_hero = hero.main_hero
        main_hero.board.render()
        board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
        self.bot.send_photo(hero.id, board_img)
        board_img.close()
        cell = hero.current_cell
        zone = []
        for x in main_hero.board.cells_color[cell]:
            zone += main_hero.board.color_directions[x]
        if hero.str == 'medusa':
            self.bot.send_message(hero.id,
                             'Укажите ячейки, в которые хотите поставить своих гарпий, номера ячеек разделяйте '
                             'пробелом')
            self.bot.register_next_step_handler(message, lambda message: self.placing_harpies(message, hero, zone))
            print(message.text)
            print(self.bot)
        elif hero.str == 'bigfoot':
            self.bot.send_message(hero.id, 'Укажите ячейку, в которую хотите поставить помощника')
            self.bot.register_next_step_handler(message, lambda message: self.placing_jackalope(message, hero, zone))
            print(message.text)
            print(self.bot)
        else:
            self.bot.send_message(hero.id,
                             f'Неверное имя персонажа, произошла ошибка внутри программы функция \npick_heroes('
                             f')\nplacing_supports{hero}'.format(hero))

    def placing_harpies(self, message, hero, zone):
        print('ok')
        try:
            cells = [int(x) for x in message.text.split()]
        except:
            self.bot.send_message(hero.id, 'Отправьте НОМЕРА клеток')
            self.bot.register_next_step_handler(message, lambda message: self.placing_harpies(message, hero, zone))
            return
        cells = [int(x) for x in message.text.split()]
        if len(set(cells)) == len(cells) and all(x in zone for x in cells) and all(
                x != hero.current_cell for x in cells) and len(cells) == 3:
            main_hero = hero.main_hero
            main_hero.places[hero.harpy1] = cells[0]
            main_hero.places[hero.harpy2] = cells[1]
            main_hero.places[hero.harpy3] = cells[2]
            hero.harpy1.current_cell = cells[0]
            hero.harpy2.current_cell = cells[1]
            hero.harpy3.current_cell = cells[2]
            main_hero.board.render()
            board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
            self.bot.send_photo(hero.id, board_img)
            board_img.close()
            if hero.id == hero.main_hero.id:
                self.bot.send_message(hero.id, 'Теперь очередь вашего противника')
                self.placing_supports(data_base.users_message[hero.enemy.id], hero.enemy)
            else:
                board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
                self.bot.send_photo(hero.enemy.id, board_img)
                board_img.close()
                main_hero.your_turn = True
                self.bot.send_message(hero.id, 'Подготовка к игре завершена, можно начинать !')
                self.bot.send_message(hero.enemy.id, 'Подготовка к игре завершена, можно начинать !')
                self.bot.send_message(hero.main_hero.id, 'Ваш ход ! Воспользуйтесь командой /turn чтобы выбрать действие')
                self.bot.send_message(hero.main_hero.enemy.id, 'Сейчас ход вашего противника')

        elif all(x in zone for x in cells) and all(x != hero.current_cell for x in cells) and len(cells) == 3:
            self.bot.send_message(hero.id, 'Нельзя ставить несколько персонажей на одну ячейку, попробуйте заново')
            self.bot.register_next_step_handler(message, lambda message: self.placing_harpies(message, hero, zone))
        elif len(set(cells)) == len(cells) and all(x != hero.current_cell for x in cells) and len(cells) == 3:
            self.bot.send_message(hero.id, 'Нужно поставить всех помощников в одну зону с главным героем, попробуйте заново')
            self.bot.register_next_step_handler(message, lambda message: self.placing_harpies(message, hero, zone))
        elif len(set(cells)) == len(cells) and all(x in zone for x in cells) and len(cells) == 3:
            self.bot.send_message(hero.id, 'Нельзя ставить помощников на одну ячейкку с героем')
            self.bot.register_next_step_handler(message, lambda message: self.placing_harpies(message, hero, zone))
        elif len(set(cells)) == len(cells) and all(x in zone for x in cells) and all(
                x != hero.current_cell for x in cells):
            self.bot.send_message(hero.id, 'Укажите клетки для всех персонажей сразу')
            self.bot.register_next_step_handler(message, lambda message: self.placing_harpies(message, hero, zone))
        else:
            self.bot.send_message(hero.id, 'Вы совершили несколько ошибок в расстановке персонажей, прочтите правила /rules')
            self.bot.register_next_step_handler(message, lambda message: self.placing_harpies(message, hero, zone))

    def placing_jackalope(self, message, hero, zone):
        print('ok')
        try:
            cells = [int(x) for x in message.text.split()]
        except:
            self.bot.send_message(hero.id, 'Отправьте НОМЕРА клеток')
            self.bot.register_next_step_handler(message, lambda message: self.placing_jackalope(message, hero, zone))
            return
        cells = [int(x) for x in message.text.split()]
        if len(cells) == 1 and cells[0] in zone and cells[0] != hero.current_cell:
            main_hero = hero.main_hero
            main_hero.places[hero.jackalope] = cells[0]
            hero.jackalope.current_cell = cells[0]
            main_hero.board.render()
            board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
            self.bot.send_photo(hero.id, board_img)
            board_img.close()
            if hero == hero.main_hero:
                self.bot.send_message(hero.id, 'Теперь очередь вашего противника')
                self.placing_supports(data_base.users_message[hero.enemy.id], hero.enemy)
            else:
                board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
                self.bot.send_photo(hero.enemy.id, board_img)
                board_img.close()
                main_hero.your_turn = True
                self.bot.send_message(hero.id, 'Подготовка к игре завершена, можно начинать !')
                self.bot.send_message(hero.enemy.id, 'Подготовка к игре завершена, можно начинать !')
                self.bot.send_message(hero.main_hero.id, 'Ваш ход ! Воспользуйтесь командой /turn чтобы выбрать действие')
                self.bot.send_message(hero.main_hero.enemy.id, 'Сейчас ход вашего противника')
        elif cells[0] in zone and cells[0] != hero.current_cell:
            self.bot.send_message(hero.id, 'Вы должны ввести номре одной клетки, попробуйте заново')
            self.bot.register_next_step_handler(message, lambda message: self.placing_jackalope(message, hero, zone))
        elif len(cells) == 1 and cells[0] != hero.current_cell:
            self.bot.send_message(hero.id, 'Нужно выбрать клетку в зоне вашего героя, попробуйте заново')
            self.bot.register_next_step_handler(message, lambda message: self.placing_jackalope(message, hero, zone))
        elif len(cells) == 1 and cells[0] in zone:
            self.bot.send_message(hero.id, 'Нельзя ставить помощника на одну клетку с героем, попробуйте заново')
            self.bot.register_next_step_handler(message, lambda message: self.placing_jackalope(message, hero, zone))
        else:
            self.bot.send_message(hero.id, 'Вы совершили несколько ошибок в расстановке персонажей, прочтите правила /rules')
            self.bot.register_next_step_handler(message, lambda message: self.placing_jackalope(message, hero, zone))

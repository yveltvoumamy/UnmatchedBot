import pygame
from src.data_objects.data_base import DataBase
data_base = DataBase()


class Hero():
    hp_img, img, current_cell, move_value, str, hp = None, None, None, None, None, None
    main_hero, played_card, type = None, None, None
    is_defence, has_moved, win, do_effect = None, False, False, True
    last_cell, increase = None, None
    sc = pygame.display.set_mode((1800, 1000))

    def discard_card(self, num):
        increase = self.hand[num].increase_value
        self.bot.send_message(self.enemy.id, 'Ваш противник сбросил эту карту')
        self.hand[num].show_card(self.enemy)
        self.hand.pop(num)
        return increase

    def draw_card(self):
        self.bot.send_message(self.id, 'Вы берете карту')
        if len(self.deck) != 0:
            card = self.deck[-1]
            self.hand.append(card)
            card.show_card()
            self.deck.pop(-1)
            self.bot.send_message(self.enemy.id, 'Ваш противник берет карту')
        else:
            for character in self.characters:
                character.deal_damage(2)
            self.bot.send_message(self.id, 'У вас не осталось карт, вы получаете 2 урона')
            self.bot.send_message(self.enemy.id, 'У вашего противника не осталось карт ! Он получает 2 урона')

    def show_hp(self):
        print(str(self.hp_img[self.hp]))
        img = open(self.hp_img[self.hp], 'rb')
        self.bot.send_photo(self.id, img)
        img.close()
        if self.str == 'bigfoot':
            img_jackalope = open(self.jackalope.hp_img[self.jackalope.hp], 'rb')
            self.bot.send_photo(self.id, img_jackalope)
            img_jackalope.close()

    def deal_damage(self, num):
        self.hp -= num
        if self.hp <= 0:
            del self.hero.main_hero.places[self]
            self.hero.characters.pop(self.hero.characters.index(self))
            self.hp = 0
            main_hero = self.hero.main_hero
            main_hero.board.render()
            board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
            self.hero.bot.send_photo(self.hero.id, board_img)
            board_img.close()
            board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
            self.hero.bot.send_photo(self.hero.enemy.id, board_img)
            board_img.close()
        self.hero.show_hp()

    def move(self, num=None, throug=False, is_effect=False, hero=None):
        if num is not None:
            self.move_value, move_value = num, self.move_value
        board = self.hero.main_hero.board
        board.move_options = []
        board.search_ways(self.current_cell, self.move_value, throug, hero=hero)
        variants = list(set(board.move_options + [self.current_cell]))
        print(variants)
        self.hero.bot.send_message(self.hero.id, f'Выбери одну из ячеек:\n{variants}'.format(variants))
        main_hero = self.hero.main_hero
        board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
        self.hero.bot.send_photo(self.hero.id, board_img)
        board_img.close()
        message = data_base.users_message[self.hero.id]
        self.move_value = move_value
        self.hero.bot.register_next_step_handler(message, lambda message: self.movement(message, is_effect))

    def movement(self, message, is_effect):
        try:
            int(message.text)
        except:
            self.hero.bot.send_message(self.hero.id, 'Отправьте НОМЕР клетки')
            self.hero.bot.register_next_step_handler(message, lambda message: self.movement(message, is_effect))
            return
        if all(int(message.text) != cell for cell in self.hero.main_hero.board.move_options) and int(
                message.text) != self.current_cell:
            self.hero.bot.send_message(self.hero.id, 'Нельзя переместиться на эту клетку')
            self.hero.bot.register_next_step_handler(message, lambda message: self.movement(message, is_effect))
            return
        places = self.hero.main_hero.places
        for cell in places.values():
            if cell == int(message.text) and cell != self.current_cell:
                self.hero.bot.send_message(self.hero.id, 'На этой клетке стоит другой персонаж')
                self.hero.bot.register_next_step_handler(message, lambda message: self.movement(message, is_effect))
                return
        cell = int(message.text)
        self.hero.main_hero.places[self] = cell
        self.current_cell = cell
        main_hero = self.hero.main_hero
        main_hero.board.render()
        board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
        self.hero.bot.send_photo(self.hero.id, board_img)
        board_img.close()
        if is_effect:
            print('ok')
            self.hero.effect_done = True

    def choose_discard_card_for_increasing(self, message, card, is_effect):
        hand = self.hand
        try:
            int(message.text)
        except:
            self.bot.send_message(self.id, 'Некоретный номер карты, считается что вы ничего не сбросили')
            self.bot.register_next_step_handler(message,
                                                lambda message: self.hero.choose_discard_card_for_increasing(message,
                                                                                                             is_effect))
            return
        num = int(message.text) - 1
        if num == -1:
            return
        if 0 <= num < len(hand):
            card.value += self.discard_card(num)
            if is_effect:
                self.hero.effect_done = True
            return
        self.bot.send_message(self.id, 'У вас нет в руке карты с таким номером, считается что вы ничего не сбросили')
        self.bot.register_next_step_handler(message,
                                            lambda message: self.hero.choose_discard_card_for_increasing(message,
                                                                                                         is_effect))
        return

    def choose_discard_card(self, is_effect=False):
        for card in self.hand:
            card.show_card()
        self.bot.send_message(self.id, 'Выберите карту, которую хотите сбросить и отправьте ее номер')
        message = data_base.users_message[self.id]
        self.bot.register_next_step_handler(message, lambda message: self.check_discard(message, is_effect))

    def check_discard(self, message, is_effect):
        hand = self.hand

        try:
            int(message.text)
        except:
            self.bot.send_message(self.id, 'Отправьте НОМЕР карты')
            self.bot.register_next_step_handler(message, lambda message: self.check_discard(message, is_effect))
            return
        num = int(message.text) - 1
        if 0 <= num < len(hand):
            self.discard_card(num)
            if is_effect:
                self.hero.effect_done = True
            return
        self.bot.send_message(self.id, 'У вас нет в руке карты с таким номером, поробуйте заново')
        self.bot.register_next_step_handler(message, lambda message: self.check_discard(message, is_effect))


class Support(Hero):
    def __init__(self, hero):
        self.hero = hero

    def discard_card(self, num, message):
        ...

    def choose_discard_card(self, message):
        ...

    def draw_card(self, message):
        ...
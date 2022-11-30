import pygame
from data_base import users_message
img_board = pygame.image.load('pictures/board.png')


class Board:
    i = 0

    def __init__(self, sc, main_hero):
        self.main_hero = main_hero
        self.sc = sc
        self.board_img = img_board

        '''self.medusa_img = pygame.image.load('pictures/medusa/medusa.jpg')
        self.harpy_img = pygame.image.load('pictures/medusa/harpy.jpg')
        self.jackalope_img = pygame.image.load('pictures/bigfoot/jackalope.jpg')
        self.bigfoot_img = pygame.image.load('pictures/bigfoot/bigfoot.jpg')'''

        self.move_options = []

        self.color_directions = {
            'lightgreen': (1, 18, 19, 20, 21, 22), 'red': (1, 2, 3, 4, 5, 6), 'green': (4, 5, 6, 7, 8, 9),
            'grey': (6, 8, 9, 10, 12), 'yellow': (10, 11, 12, 13, 14, 15, 16, 17, 18, 25, 26, 27),
            'brown': (22, 23, 24, 25, 26, 27), 'blue': (3, 26, 27, 28, 29, 30)
        }
        self.cells_color = [[], ['lightgreen', 'red'], ['red'], ['red', 'blue'], ['red', 'green'], ['red', 'green'],
                            ['red', 'green', 'grey'], ['green'], ['green', 'grey'], ['green', 'grey'],
                            ['yellow', 'grey'],
                            ['yellow'], ['yellow', 'grey'], ['yellow'], ['yellow'], ['yellow'], ['yellow'], ['yellow'],
                            ['yellow', 'lightgreen'], ['lightgreen'], ['lightgreen'], ['lightgreen'],
                            ['lightgreen', 'brown'], ['brown'], ['brown'], ['brown', 'yellow'],
                            ['brown', 'yellow', 'blue'],
                            ['brown', 'yellow', 'blue'], ['blue'], ['blue'], ['blue']]

        self.cells_ways = [(), (2, 22), (1, 3), (2, 4, 30), (3, 5), (4, 6, 7), (5, 7, 8), (5, 6, 8), (6, 7, 9), (8, 10),
                           (11, 12, 9), (10, 12, 13, 27), (10, 11, 13), (11, 12, 14), (13, 15), (14, 16, 17),
                           (15, 17, 25),
                           (15, 16, 18), (17, 19), (18, 20), (19, 21), (20, 22), (1, 21, 23), (22, 24), (23, 25),
                           (16, 24, 26),
                           (25, 27, 29), (26, 28, 11), (27, 29), (26, 28, 30), (29, 3)]

        self.cells_coord = [[], [338, 135], [546, 56], [753, 41], [965, 38], [1172, 48], [1403, 38], [1308, 215],
                            [1535, 215], [1630, 401], [1602, 612], [1395, 642], [1507, 815], [1279, 831], [1072, 851],
                            [861, 851], [749, 682], [636, 840], [432, 820], [228, 780], [77, 642], [88, 442], [238, 305],
                            [417, 406],
                            [607, 470], [810, 490], [1004, 543], [1198, 603], [1178, 410], [992, 332], [832, 218]]

    def render(self):  # надо переписать чтобы все персонажи рендерились
        ''''img = self.main_hero.img
        for i in range(1, len(self.cells_coord)):
            self.sc.blit(self.board_img, (0, 0))
            rect = pygame.Rect(*self.cells_coord[i], 100, 100)
            self.sc.blit(img, rect)
            pygame.display.flip()
            pygame.image.save(self.sc, f"pictures/boards_in_game/current_board{i}.jpg".format(i))'''''
        self.sc.blit(self.board_img, (0, 0))
        places = self.main_hero.places
        for character in places:
            cell = places[character]
            print(cell)
            rect = pygame.Rect(*self.cells_coord[cell], 100, 100)
            print(rect)
            print(character.img)
            self.sc.blit(character.img, rect)
            # character.img.close()
        pygame.display.flip()
        main_hero_id = self.main_hero.id
        pygame.image.save(self.sc, f"pictures/boards_in_game/current_board{main_hero_id}.jpg".format(main_hero_id))

    def search_ways(self, current_cell, num, through=False, hero=None):
        places = self.main_hero.places
        reversed_places = {places[x]: x for x in places}
        if num == 0: return
        for x in self.cells_ways[current_cell]:
            if through or (hero is not None and reversed_places[x] in hero.characters):
                self.search_ways(x, num - 1, through)
            if x not in places.values():
                if not through and not (hero is not None and reversed_places[x] in hero.characters):
                    self.search_ways(x, num - 1, through)
                self.move_options += [x]


class Hero():
    hp_img, img, current_cell, move_value, str, hp = None, None, None, None, None, None
    main_hero, played_card, type = None, None, None
    is_defence, has_moved, win, do_effect = None, False, False, True
    last_cell, increase = None, None
    sc = pygame.display.set_mode((1800, 1000))

    '''def __init__(self, deck):
        self.hero = self
        self.deck = deck
        self.hero_in_battle = None # мб фиктивная
        self.hand = []
        self.actions = 0
        self.played_card = None'''

    def discard_card(self, num):
        increase = self.hand[num].increase_value
        'send message to enemy'
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
            img_jackalope = open(hp_img_jackalope[self.jackalope.hp], 'rb')
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
        message = users_message[self.hero.id]
        self.move_value = move_value
        self.hero.bot.register_next_step_handler(message, lambda message: self.movement(message, is_effect))

    def movement(self, message, is_effect):
        try:
            int(message.text)
        except:
            self.hero.bot.send_message(self.hero.id, 'Отправьте НОМЕР клетки')
            self.hero.bot.register_next_step_handler(message, lambda message: self.movement(message, is_effect))
            return
        if all(int(message.text) != cell for cell in self.hero.main_hero.board.move_options) and int(message.text) != self.current_cell:
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
                                                lambda message: self.hero.choose_discard_card_for_increasing(message, is_effect))
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
        self.bot.register_next_step_handler(message, lambda message: self.hero.choose_discard_card_for_increasing(message, is_effect))
        return

    def choose_discard_card(self, is_effect=False):
        for card in self.hand:
            card.show_card()
        self.bot.send_message(self.id, 'Выберите карту, которую хотите сбросить и отправьте ее номер')
        message = users_message[self.id]
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


img_hary = pygame.image.load('pictures/medusa/harpy.jpg')


class Harpy(Support):
    hp = 1
    img = img_hary
    move_value = 3
    str = 'harpy'
    type = 'melee'

    def resurect(self):
        self.hero.bot.send_message('Выберите ячейку в вашей зоне, в которую хотите поместить гарпию')
        zone = []
        for color in self.hero.main_hero.board.cells_color[self.hero.current_cell]:
            zone = self.hero.main_hero.board.color_directions[color]
        message = users_message[self.hero.id]
        self.hero.bot.register_next_step_handler(message, lambda message: self.placing_self(message, zone))

    def placing_self(self, message, zone):
        hero = self.hero
        try:
            cells = [int(x) for x in message.text.split()]
        except:
            self.hero.bot.send_message(hero.id, 'Отправьте НОМЕРА клеток')
            self.hero.bot.register_next_step_handler(message, lambda message: self.placing_self(message, zone))
            return
        cells = [int(x) for x in message.text.split()]
        places = hero.main_hero.places
        if len(cells) == 1 and cells[0] in zone and all(cells[0] != places.values()[i] for i in range(len(places))):
            main_hero = hero.main_hero
            main_hero.places[self] = cells[0]
            hero.characters.append(self)
            self.current_cell = cells[0]
            main_hero.board.render()
            board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
            self.hero.bot.send_photo(hero.id, board_img)
            board_img.close()
            self.hero.effect_done = True
        elif cells[0] in zone and all(cells[0] != places.values()[i] for i in range(len(places))):
            self.hero.bot.send_message(hero.id, 'Вы должны ввести номре одной клетки, попробуйте заново')
            self.hero.bot.register_next_step_handler(message, lambda message: self.placing_self(message, zone))
        elif len(cells) == 1 and all(cells[0] != places.values()[i] for i in range(len(places))):
            self.hero.bot.send_message(hero.id, 'Нужно выбрать клетку в зоне вашего героя, попробуйте заново')
            self.hero.bot.register_next_step_handler(message, lambda message: self.placing_self(message, zone))
        elif len(cells) == 1 and cells[0] in zone:
            self.hero.bot.send_message(hero.id, 'Нельзя ставить помощника на одну клетку с дргуим персонажем, попробуйте заново')
            self.hero.bot.register_next_step_handler(message, lambda message: self.placing_self(message, zone))
        else:
            self.hero.bot.send_message(hero.id, 'Вы совершили несколько ошибок в расстановки персонажей, прочтите правила /rules')
            self.hero.bot.register_next_step_handler(message, lambda message: self.placing_self(message, zone))


hp_img_medusa = [f'pictures/medusa/hp/{i}.png'.format(i) for i in range(17)]
img_medusa = pygame.image.load('pictures/medusa/medusa.jpg')


class Medusa(Hero):
    effect_done = False
    id = None
    enemy = None
    enemy_id = None
    your_turn = None
    board = None
    places = None
    hp_img = hp_img_medusa

    img = img_medusa
    current_cell = None
    move_value = 3
    str = 'medusa'
    hp = 16
    type = 'distance'

    def __init__(self, deck, bot):
        self.bot = bot
        self.hero = self
        self.deck = deck
        self.hero_in_battle = None
        self.hand = []
        self.actions = 0
        self.played_card = None
        self.harpy1 = Harpy(self)
        self.harpy2 = Harpy(self)
        self.harpy3 = Harpy(self)
        self.characters = [self, self.harpy1, self.harpy2, self.harpy3]

    def effect(self):
        board = self.main_hero.board
        places = self.main_hero.places
        zone = []
        for color in board.cells_color[self.current_cell]:
            zone += board.color_directions[color]
        print(zone)
        variants = {}
        for character in places:
            if character not in self.characters and places[character] in zone:
                variants[character.str] = character
        if len(variants) == 0:
            self.bot.send_message(self.id, 'В вашей зоне нет противников, поэтому вы никому не наносите урон\n(эффект медузы)')
            self.hero.effect_done = True
            return
        if len(variants) == 1:
            character = list(variants.keys())[0]
            variants[character].deal_damage(1)
            self.bot.send_message(self.id, f'Вы нанесли 1 урона персонажу {character} в вашей зоне\n(эффект меддузы)')
            self.bot.send_message(self.enemy.id, f'Ваш {character} получил 1 урона, так как находился в зоне медузы\n'
                                                 f'(эффект меддузы)')
            self.hero.effect_done = True
            return
        message = users_message[self.id]
        self.bot.send_message(self.id, f'Выберите персонажа которого будете атаковать\n{list(variants.keys())}')
        self.bot.register_next_step_handler(message, lambda message: self.choose_cell(message, variants))

    def choose_cell(self, message, variants):
        direct = message.text
        if direct not in variants:
            self.bot.send_message(self.id, 'Выберите персонажа ИЗ СПИСКА')
            self.bot.register_next_step_handler(message, lambda message: self.choose_cell(message, variants))
            return
        variants[direct].deal_damage(1)
        self.bot.send_message(self.id, f'Вы нанесли 1 урона персонажу {direct} в вашей зоне\n(эффект меддузы)')
        self.bot.send_message(self.enemy.id, f'Ваш {direct} получил 1 урона, так как находился в зоне медузы\n'
                                             f'(эффект меддузы)')
        self.hero.effect_done = True




hp_img_jackalope = [f'pictures/bigfoot/jackalope/hp/{i}.png'.format(i) for i in range(7)]
img_jackalope = pygame.image.load('pictures/bigfoot/jackalope/jackalope.jpg')


class Jackalope(Support):
    hp_img = hp_img_jackalope
    img = img_jackalope
    move_value = 3
    str = 'jackalope'
    hp = 6
    type = 'melee'


hp_img_bigfoot = [f'pictures/bigfoot/hp/{i}.png'.format(i) for i in range(17)]
img_bigfoot = pygame.image.load('pictures/bigfoot/bigfoot.jpg')


class Bigfoot(Hero):
    effect_done = False
    id = None
    enemy = None
    enemy_id = None
    your_turn = None
    board = None
    places = None
    hp_img = hp_img_bigfoot
    img = img_bigfoot
    current_cell = None
    move_value = 3
    str = 'bigfoot'
    hp = 16
    type = 'melee'

    def __init__(self, deck, bot):
        self.bot = bot
        self.hero = self
        self.deck = deck
        self.hero_in_battle = None
        self.hand = []
        self.actions = 0
        self.played_card = None
        self.jackalope = Jackalope(self)
        self.characters = [self, self.jackalope]

    def effect(self):
        board = self.main_hero.board
        places = self.main_hero.places
        zone = []
        for color in board.cells_color[self.current_cell]:
            zone += board.color_directions[color]
        for character in places:
            print(places[character], '\n', zone, '\n', character, '\n', self.jackalope)
            if places[character] in zone and character != self.jackalope and character != self:
                self.bot.send_message(self.id,
                                      'В вашей зоне есть персонажи противника, поэтому вы не берете карту\n(эффект бигфута)')
                self.hero.effect_done = True
                return
        self.bot.send_message(self.id, 'В вашей зоне нет персонажей противника, поэтому вы берете карту\n(эффект бигфута)')
        self.draw_card()
        self.bot.send_message(self.enemy.id, '(эффект бигфута)')
        self.hero.effect_done = True


from src.auxiliary_objects.hero_parrent import Hero, Support
from src.data_objects.data_base import DataBase
import pygame
from random import randint

data_base = DataBase()


class Harpy(Support):
    hp = 1
    img = pygame.image.load('pictures/medusa/harpy.jpg')
    move_value = 3
    str = 'harpy'
    type = 'melee'

    def resurect(self):
        self.hero.bot.send_message('Выберите ячейку в вашей зоне, в которую хотите поместить гарпию')
        zone = []
        for color in self.hero.main_hero.board.cells_color[self.hero.current_cell]:
            zone = self.hero.main_hero.board.color_directions[color]
        message = data_base.users_message[self.hero.id]
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


class Medusa(Hero):
    effect_done = False
    id = None
    enemy = None
    enemy_id = None
    your_turn = None
    board = None
    places = None
    hp_img = [f'pictures/medusa/hp/{i}.png'.format(i) for i in range(17)]
    card_img = [f'pictures/medusa/cards/{i}.png'.format(i) for i in range(1, 12)]
    img = pygame.image.load('pictures/medusa/medusa.jpg')
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
        message = data_base.users_message[self.id]
        character = list(variants.keys())[randint(0,1)]
        variants[character].deal_damage(1)
        self.bot.send_message(self.id, f'Вы нанесли 1 урона персонажу {character} в вашей зоне\n(эффект меддузы)')
        self.bot.send_message(self.enemy.id, f'Ваш {character} получил 1 урона, так как находился в зоне медузы\n'
                                             f'(эффект меддузы)')
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

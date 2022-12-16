from src.auxiliary_objects.hero_parrent import Hero, Support
from src.data_objects.data_base import DataBase
import pygame

data_base = DataBase()


class Jackalope(Support):
    hp_img = [f'pictures/bigfoot/jackalope/hp/{i}.png'.format(i) for i in range(7)]
    img = pygame.image.load('pictures/bigfoot/jackalope/jackalope.jpg')
    move_value = 3
    str = 'jackalope'
    hp = 6
    type = 'melee'


class Bigfoot(Hero):
    effect_done = False
    id = None
    enemy = None
    enemy_id = None
    your_turn = None
    board = None
    places = None
    card_img = [f'pictures/bigfoot/cards/{i}.png'.format(i) for i in range(1, 12)]
    hp_img = [f'pictures/bigfoot/hp/{i}.png'.format(i) for i in range(17)]
    img = pygame.image.load('pictures/bigfoot/bigfoot.jpg')
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


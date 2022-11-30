from random import randint
from data_base import users_message


medusa_imgs = [f'pictures/medusa/cards/{i}.png'.format(i) for i in range(1, 12)]


class Card():
    def __init__(self, hero, enemy, bot):
        self.enemy = enemy
        self.hero = hero
        self.bot = bot


class MedusaCard(Card):
    def show_card(self, hero=None):
        if hero is None:
            hero = self.hero
        img = open(medusa_imgs[self.img], 'rb')
        self.bot.send_photo(hero.id, img)
        img.close()


class MomentaryGlance(MedusaCard):
    img = 0
    who = 'medusa'
    increase_value = 4
    count_in_deck = 2
    type = 'scheme'

    def effect(self):
        places = self.hero.main_hero.places
        b = self.hero.main_hero.board
        variants = {}
        places_cells = {places[x]: x for x in places}
        for i in b.cells_color[self.hero.current_cell]:
            for x in b.color_directions[i]:
                if x in places_cells:
                    variants[x] = places_cells[x]
        if len(variants) == 0:
            self.bot.send_message(self.hero.id, 'Вы не можете никого атаковать')
            return
        self.bot.send_message(self.hero.id, 'Выберите клетку, которую хотите атаковать\n' +
                              f'\n{list(variants.keys())}'.format(variants.keys()))
        message = users_message[self.hero.id]
        self.bot.register_next_step_handler(message, lambda message: choose_cell_in_zone_to_attack(message, variants, self.bot))
        self.hero.effect_done = True


def choose_cell_in_zone_to_attack(message, variants, bot):
    try:
        int(message.text)
    except:
        bot.send_message(message.chat.id, 'Введите НОМЕР клетки')
        bot.register_next_step_handler(message,
                                       lambda message: choose_cell_in_zone_to_attack(message, variants, bot))
        return
    cell = int(message.text)
    if cell in variants:
        variants[cell].deal_damage(2)
        return
    bot.send_message(message.chat.id, 'Эта клетка недоступна, попробуйте еще раз')
    bot.register_next_step_handler(message, lambda message: choose_cell_in_zone_to_attack(message, variants, bot))


class ClutchingClaws(MedusaCard):
    img = 1
    who = 'harpy'
    increase_value = 2
    count_in_deck = 3
    type = 'versatile'
    effect_moment = 3
    value = 3

    def effect(self):
        self.bot.send_message(self.hero.enemy.id, 'Отправьте номер карты которой хотите сбросить')
        for card in self.hero.enemy.hand:
            card.show_card()
        message = users_message[self.hero.enemy.id]
        self.bot.register_next_step_handler(message,
                                            lambda message: self.hero.enemy.choose_discard_card_for_increasing(message,
                                                                                                        self, True))


class Dash(MedusaCard):
    img = 2
    who = 'all'
    increase_value = 1
    count_in_deck = 3
    type = 'versatile'
    effect_moment = 3
    value = 3

    def effect(self):
        if self.hero.hero_in_battle.hp > 0:
            self.hero.hero_in_battle.move(3, is_effect=True)


class Fient(MedusaCard):
    img = 3
    who = 'all'
    increase_value = 2
    count_in_deck = 3
    type = 'versatile'
    effect_moment = 1
    value = 2

    def effect(self):
        self.enemy.do_effect = False
        self.hero.effect_done = True


class GazeOfStone(MedusaCard):
    img = 4
    who = 'medusa'
    increase_value = 4
    count_in_deck = 3
    type = 'attack'
    effect_moment = 3
    value = 2

    def effect(self):
        if self.hero.win:
            self.enemy.deal_damage(8)
        self.hero.effect_done = True


class HissAndSlither(MedusaCard):
    img = 5
    who = 'medusa'
    increase_value = 3
    count_in_deck = 3
    type = 'defence'
    effect_moment = 3
    value = 4

    def effect(self):
        self.bot.send_message(self.hero.enemy.id, 'Отправьте номер карты которой хотите сбросить')
        for card in self.hero.enemy.hand:
            card.show_card()
        message = users_message[self.hero.enemy.id]
        self.bot.register_next_step_handler(message, lambda message: self.hero.enemy.choose_discard_card_for_increasing(
                                                                                                   message, self, True))


class Regroup(MedusaCard):
    img = 6
    who = 'all'
    increase_value = 2
    count_in_deck = 3
    type = 'versatile'
    effect_moment = 3
    value = 1

    def effect(self):
        self.hero.draw_card()
        if self.hero.win:
            self.hero.draw_card()
        self.hero.effect_done = True


class SecondShot(MedusaCard):
    img = 7
    who = 'medusa'
    increase_value = 3
    count_in_deck = 3
    type = 'attack'
    effect_moment = 2
    value = 3

    def effect(self):
        self.bot.send_message(self.hero.id, 'Выберите карту, которую хотите сбросить и отправьте ее номер, 0 если никакую')
        for card in self.hero.hand:
            card.show_card()
        message = users_message[self.hero.id]
        self.bot.register_next_step_handler(message, lambda message: self.hero.choose_discard_card_for_increasing(message, self, True))


class Snipe(MedusaCard):
    img = 8
    who = 'all'
    increase_value = 1
    count_in_deck = 3
    type = 'versatile'
    effect_moment = 3
    value = 3

    def effect(self):
        self.hero.draw_card()
        self.hero.effect_done = True


class TheHoundsOfMightyZeus(MedusaCard):
    img = 9
    who = 'harpy'
    increase_value = 3
    count_in_deck = 2
    type = 'versatile'
    effect_moment = 3
    value = 4

    def effect(self):
        for character in self.hero.characters:
            if character != self.hero:
                character.move(3, is_effect=True)
                while not self.hero.effect_done:
                    ...
                self.hero.effect_done = False
        self.hero.effect_done = True


class WingedFrenzy(MedusaCard):
    who = 'all'
    img = 10
    increase_value = 2
    count_in_deck = 2
    type = 'scheme'

    def effect(self):
        for character in self.hero.characters:
            character.move(3, is_effect=True)
            while not self.hero.effect_done:
                print('scheme effect')
            self.hero.effect_done = False
        if self.hero.harpy1.hp == 0:
            self.hero.harpy1.resurect()
        elif self.hero.harpy2.hp == 0:
            self.hero.harpy2.resurect()
        elif self.hero.harpy2.hp == 0:
            self.hero.harpy2.resurect()
        else:
            self.hero.effect_done = True

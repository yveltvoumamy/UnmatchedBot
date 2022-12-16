from random import randint
from src.data_objects.data_base import DataBase
from src.auxiliary_objects.card_parent import *

data_base = DataBase()


class MedusaCard(Card):
    def show_card(self, hero=None):
        if hero is None:
            hero = self.hero
        img = open(self.hero.card_img[self.img], 'rb')
        self.bot.send_photo(hero.id, img)
        img.close()


@card_properties(0, 'medusa', 4, 2, 'scheme')
class MomentaryGlance(MedusaCard):
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
        message = data_base.users_message[self.hero.id]
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


@card_properties(1, 'harpy', 2, 3, 'versatile', effect=3, value=3)
class ClutchingClaws(MedusaCard):
    def effect(self):
        self.bot.send_message(self.hero.enemy.id, 'Отправьте номер карты которой хотите сбросить')
        for card in self.hero.enemy.hand:
            card.show_card()
        message = data_base.users_message[self.hero.enemy.id]
        self.bot.register_next_step_handler(message,
                                            lambda message: self.hero.enemy.choose_discard_card_for_increasing(message,
                                                                                                        self, True))


@card_properties(2, 'all', 1, 3, 'versatile', effect=3, value=3)
class Dash(MedusaCard):
    def effect(self):
        if self.hero.hero_in_battle.hp > 0:
            self.hero.hero_in_battle.move(3, is_effect=True)


@card_properties(3, 'all', 2, 3, 'versatile', effect=1, value=2)
class Fient(MedusaCard):
    def effect(self):
        self.enemy.do_effect = False
        self.hero.effect_done = True


@card_properties(4, 'medusa', 4, 3, 'attack', effect=3, value=2)
class GazeOfStone(MedusaCard):
    def effect(self):
        if self.hero.win:
            self.enemy.deal_damage(8)
        self.hero.effect_done = True


@card_properties(5, 'medusa', 3, 3, 'defence', effect=3, value=4)
class HissAndSlither(MedusaCard):
    def effect(self):
        self.bot.send_message(self.hero.enemy.id, 'Отправьте номер карты которой хотите сбросить')
        for card in self.hero.enemy.hand:
            card.show_card()
        message = data_base.users_message[self.hero.enemy.id]
        self.bot.register_next_step_handler(message, lambda message: self.hero.enemy.choose_discard_card_for_increasing(
                                                                                                   message, self, True))


@card_properties(6, 'all', 2, 3, 'versatile', effect=3, value=1)
class Regroup(MedusaCard):
    def effect(self):
        self.hero.draw_card()
        if self.hero.win:
            self.hero.draw_card()
        self.hero.effect_done = True


@card_properties(7, 'medusa', 3, 3, 'attack', effect=2, value=3)
class SecondShot(MedusaCard):
    def effect(self):
        self.bot.send_message(self.hero.id, 'Выберите карту, которую хотите сбросить и отправьте ее номер, 0 если никакую')
        for card in self.hero.hand:
            card.show_card()
        message = data_base.users_message[self.hero.id]
        self.bot.register_next_step_handler(message, lambda message: self.hero.choose_discard_card_for_increasing(message, self, True))


@card_properties(8, 'all', 1, 3, 'versatile', effect=3, value=3)
class Snipe(MedusaCard):
    def effect(self):
        self.hero.draw_card()
        self.hero.effect_done = True


@card_properties(9, 'harpy', 3, 2, 'versatile', effect=3, value=4)
class TheHoundsOfMightyZeus(MedusaCard):
    def effect(self):
        for character in self.hero.characters:
            if character != self.hero:
                character.move(3, is_effect=True)
                while not self.hero.effect_done:
                    ...
                self.hero.effect_done = False
        self.hero.effect_done = True


@card_properties(10, 'all', 2, 2, 'scheme')
class WingedFrenzy(MedusaCard):
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

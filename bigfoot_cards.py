from medusa_cards import Card
from data_base import users_message

bigfoot_imgs = [f'pictures/bigfoot/cards/{i}.png'.format(i) for i in range(1, 12)]


class BigfootCard(Card):
    def show_card(self, hero=None):
        if hero is None:
            hero = self.hero
        img = open(bigfoot_imgs[self.img], 'rb')
        self.bot.send_photo(hero.id, img)
        img.close()


class CrashThroughTheTrees(BigfootCard):
    img = 0
    who = 'bigfoot'
    increase_value = 3
    count_in_deck = 2
    type = 'scheme'

    def effect(self):
        self.hero.move(5, True, is_effect=True)


class Disengage(BigfootCard):
    img = 1
    who = 'all'
    increase_value = 2
    count_in_deck = 2
    type = 'attack'
    effect_moment = 3
    value = 4

    def effect(self):
        b = self.hero.main_hero.board
        places = self.hero.main_hero.places
        variants = []
        for i in b.cells_color[self.hero.hero_in_battle.current_cell]:
            for x in b.color_directions[i]:
                if x not in places.values():
                    variants.append(x)
        message = users_message[self.hero.id]
        self.bot.send_message(self.hero.id, 'На каую клетку хотите переместиться ?\n' + str(variants) +
                              '\nОтправьте 0, если не хотите перемещаться')
        self.bot.register_next_step_handler(message, lambda message: choose_cell_in_zone_to_move(
            message, self.hero, variants, self.bot))


def choose_cell_in_zone_to_move(message, hero, variants, bot):
    if message.text == '0':
        return
    try:
        int(message.text)
    except:
        bot.send_message(message.chat.id, 'Отправьте НОМЕР клетки')
        bot.register_next_step_handler(message, lambda message: choose_cell_in_zone_to_move(message, hero, variants, bot))
        return
    cell = int(message.text)
    if cell in variants:
        hero.main_hero.places[hero] = cell
        hero.current_cell = cell
        hero.hero.effect_done = True
        return
    bot.send_message(message.chat.id, 'Эта клетка недоступна, попробуйте еще раз')
    bot.register_next_step_handler(message, lambda message: choose_cell_in_zone_to_move(message, hero, variants, bot))


class FientBigfoot(BigfootCard):
    img = 2
    who = 'all'
    increase_value = 2
    count_in_deck = 3
    type = 'versatile'
    effect_moment = 1
    value = 2

    def effect(self):
        self.enemy.do_effect = False
        self.hero.effect_done = True


class Hoax(BigfootCard):
    img = 3
    who = 'all'
    increase_value = 2
    count_in_deck = 3
    type = 'versatile'
    effect_moment = 3
    value = 4

    def effect(self):
        self.hero.hero_in_battle.move(5, throug=True, is_effect=True)


class ItsJustYourImagination(BigfootCard):
    img = 4
    who = 'all'
    increase_value = 3
    count_in_deck = 2
    type = 'defence'
    effect_moment = 1
    value = 3

    def effect(self):
        self.enemy.do_effect = False
        self.hero.effect_done = True


class JackalopeHorns(BigfootCard):
    img = 5
    who = 'lackalope'
    increase_value = 2
    count_in_deck = 3
    type = 'scheme'

    def effect(self):
        if self.hero.jackalope.hp == 0:
            self.bot.send_message(self.hero.id, 'Ваш jackalope мертв, вы не можете использовать эту карту, поэтому она просто сбрасывается')
            return
        variants = []
        places = self.hero.main_hero.places
        b = self.hero.main_hero.board
        self.hero.jackalope.move(5, True, is_effect=True)
        while not self.hero.effect_done:
            ...
        self.hero.effect_done = False
        for x in b.cells_ways[self.hero.jackalope.current_cell]:
            if x in places.values():
                variants.append(x)
        if len(variants) == 0:
            self.bot.send_message(self.hero.id, 'Атаковать некого')
            self.hero.effect_done = True
            return
        if len(variants) == 1:
            reversed_places = {places[x]: x for x in places}
            reversed_places[variants[0]].deal_damage(2)
            self.hero.effect_done = True
            return
        message = users_message[self.hero.id]
        self.bot.send_message(self.hero.id, 'Выберите клетку, которую хотите атаковать\n' + str(variants))
        self.bot.register_next_step_handler(message, lambda message: self.choose_adjacent_enemy(message, variants))

    def choose_adjacent_enemy(self, message, variants):
        places = self.hero.main_hero.places
        reversed_places = {places[x]: x for x in places}
        try:
            int(message.text)
        except:
            self.bot.send_message(self.hero.id, 'Отправьте НОМЕР клетки')
            self.bot.register_next_step_handler(message, lambda message: self.choose_adjacent_enemy(message, variants))
            return
        cell = int(message.text)
        if cell in variants:
            reversed_places[cell].deal_damage(2)
            self.hero.effect_done = True
            self.bot.send_message(self.hero.id, f'Пресонаж противника {reversed_places[cell].str} получил 2 урона')
            return
        self.bot.send_message(self.hero.id, 'Нельзя нанести урон по этой клетке')
        self.bot.register_next_step_handler(message, lambda message: self.choose_adjacent_enemy(message, variants))


class LargerThenLife(BigfootCard):
    img = 6
    who = 'bigfoot'
    increase_value = 3
    count_in_deck = 3
    type = 'attack'
    effect_moment = 3
    value = 6

    def effect(self):
        self.hero.effect_done = True


class MomentousShift(BigfootCard):
    img = 7
    who = 'all'
    increase_value = 1
    count_in_deck = 3
    type = 'versatile'
    effect_moment = 2
    value = 3

    def effect(self):
        if self.hero.hero_in_battle.last_cell != self.hero.hero_in_battle.current_cell:
            self.value = 5
        self.hero.effect_done = True


class RegroupBigfoot(BigfootCard):
    img = 8
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


class Savagery(BigfootCard):
    img = 9
    who = 'bigfoot'
    increase_value = 3
    count_in_deck = 3
    type = 'attack'
    effect_moment = 3
    value = 4

    def effect(self):
        places = self.hero.main_hero.places
        b = self.hero.main_hero.board
        reversed_places = {places[x]: x for x in places}
        if self.hero.win:
            for x in b.cells_ways[self.hero.current_cell]:
                if x in places.values():
                    if reversed_places[x] not in self.hero.characters:
                        reversed_places[x].deal_damage(1)
        self.hero.effect_done = True


class Skrimish(BigfootCard):
    img = 10
    who = 'all'
    increase_value = 1
    count_in_deck = 3
    type = 'versatile'
    effect_moment = 3
    value = 4

    def effect(self):
        if self.hero.win:
            self.bot.send_message(self.hero.id, 'Кого вы хотите переместить ? (себя/противника)')
            message = users_message[self.hero.id]
            self.bot.register_next_step_handler(message, lambda message: self.move_self_or_enemy(message))

    def move_self_or_enemy(self, message):
        if message == users_message[self.hero.id]:
            self.bot.register_next_step_handler(message, lambda message: self.move_self_or_enemy(message))
            return
        if message.text == 'себя':
            self.bot.send_message(self.hero.id, f'Переместите {self.hero.hero_in_battle.str} на 2 ячейки'.format(
                self.hero.hero_in_battle.str))
            self.hero.hero_in_battle.move(2, hero=self.hero.hero_in_battle)
            return
        if message.text == 'противника':
            self.bot.send_message(self.hero.id, f'Переместите {self.hero.hero_in_battle.str} на 2 ячейки'.format(
                self.hero.hero_in_battle.str))
            self.hero.enemy.hero_in_battle.move(2, hero=self.hero.enemy.hero_in_battle)
            return

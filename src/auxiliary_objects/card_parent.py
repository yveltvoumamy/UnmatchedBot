class Card():
    def __init__(self):
        self.enemy, self.hero, self.bot = None, None, None

    def add_attr(self, hero, enemy, bot):
        self.enemy = enemy
        self.hero = hero
        self.bot = bot
        return self


def card_properties(*args, **kwargs):
    def wrapper(cls):
        class NewCls:
            def __init__(self, cls):
                self.obj = cls()
                print(args)
                self.obj.img, self.obj.who, self.obj.increase_value, self.obj.count_in_deck, self.obj.type = args
                try:
                    self.obj.effect_moment, self.obj.value = kwargs.values()
                except:
                    ...
        return NewCls(cls).obj

    return wrapper


class DeckComposite():
    def __init__(self):
        self.deck = []

    def add(self, obj):
        if isinstance(obj, Card) and not obj in self.deck:
            self.deck.append(obj)

    def remove(self, obj):
        index = self.deck.index(obj)
        del self.deck[index]

    def get_child(self, index):
        return self.deck[index]

    def set_deck(self, deck):
        self.deck = deck

    def get_list(self):
        return self.deck
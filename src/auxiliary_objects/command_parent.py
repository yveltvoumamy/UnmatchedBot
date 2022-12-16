
class Commands():
    heroes, users_message, users_id = None, None, None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Commands, cls).__new__(cls)
        return cls.instance

    def update(self, heroes, users_message, users_id):
        self.heroes = heroes
        self.users_message = users_message
        self.users_id = users_id


class CommandComposite():
    def __init__(self):
        self._children = []

    def add(self, obj):
        if isinstance(obj, Commands) and not obj in self._children:
            self._children.append(obj)

    def remove(self, obj):
        index = self._children.index(obj)
        del self._children[index]

    def get_child(self, index):
        return self._children[index]

    def get_list(self):
        return self._children
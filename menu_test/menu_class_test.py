class Menu:
    # Wehn a menu is clicked, it shows its children
    def __init__(self, name, menu_type, parent=None):
        self.name = name
        self.menu_type = menu_type
        self.is_selected = False
        self.is_focus = False
        self.children = []

    def __repr__(self):
        return '{} {} Selected:{}'.format(self.name, self.menu_type, self.is_selected)
    def __str__(self):
        return self.name

    def add_child(self, c):
        self.children.append(c)


class Item:
    # When an item is clicked, it runs its function
    def __init__(self, item_type, name=None, func=None, song=None):
        self.item_type = item_type

        self.is_selected = False

        if self.item_type == 'SONG':
            self.song = song
            self.name = self.song.name

        else:
            self.name = name
            self.func = self.func


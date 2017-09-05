#!/bin/python

from mpi3.view.menu_items import ViewItem

class Stack(object):
    def __init__(self):
        self.stack = []

    def add(self, menu):
        self.stack.append(menu)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def __nonzero__(self):
        return len(self.stack) > 0

    def __len__(self):
        return len(self.stack)


class Menu(ViewItem):
    def __init__(self):
        super(Menu, self).__init__()
        # page
        # filter
        # is_home
        pass

    def render(self):
        pass


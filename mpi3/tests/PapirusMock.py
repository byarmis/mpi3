#!/bin/python


class PapirusMock:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def clear(self):
        print('CLEARING SCREEN')

    def display(self, other):
        print('DISPLAYING {other}'.format(other=other))

    def partial_update(self):
        print('PARTIALLY UPDATING DISPLAY')

    def update(self):
        print('FULLY UPDATING DISPLAY')

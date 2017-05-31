#!/bin/python3


class PapirusMock:
    def __init__(self, **kwargs):
        for k, v in kwargs:
            setattr(self, k, v)

    def clear(self):
        print('CLEARING SCREEN')

    def display(self, other):
        print(f'DISPLAYING {other}')

    def partial_update(self):
        print('PARTIALLY UPDATING DISPLAY')

    def update(self):
        print('FULLY UPDATING DISPLAY')

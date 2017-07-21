#!/bin/python
import unittest
from main import Player


class TestBasicControls(unittest.TestCase):
    def test_initialize(self):
        p = Player()

    def test_cursor(self):
        p = Player()
        for _ in range(40):
            p.move_cursor(1)
            p.screen.render()

        for _ in range(80):
            p.move_cursor(-1)
            p.screen.render()

    def test_vol_change(self):
        p = Player()

        for _ in range(25):
            p.vol.increase
            p.screen.render()

        for _ in range(30):
            p.vol.decrease
            p.screen.render()

    def test_state_cycle(self):
        p = Player()

        for _ in range(25):
            p.state.next()
            p.screen.render()

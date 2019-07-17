#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from mpi3.view.types import HowUpdate


class TestHowUpdate(unittest.TestCase):
    def test_raises_exception(self):
        with self.assertRaises(ValueError):
            _ = HowUpdate()

        with self.assertRaises(ValueError):
            _ = HowUpdate(partial=True, complete=True)

        with self.assertRaises(ValueError):
            _ = HowUpdate(partial=False, complete=False)

        _ = HowUpdate(partial=False, complete=True)
        _ = HowUpdate(partial=True, complete=False)

    def test_partial(self):
        hu = HowUpdate(partial=True)
        self.assertTrue(hu.partial)
        self.assertFalse(hu.complete)

        hu = HowUpdate(complete=False)
        self.assertTrue(hu.partial)
        self.assertFalse(hu.complete)

    def test_complete(self):
        hu = HowUpdate(complete=True)
        self.assertFalse(hu.partial)
        self.assertTrue(hu.complete)

        hu = HowUpdate(partial=False)
        self.assertFalse(hu.partial)
        self.assertTrue(hu.complete)

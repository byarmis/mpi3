#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from mpi3.model.types import Statement

SIMPLE_SQL = '''
SELECT *
FROM {table}
;'''

SQL = '''
SELECT *
FROM {table}
WHERE {where_clause}
;'''

TABLE = 'asdf'
WHERE = '1 = 1'


class TestStatement(unittest.TestCase):
    def test_init(self):
        s = Statement(SQL)

    def test_raises_exception(self):
        s = Statement(SQL)
        with self.assertRaises(KeyError):
            _ = str(s)

    def test_inheritance(self):
        s = Statement(SQL)
        self.assertTrue(isinstance(s, str))

    def test_set_attribute(self):
        s = Statement(SIMPLE_SQL)
        s.table = TABLE
        self.assertTrue(hasattr(s, 'table'))
        ret = str(s)
        self.assertEqual(ret, SIMPLE_SQL.format(table=TABLE))
        self.assertIn('table', repr(s))

    def test_prepopulate_attributes(self):
        s = Statement(SQL, table=TABLE)
        self.assertTrue(hasattr(s, 'table'))

    def test_prepopulate_attributes_raises_exception(self):
        s = Statement(SQL, table=TABLE)
        with self.assertRaises(KeyError):
            _ = str(s)

    def test_prepopulate_attributes_set_attributes(self):
        s = Statement(SQL, table=TABLE)
        s.where_clause = WHERE
        ret = str(s)
        self.assertEqual(ret, SQL.format(table=TABLE, where_clause=WHERE))
        self.assertIn('table', repr(s))
        self.assertIn('where_clause', repr(s))
        self.assertIn(TABLE, repr(s))
        self.assertIn(WHERE, repr(s))

        s = Statement(SQL, table=TABLE, where_clause=WHERE)
        ret = str(s)
        self.assertEqual(ret, SQL.format(table=TABLE, where_clause=WHERE))
        self.assertIn('table', repr(s))
        self.assertIn('where_clause', repr(s))
        self.assertIn(TABLE, repr(s))
        self.assertIn(WHERE, repr(s))

    def test_docstring(self):
        s = Statement('SELECT * FROM {table}')
        with self.assertRaises(KeyError):
            _ = str(s)

        s.table = TABLE
        self.assertEqual(str(s), 'SELECT * FROM {table}'.format(table=TABLE))

        s = Statement('SELECT * FROM {table} WHERE {where_clause}', table=TABLE)
        with self.assertRaises(KeyError):
            _ = str(s)

        s.where_clause = WHERE
        self.assertEqual(str(s), 'SELECT * FROM {table} WHERE {where}'.format(table=TABLE, where=WHERE))

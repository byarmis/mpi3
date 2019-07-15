#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import Dict, Set


class Statement(str):
    """
    A Statement is a string that can be built up progressively and interacted with like an object.

    >>> s = Statement('SELECT * FROM {table}')
    >>> str(s)
    ValueError

    >>> s.table = 'library'
    >>> str(s)
    'SELECT * FROM library'

    A Statement also accept a dictionary in the constructor to pre-populate attributes
    >>> s = Statement('SELECT * FROM {table} WHERE {where_clause}', {'table':'library'})
    >>> str(s)
    ValueError

    >>> s.where_clause = '1 = 1'
    >>> str(s)
    'SELECT * FROM library WHERE 1 = 1'
    """

    def __new__(cls, a, *args, **kw):
        return str.__new__(cls, a)

    regex = r'.*{(.*)}.*'

    def __init__(self, sql_statement: str, requirements: Dict[str, str] = None) -> None:
        super().__init__()
        self.sql = sql_statement
        self.required = self._process_required(self.sql)

        self._expected = {'sql', 'required'}

        if requirements is not None:
            for requirement, value in requirements.items():
                setattr(self, requirement, value)

    def __str__(self) -> str:
        missing_requirements = self.required - set(self.__dict__.keys())
        if missing_requirements:
            raise ValueError(f'Required statement(s) not defined: {",".join(missing_requirements)}')

        return self.sql.format(**self.__dict__)

    def __repr__(self) -> str:
        kwargs = {k: v for k, v in self.__dict__.items() if not k.startswith('_') and k not in self._expected}
        return f'Statement({self.sql}, {kwargs})'

    def _process_required(self, sql: str) -> Set[str]:
        match = re.findall(self.regex, sql, flags=re.MULTILINE)

        if match is None:
            return set()
        else:
            return set(match)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class HowUpdate:
    def __init__(self, partial: bool = None, complete: bool = None):
        if partial == complete:
            raise ValueError('Partial or complete must be set and different from each other')

        self._partial = partial
        self._complete = complete

    @property
    def partial(self) -> bool:
        if self._partial is not None:
            return self._partial
        return not self._complete

    @property
    def complete(self) -> bool:
        if self._complete is not None:
            return self._complete
        return not self._partial

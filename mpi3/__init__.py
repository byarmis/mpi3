#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import partial


# Y'all ready for a weird, hacky workaround?
# http://tomerfiliba.com/blog/Infix-Operators/

class Infix(object):
    def __init__(self, func):
        self.func = func

    def __or__(self, other):
        return self.func(other)

    def __ror__(self, other):
        return Infix(partial(self.func, other))

    def __call__(self, v1, v2):
        return self.func(v1, v2)


@Infix
def xor(x, y):
    # 'a' |xor| '' => True
    # 'a' |xor| 'b' => False
    return bool(x) ^ bool(y)

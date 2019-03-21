# -*- coding:utf-8 -*-


import six
from .basket import *

__all__ = ['load_basket', 'save_basket']


def load_basket(fname, flood=True, keys=None, excluded_keys=None, dest=None, attr=False, basket_class=Basket):
    basket = basket_class.load(fname)
    if flood:
        basket.flood(keys=keys, excluded_keys=excluded_keys, dest=dest, attr=attr)
    return basket


def save_basket(fname, keys=None, excluded_keys=None, source=None, attr=False, basket_class=Basket):
    basket = basket_class.collect(keys=keys, excluded_keys=excluded_keys, source=source, attr=attr)
    basket.save(fname)
    return basket

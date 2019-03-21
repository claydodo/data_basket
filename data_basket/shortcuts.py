# -*- coding:utf-8 -*-


import six
from .basket import *


def load_basket(fname, basket_class=Basket, flood=True, target=None, keys=None, excluded_keys=None, attr=False):
    basket = basket_class.load(fname)
    if flood:
        basket.flood(target=target, keys=keys, excluded_keys=excluded_keys, attr=attr)
    return basket


def save_basket(fname, varnames, basket_class=Basket, source=None):
    basket = basket_class.collect(varnames=varnames, source=source)
    basket.save(fname)

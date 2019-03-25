# -*- coding:utf-8 -*-

import six
import os
import sys
import json
from datetime import datetime
import warnings
from krux.random.uuid import gen_uuid16
from krux.lodash import pick
from krux.functools.cache import cache
from krust.file_utils import *
from krust.zip_utils import *
from .serializers import *
from .exceptions import *


GLOBAL_SCOPE = sys.modules['__main__'].__dict__

__all__ = ['Basket', 'TextBasket']


class Basket(object):
    variant = 'Default'
    serializers = BUILTIN_SERIALIZERS + NUMPY_SERIALIZERS + PANDAS_SERIALIZERS

    def __init__(self, data=None, copy=True):
        if data is None:
            self.d = {}
        elif isinstance(data, Basket):
            if copy:
                self.d = data.d.copy()
            else:
                self.d = data.d
        else:
            if copy:
                self.d = data.copy()
            else:
                self.d = data

        self.tmp_dir = self._gen_tmp_path()

    @property
    @cache
    def _type_dict(self):
        return self.__class__._get_type_dict()

    def save(self, fname, keys=None, excluded_keys=None):
        fname = P(fname)
        selection = pick(self.d, keys) if keys else self.d.copy()
        if excluded_keys:
            for k in excluded_keys:
                selection.pop(k, None)

        meta_data = {}
        try:
            MKDIR(self.tmp_dir)
            for k, v in six.iteritems(selection):
                dest_without_ext = os.path.join(self.tmp_dir, k)
                for serializer in self.serializers:
                    s = serializer(v)
                    if s.check_type():
                        item = {
                            "type": s.type_name,
                            "inline": s.inline,
                        }
                        if s.inline:
                            item['value'] = s.dump(basket=self)
                        else:
                            s.dump(dest_without_ext + s.first_ext, basket=self)
                            item['value'] = k + s.first_ext
                        meta_data[k] = item
                        break

            meta_fname = os.path.join(self.tmp_dir, '__meta__.json')
            with open(meta_fname, 'w') as metaf:
                json.dump({
                    "variant": self.variant,
                    "data": meta_data,
                }, metaf, ensure_ascii=False, indent=2)

            zip(self.tmp_dir, fname)
        finally:
            RM(self.tmp_dir)

    @classmethod
    def load(cls, fname):
        fname = P(fname)
        basket = cls()
        try:
            unzip(fname, basket.tmp_dir)
            data = {}
            contents = LS(basket.tmp_dir)
            if '__meta__.json' not in contents:
                # guess mode
                for fn in contents:
                    src = os.path.join(basket.tmp_dir, fn)
                    vn = strip_ext(fn)
                    ext = get_ext(fn)
                    for s in cls.serializers:
                        s_obj = s()
                        if (not s_obj.inline) and ext in s_obj.exts:
                            try:
                                data[vn] = s_obj.load(src)
                                break
                            except Exception as e:
                                pass
            else:
                with open(os.path.join(basket.tmp_dir, '__meta__.json')) as f:
                    meta = json.load(f)

                if 'variant' in meta and meta['variant'] != cls.variant:
                    warnings.warn(BasketVariantMismatch(u'Basket: {}, file: {}'.format(cls.variant, meta['variant'])))

                type_dict = cls._get_type_dict()
                for k, v in six.iteritems(meta.get('data', {})):
                    if 'type' in v and v['type'] in type_dict:
                        serializer = type_dict[v['type']]
                        if v.get('inline', False):
                            src = v['value']
                        else:
                            src = os.path.join(basket.tmp_dir, v['value'])

                        data[k] = serializer().load(src, basket=basket)

            basket.update(data)
            return basket
        finally:
            RM(basket.tmp_dir)

    @classmethod
    def collect(cls, keys=None, excluded_keys=None, source=None, attr=False):
        if source is None:
            source = GLOBAL_SCOPE

        if isinstance(source, dict):
            attr = False
            keys = set(source.keys()) if keys is None else set(keys)
        else:
            keys = set(keys) if keys else set()

        if excluded_keys:
            keys = keys - set(excluded_keys)

        data = {}
        for key in keys:
            try:
                if attr:
                    data[key] = getattr(source, key)
                else:
                    data[key] = source[key]
            except (AttributeError, KeyError) as e:
                pass

        return cls(data, copy=False)

    def flood(self, keys=None, excluded_keys=None, dest=None, attr=False):
        """Flood the contents into global scope or target object."""
        keys = set(self.keys()) if keys is None else set(keys)
        if excluded_keys:
            keys = keys - set(excluded_keys)

        if dest is None:
            dest = GLOBAL_SCOPE

        if isinstance(dest, dict):
            attr = False

        for key in keys:
            try:
                value = self[key]
                if attr:
                    setattr(dest, key, value)
                else:
                    dest[key] = value
            except KeyError as e:
                pass

    def _dump_obj(self, obj):
        """For compound types"""
        for s in self.serializers:
            try:
                if isinstance(obj, s.type_class):
                    s_obj = s(obj)
                    if s_obj.inline:
                        return {"type": s_obj.type_name, "inline": True, "value": s_obj.dump(basket=self)}
                    else:
                        dump_name = os.path.join('__anonymous__', gen_uuid16()+s_obj.first_ext)
                        dest = os.path.join(self.tmp_dir, dump_name)
                        MKDIR(DIRNAME(dest))
                        s_obj.dump(dest, basket=self)
                        return {"type": s_obj.type_name, "inline": False, "value": dump_name}
            except Exception as e:
                pass
        raise CannotDumpBasketData(obj)

    def _load_obj(self, d):
        """For compound types"""
        s = self._type_dict.get(d['type'])
        if s:
            src = d['value'] if s.inline else os.path.join(self.tmp_dir, d['value'])
            return s().load(src, basket=self)
        else:
            raise CannotLoadBasketData(d)

    @staticmethod
    def _gen_tmp_path():
        tmp_root = os.getenv('DATA_BASKET_TMP', '/tmp/data_basket')
        return os.path.join(tmp_root, '{}-{:%Y%m%d%H%M%S}'.format(gen_uuid16(), datetime.now()))

    @classmethod
    def _get_type_dict(cls):
        res = {}
        for s in cls.serializers:
            res.setdefault(s.type_name, s)  # prefer the first occurrence.
        return res

    ### dict-like interfaces ###

    def __getitem__(self, key):
        return self.d[key]

    def __setitem__(self, key, value):
        self.d[key] = value

    def get(self, key, default=None):
        return self.d.get(key, default)

    def setdefault(self, key, default):
        return self.d.setdefault(key, default)

    def update(self, d):
        self.d.update(d)

    def keys(self):
        return self.d.keys()

    def values(self):
        return self.d.values()

    def items(self):
        return self.d.items()

    def __contains__(self, item):
        return item in self.d

    def __repr__(self):
        return self.d.__repr__()


class TextBasket(Basket):
    variant = 'Text'
    serializers = BUILTIN_SERIALIZERS + NUMPY_TEXT_SERIALIZERS + PANDAS_TEXT_SERIALIZERS

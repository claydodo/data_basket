# -*- coding:utf-8 -*-

import six
import os
import json
from datetime import datetime
import warnings
from krux.random.uuid import gen_uuid16
from krux.lodash import pick
from krux.functools.cache import cache
from krust.file_utils import *
from krust.zip_utils import *
from .serializers import *


class Basket(object):
    variant = 'Default'
    serializers = BUILTIN_SERIALIZERS + NUMPY_SERIALIZERS + PANDAS_SERIALIZERS

    def __init__(self, **kwargs):
        self.d = {}

        for k, v in kwargs.items():
            self.d[k] = v

    def save(self, fname, keys=None, excluded_keys=None):
        selection = pick(self.d, keys) if keys else self.d.copy()
        if excluded_keys:
            for k in excluded_keys:
                selection.pop(k, None)

        meta_data = {}
        tmp_dir = self._gen_tmp_path()
        try:
            MKDIR(tmp_dir)
            # TODO
            for k, v in six.iteritems(selection):
                dest_without_ext = os.path.join(tmp_dir, k)
                for serializer in self.serializers:
                    s = serializer(v)
                    if s.check_type():
                        item = {
                            "type": s.type_name,
                            "inline": s.inline,
                        }
                        if s.inline:
                            item['value'] = s.dump()
                        else:
                            s.dump(dest_without_ext + s.ext)
                            item['value'] = k + s.ext
                        meta_data[k] = item
                        break

            meta_fname = os.path.join(tmp_dir, '__meta__.json')
            with open(meta_fname, 'w') as metaf:
                json.dump({
                    "variant": self.variant,
                    "data": meta_data,
                }, metaf, ensure_ascii=False, indent=2)

            zip(tmp_dir, fname)
        finally:
            RM(tmp_dir)

    @classmethod
    def load(cls, fname):
        tmp_dir = cls._gen_tmp_path()
        try:
            unzip(fname, tmp_dir)
            data = {}
            contents = LS(tmp_dir)
            if '__meta__.json' not in contents:
                # guess mode
                for fn in contents:
                    src = os.path.join(tmp_dir, fn)
                    vn = strip_ext(fn)
                    ext = get_ext(fn)
                    for s in cls.serializers:
                        if (not s.inline) and ext in s.exts:
                            try:
                                data[vn] = s().load(src)
                                break
                            except Exception as e:
                                pass
            else:
                with open(os.path.join(tmp_dir, '__meta__.json')) as f:
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
                            src = os.path.join(tmp_dir, v['value'])

                        data[k] = serializer().load(src)

            basket = cls(**data)
            return basket
        finally:
            RM(tmp_dir)

    @classmethod
    def collect(cls, varnames=None, source=None):
        pass

    def flood(self, target=None, keys=None, excluded_keys=None, attr=False):
        """Flood the contents into global scope or target object."""
        pass

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

    def keys(self):
        return self.d.keys()

    def values(self):
        return self.d.values()

    def items(self):
        return self.d.items()

    def iteritems(self):
        return six.iteritems(self.d)

    def __repr__(self):
        return self.d.__repr__()


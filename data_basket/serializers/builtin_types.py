import six
from .base import BasketSerializer
from data_basket.exceptions import *

__all__ = [
    'IntSerializer', 'FloatSerializer', 'ComplexSerializer',
    'StrSerializer',
    'NoneSerializer',
    'ListSerializer', 'TupleSerializer', 'DictSerializer',
    'BUILTIN_SERIALIZERS'
]


class IntSerializer(BasketSerializer):
    type_name = 'int'
    type_class = int
    inline = True

    def dump(self, dest=None, basket=None):
        return self.obj


class FloatSerializer(BasketSerializer):
    type_name = 'float'
    type_class = float
    inline = True

    def dump(self, dest=None, basket=None):
        return self.obj


class ComplexSerializer(BasketSerializer):
    type_name = 'complex'
    type_class = complex
    inline = True


class StrSerializer(BasketSerializer):
    type_name = 'str'
    type_class = six.string_types
    inline = True

    def dump(self, dest=None, basket=None):
        # TODO: PY2, PY3 compatible
        return self.obj

    def load(self, src, basket=None):
        # TODO: PY2, PY3 compatible
        self.obj = src
        return self.obj


class NoneSerializer(BasketSerializer):
    type_name = 'None'
    type_class = type(None)
    inline = True

    def check_type(self):
        return self.obj is None

    def dump(self, dest=None, basket=None):
        return self.obj

    def load(self, src, basket=None):
        return None


class ListSerializer(BasketSerializer):
    type_name = 'list'
    type_class = list
    inline = True

    def dump(self, dest=None, basket=None):
        if basket:
            res = [basket._dump_obj(item) for item in self.obj]
        else:
            res = [dump_builtin_obj(item) for item in self.obj]
        return res

    def load(self, src, basket=None):
        if basket:
            self.obj = [basket._load_obj(d) for d in src]
        else:
            self.obj = [load_builtin_obj(d) for d in src]
        return self.obj


class TupleSerializer(ListSerializer):
    type_name = 'tuple'
    type_class = tuple

    def load(self, src, basket=None):
        if basket:
            self.obj = tuple([basket._load_obj(d) for d in src])
        else:
            self.obj = tuple([load_builtin_obj(d) for d in src])
        return self.obj


class DictSerializer(BasketSerializer):
    type_name = 'dict'
    type_class = dict
    inline = True

    def dump(self, dest=None, basket=None):
        if basket:
            res = {k: basket._dump_obj(v) for (k, v) in six.iteritems(self.obj)}
        else:
            res = {k: dump_builtin_obj(v) for (k, v) in six.iteritems(self.obj)}
        return res

    def load(self, src, basket=None):
        if basket:
            self.obj = {k: basket._load_obj(v) for (k, v) in six.iteritems(src)}
        else:
            self.obj = {k: load_builtin_obj(v) for (k, v) in six.iteritems(src)}
        return self.obj


BUILTIN_SERIALIZERS = [IntSerializer, FloatSerializer, ComplexSerializer,
                       StrSerializer,
                       NoneSerializer,
                       ListSerializer, TupleSerializer, DictSerializer]

# offline version, to make compound type such as list/dict work without basket.
BUILTIN_SERIALIZER_DICT = {s.type_name: s for s in BUILTIN_SERIALIZERS}


def dump_builtin_obj(obj):
    type_name = type(obj).__name__
    s = BUILTIN_SERIALIZER_DICT.get(type_name)
    if s:
        return {"type": s.type_name, "inline": True, "value": s(obj).dump()}
    else:
        raise CannotDumpBasketData(obj)


def load_builtin_obj(d):
    s = BUILTIN_SERIALIZER_DICT.get(d['type'])
    if s:
        return s().load(d['value'])
    else:
        raise CannotLoadBasketData(d)

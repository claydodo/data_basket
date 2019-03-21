import six
from .base import BasketSerializer
from data_basket.exceptions import *


class IntSerializer(BasketSerializer):
    type_name = 'int'
    type_class = int
    inline = True

    def dump(self, dest=None):
        return self.obj


class FloatSerializer(BasketSerializer):
    type_name = 'float'
    type_class = float
    inline = True

    def dump(self, dest=None):
        return self.obj


class ComplexSerializer(BasketSerializer):
    type_name = 'complex'
    type_class = complex
    inline = True


class StrSerializer(BasketSerializer):
    type_name = 'str'
    type_class = six.string_types
    inline = True

    def dump(self, dest=None):
        # TODO: PY2, PY3 compatible
        return self.obj

    def load(self, src):
        # TODO: PY2, PY3 compatible
        self.obj = src
        return self.obj


class NoneSerializer(BasketSerializer):
    type_name = 'None'
    type_class = None
    inline = True

    def check_type(self):
        return self.obj is None

    def dump(self, dest=None):
        return self.obj

    def load(self, src):
        return None


class ListSerializer(BasketSerializer):
    type_name = 'list'
    type_class = list
    inline = True

    def dump(self, dest=None):
        res = [dump_builtin_obj(item) for item in self.obj]
        return res

    def load(self, src):
        self.obj = [load_builtin_obj(d) for d in src]
        return self.obj


class TupleSerializer(ListSerializer):
    type_name = 'tuple'
    type_class = tuple

    def load(self, src):
        self.obj = tuple([load_builtin_obj(d) for d in src])
        return self.obj


class DictSerializer(BasketSerializer):
    type_name = 'dict'
    type_class = dict

    def dump(self, dest=None):
        res = {k: dump_builtin_obj(v) for (k, v) in six.iteritems(self.obj)}
        return res

    def load(self, src):
        self.obj = {k: load_builtin_obj(v) for (k, v) in six.iteritems(src)}
        return self.obj


BUILTIN_SERIALIZERS = [IntSerializer, FloatSerializer, ComplexSerializer,
                       StrSerializer,
                       NoneSerializer,
                       ListSerializer, TupleSerializer, DictSerializer]
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

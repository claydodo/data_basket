__all__ = ['BasketSerializer']


class BasketSerializer(object):
    type_name = ''
    type_class = object
    inline = False
    ext = ''

    def __init__(self, obj=None):
        self.obj = obj

    @property
    def first_type_class(self):
        if isinstance(self.type_class, (list, tuple)):
            return self.type_class[0]
        else:
            return self.type_class

    @property
    def type_classes(self):
        if isinstance(self.type_class, (list, tuple)):
            return self.type_class
        else:
            return tuple(self.type_class)

    @property
    def first_ext(self):
        if isinstance(self.ext, (list, tuple)):
            return self.ext[0]
        else:
            return self.ext

    @property
    def exts(self):
        if isinstance(self.ext, (list, tuple)):
            return self.ext
        else:
            return tuple(self.ext)

    def check_type(self):
        return isinstance(self.obj, self.type_class)

    def load(self, src, basket=None):
        if self.inline:
            self.obj = self.first_type_class(src)
            return self.obj
        else:
            raise NotImplementedError

    def dump(self, dest=None, basket=None):
        if self.inline:
            return repr(self.obj)
        else:
            raise NotImplementedError


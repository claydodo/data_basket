import six
from .base import BasketSerializer

import numpy as np


class NumpyArraySerializer(BasketSerializer):
    type_name = 'numpy_array'
    type_class = np.ndarray
    ext = '.npy'

    def dump(self, dest=None):
        np.save(dest, self.obj)

    def load(self, src):
        return np.load(src)


NUMPY_SERIALIZERS = [NumpyArraySerializer]
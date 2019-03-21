import six
from .base import BasketSerializer

try:
    import numpy as np


    class NumpyArraySerializer(BasketSerializer):
        type_name = 'numpy_array'
        type_class = np.ndarray
        ext = '.npy'

        def dump(self, dest=None, basket=None):
            np.save(dest, self.obj)

        def load(self, src, basket=None):
            return np.load(src)


    NUMPY_SERIALIZERS = [NumpyArraySerializer]
except ImportError:
    NUMPY_SERIALIZERS = []

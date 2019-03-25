import six
from .base import BasketSerializer

try:
    import numpy as np

    __all__ = [
        'NumpyArraySerializer',
        'NUMPY_SERIALIZERS', 'NUMPY_TEXT_SERIALIZERS',
    ]

    class NumpyArraySerializer(BasketSerializer):
        type_name = 'numpy_array'
        type_class = np.ndarray
        ext = '.npy'

        def dump(self, dest=None, basket=None):
            np.save(dest, self.obj)

        def load(self, src, basket=None):
            return np.load(src)


    class NumpyArrayTextSerializer(BasketSerializer):
        type_name = 'text_numpy_array'
        type_class = np.ndarray
        ext = '.txt'

        # TODO: masked array handling.

        def dump(self, dest=None, basket=None):
            np.savetxt(dest, self.obj, fmt='%g')

        def load(self, src, basket=None):
            return np.loadtxt(src)


    NUMPY_SERIALIZERS = [NumpyArraySerializer, NumpyArrayTextSerializer]
    NUMPY_TEXT_SERIALIZERS = [NumpyArrayTextSerializer, NumpyArraySerializer]
except ImportError:
    __all__ = ['NUMPY_SERIALIZERS']

    NUMPY_SERIALIZERS = []
    NUMPY_TEXT_SERIALIZERS = []

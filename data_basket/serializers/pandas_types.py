import six
from .base import BasketSerializer

try:
    import pandas as pd

    __all__ = [
        'PandasDataFrameSerializer',
        'PANDAS_SERIALIZERS', 'PANDAS_TEXT_SERIALIZERS',
    ]

    class PandasDataFrameSerializer(BasketSerializer):
        type_name = 'pandas_data_frame'
        type_class = pd.DataFrame
        ext = '.h5'

    # Not Ready
    # PANDAS_SERIALIZERS = [PandasDataFrameSerializer]
    PANDAS_SERIALIZERS = []
    PANDAS_TEXT_SERIALIZERS = []
except ImportError:
    __all__ = ['PANDAS_SERIALIZERS']

    PANDAS_SERIALIZERS = []
    PANDAS_TEXT_SERIALIZERS = []

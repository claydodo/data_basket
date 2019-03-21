import six
from .base import BasketSerializer

try:
    import pandas as pd


    class PandasDataFrameSerializer(BasketSerializer):
        type_name = 'pandas_data_frame'
        type_class = pd.DataFrame
        ext = '.h5'

    # Not Ready
    # PANDAS_SERIALIZERS = [PandasDataFrameSerializer]
    PANDAS_SERIALIZERS = []
except ImportError:
    PANDAS_SERIALIZERS = []

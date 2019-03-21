import six
from .base import BasketSerializer

import pandas as pd


class PandasDataFrameSerializer(BasketSerializer):
    type_name = 'pandas_data_frame'
    type_class = pd.DataFrame
    ext = '.h5'



PANDAS_SERIALIZERS = [PandasDataFrameSerializer]
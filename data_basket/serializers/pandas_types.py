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

        def load(self, src, basket=None):
            self.obj = pd.read_hdf(src)
            return self.obj

        def dump(self, dest=None, basket=None):
            self.obj.to_hdf(dest, 'data', mode='w', format='table')


    class PandasDataFrameCSVSerializer(PandasDataFrameSerializer):
        type_name = 'csv_pandas_data_frame'
        ext = ('.csv', '.tsv')

        def load(self, src, basket=None):
            self.obj = pd.read_csv(src, sep=self._get_sep(src), index_col=0)
            return self.obj

        def dump(self, dest=None, basket=None):
            self.obj.to_csv(dest, sep=self._get_sep(dest), float_format='%g', na_rep='NaN', header=True)

        def _get_sep(self, fname):
            return '\t' if fname.endswith('.tsv') else ','


    class PandasSeriesSerializer(PandasDataFrameSerializer):
        type_name = 'pandas_series'
        type_class = pd.Series


    class PandasSeriesCSVSerializer(PandasDataFrameCSVSerializer):
        type_name = 'csv_pandas_series'
        type_class = pd.Series

        def load(self, src, basket=None):
            self.obj = pd.read_csv(src, sep=self._get_sep(src), index_col=0, squeeze=True)
            return self.obj

    # TODO: other pandas types
    PANDAS_SERIALIZERS = [PandasDataFrameSerializer, PandasDataFrameCSVSerializer, PandasSeriesSerializer, PandasSeriesCSVSerializer]
    PANDAS_TEXT_SERIALIZERS = [PandasDataFrameCSVSerializer, PandasDataFrameSerializer, PandasSeriesCSVSerializer, PandasSeriesSerializer]
except ImportError:
    __all__ = ['PANDAS_SERIALIZERS']

    PANDAS_SERIALIZERS = []
    PANDAS_TEXT_SERIALIZERS = []

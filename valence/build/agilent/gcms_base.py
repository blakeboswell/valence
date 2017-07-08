""" Common build functionality for the Agilent .D files
    RESULTS.CSV, and DATA.MS
"""
import pandas as pd


class GcmsBuildBase(object):
    """ Base Agilent GCMS reader class

        Parameters
        ----------
            col_keys : dict
                File parsing specification.
            reader : function
                Function that extracts data from source file.
    """
    @classmethod
    def clean_name(item):
        """ return clean name from colstr item
        """
        return item[0]

    @classmethod
    def np_type(item):
        """ return np type from colstr item
        """
        return item[1]

    @classmethod
    def pd_columns(header, colstr):
        """ return clean column names for header
            specification in pd DataFrame
        """
        return [GcmsBuildBase.clean_name(colstr[col]) for col in header]

    @classmethod
    def column_structure(header, keys):
        """ determine table column structure from
            table header
        """
        for key, val in keys.items():
            if set(header) == set(val.keys()):
                return key, val
        raise Exception(
            'expected column structure: {}, found {}'.format(
                val.keys(), header)
        )

    def __init__(self, col_keys, reader, file_path):
        self.col_keys = col_keys
        self._meta, self._tables = reader(file_path)
        self._data = {}

    def _as_dataframe(self, header, data):
        """ transform list of rows as lists of tokens into
            pandas DataFrame with appropriate names and types
        """
        key, colstr = self.column_structure(header, self.col_keys)
        df = (pd.DataFrame(data, columns=self.pd_columns(header, colstr))
                .apply(pd.to_numeric, errors='ignore'))
        return (key, df)

    def _build_data(self):
        """ convert list of tables to dictionary of pandas dataframe
        """
        def build(tbl):
            return self._as_dataframe(tbl[0], tbl[1:])
        return {key: df for key, df in map(build, self._tables)}

    def _access(self, key):
        """ provide access to key in data with appropriate
            exception handling
        """
        if key not in self.source_data:
            # raise AttributeError(
            #     '{} has no attribute {}'.format(type(self).__name__, key)
            # )
            return None
        return self._data[key]

    def __getitem__(self, key):
        return self._access(key)

    @property
    def source_data(self):
        """ lazily load data from file
        """
        if not self._data:
            self._data = self._build_data()
        return self._data

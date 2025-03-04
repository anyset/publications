import pandas as pd
import json


class FileLoader:
    def __init__(self, file_path: str, file_format: str, column_mapping: dict | None = None, encoding: str = 'utf-8'):
        """

        :param file_path:  file path
        :param file_format: expected values are 'json' or 'csv'
        :param column_mapping: dict of columns to be renamed by value
        :param encoding: default is 'utf-8'
        """
        self.file_path = file_path
        self.file_format = file_format
        self.column_mapping = column_mapping
        self.encoding = encoding

    def load(self):
        if self.file_format == "csv":
            df = self.load_csv()
        elif self.file_format == "json":
            df = self.load_json()
        else:
            raise NotImplementedError(f"Unexpected format: '{self.file_format}'")
        if self.column_mapping:
            df = df.rename(columns=self.column_mapping)
        df = self.clean(df)
        return df

    def load_csv(self):
        return pd.read_csv(self.file_path, encoding=self.encoding)

    def load_json(self):
        with open(self.file_path) as file:
            d = json.load(file)
        return pd.DataFrame.from_dict(d)

    @staticmethod
    def clean(df: pd.DataFrame):
        """Replace NaN values by None"""
        df = df.where(df.notnull(), None)
        return df

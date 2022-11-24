import pandas as pd
from typing import Union, Iterable


def is_columns_exists(df: pd.DataFrame, column_names: Union[str, Iterable]):
    if isinstance(column_names, str):
        if column_names not in df.columns.values:
            raise KeyError(f'{column_names} not in column!')
    elif isinstance(column_names, Iterable):
        for column_name in column_names:
            if column_name not in df.columns.values:
                raise KeyError(f'{column_name} not in column!')
    else:
        raise TypeError(f'{column_names} is not in str or Iterable!')

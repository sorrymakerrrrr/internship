import pandas as pd
from typing import Union, Iterable
import os

__all__ = ['Preprocessing']


class Preprocessing:
    df = pd.DataFrame()
    src = None

    def __new__(cls, src: str, sheet_name, header, *args, **kwargs):
        if os.path.isfile(src):
            cls.df = pd.read_excel(src, sheet_name=sheet_name, header=header)
        cls.src = src
        cls.sheet_name = sheet_name
        return super().__new__(cls)

    @classmethod
    def is_columns_exists(cls, column_names: Union[str, Iterable]):
        if isinstance(column_names, str):
            if column_names not in cls.df.columns.values:
                raise KeyError(f'{column_names} not in column!')
        elif isinstance(column_names, Iterable):
            for column_name in column_names:
                if column_name not in cls.df.columns.values:
                    raise KeyError(f'{column_name} not in column!')
        else:
            raise TypeError(f'{column_names} is not in str or Iterable!')

    # 公司字段处理
    def _company(self, column_name: str = None):
        ...

    # 标题字段处理
    def _title(self, column_name: str = None):
        ...

    # 标题链接字段处理
    def _title_link(self, column_name: str = None):
        ...

    # 薪资字段处理
    def _salary(self, column_name: str = None):
        ...

    # 工作经验字段处理
    def _exp(self, column_name: str = None):
        ...

    # 学历要求字段处理
    def _edu(self, column_name: str = None):
        ...

    # 地点字段处理
    def _location(self, column_name: str = None):
        ...

    # 要求字段处理
    def _requirement(self, column_name: str = None):
        ...

    # 更新时间处理
    def _update_time(self, column_name: str = None):
        ...

    # 增加岗位分类
    def _add_post_classifier(self, column_name: str = None):
        ...

    # 游戏类岗位筛选
    def _select_game_jobs(self, column_name: str = None):
        ...

    # 岗位去重
    def _drop_duplicates(self, *args):
        ...

    # 清洗表
    def clean_table(self, *args):
        ...


if __name__ == '__main__':
    pass

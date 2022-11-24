import pandas as pd
import os
from typing import List
from utils.Save import FSave


class Save(FSave):

    def __init__(self, dst: str):
        super().__init__(dst)

    def single_table_save(self, df: pd.DataFrame, table_name: str, sheet_name: str, index: bool = False):
        """
        以单个表的形式保存
        :param df: 需要保存的表
        :param table_name: 表名
        :param sheet_name: sheet名
        :param index: 是否添加索引
        :return: None
        """
        dst = self._dst
        self.mkdir(dst)
        day = self.day
        table_name = f'{table_name[: -5]}预处理-{day}.xlsx'
        path = os.path.join(dst, table_name)
        print(f'正在写入: {table_name}')
        df.to_excel(path, sheet_name=sheet_name, index=index)
        print(f'{table_name} 写入完成!')

    def merge_table_save(self, dfs: List[pd.DataFrame], table_name: str,
                         sheet_name: str = 'sheet1', index: bool = False):
        """
        以多个表的形式保存
        :param dfs: 需要保存的所有表，列表形式
        :param table_name: 需要保存的表名
        :param sheet_name: sheet名
        :param index: 是否添加索引
        :return: None
        """
        dst = self._dst
        self.mkdir(dst)
        day = self.day
        table_name = f'{table_name}-{day}.xlsx'
        path = os.path.join(dst, table_name)
        print(f'正在写入: {table_name}')
        df_total = pd.DataFrame()
        for df in dfs:
            if df_total.empty:
                df_total = df
            else:
                df_total = pd.concat([df_total, df])
        df_total.to_excel(path, sheet_name=sheet_name, index=index)
        print(f'{table_name} 写入完成!')

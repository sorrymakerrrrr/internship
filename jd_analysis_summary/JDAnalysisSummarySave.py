import pandas as pd
import os
from typing import List
from utils.Save import FSave


class Save(FSave):

    def __init__(self, dst: str, sheet_names: List[str]):
        self.sheet_names = sheet_names
        super().__init__(dst)

    def single_table_save(self, dfs: List[pd.DataFrame], table_name: str, index: bool = False):
        """
        将DataFrame保存在同一张表的不同sheet中
        :param dfs: 同一张表的不同sheet对应的dataframe表
        :param table_name: 需要保存的表名
        :param index: 是否添加索引
        :return: None
        """
        dst = self._dst
        self.mkdir(dst)
        day = self.day
        table_name = f'{table_name}-{day}.xlsx'
        sheet_names = self.sheet_names
        path = os.path.join(self._dst, table_name)
        print(f'正在写入: {table_name}')
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            for df, sheet_name in zip(dfs, sheet_names):
                df.to_excel(writer, sheet_name=sheet_name, index=True)
                print(f'{sheet_name}写入成功')
        print(f'{table_name} 写入完成!')

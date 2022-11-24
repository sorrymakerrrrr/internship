import pandas as pd
import os
from utils.Save import FSave
from typing import List


class Save(FSave):

    def __init__(self, dst: str, cur_month: int):
        self.sheet_names = [f'{cur_month}月薪资变化岗位', f'{cur_month}月删减岗位', f'{cur_month}月增加岗位']
        super().__init__(dst)

    def single_table_save(self, dfs: List[pd.DataFrame], table_name: str, index: bool = False):
        """
        以单个表形式保存JD监控
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
        path = os.path.join(dst, table_name)
        print(f'正在写入: {table_name}')
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            for df, sheet_name in zip(dfs, sheet_names):
                df.to_excel(writer, sheet_name=sheet_name, index=index)
                print(f'{sheet_name}写入成功')
        print(f'{table_name} 写入完成!')

    def merge_table_save(self, dfs: List[List[pd.DataFrame]], table_name: str, index: bool = False):
        """
        合并得到JD监控总表
        :param dfs: 同一张表的不同sheet对应多个dataframe表 需要先合并再保存 [['薪资变化岗位', '删减岗位', '添加岗位'], ...]
        :param table_name: 需要保存的表名
        :param index: 是否添加索引
        :return: None
        """
        dst = self._dst
        self.mkdir(dst)
        day = self.day
        table_name = f'{table_name}-{day}.xlsx'
        sheet_names = self.sheet_names
        path = os.path.join(dst, table_name)
        print(f'正在写入: {table_name}')
        dfs_merge = []  # 合并之后的表
        # 做转置 [['薪资变化岗位1', '薪资变化岗位2', ...], ['删减岗位1', '删减岗位2', ...], ['添加岗位1', '添加岗位2', ...]]
        dfs = [[dfs[i][j] for i in range(len(dfs))] for j in range(len(dfs[0]))]
        for dfs_ in dfs:
            df_merge = pd.DataFrame()
            for df in dfs_:
                df_merge = pd.concat([df_merge, df]) if not df_merge.empty else df
            dfs_merge.append(df_merge)

        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            for df_merge, sheet_name in zip(dfs_merge, sheet_names):
                df_merge.to_excel(writer, sheet_name=sheet_name, index=index)
                print(f'{sheet_name}写入成功')
        print(f'{table_name} 写入完成!')

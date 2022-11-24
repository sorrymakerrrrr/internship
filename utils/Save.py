import os
import datetime


class FSave:

    def __init__(self, dst: str):
        self._dst = dst

    @property
    def day(self):
        return datetime.date.strftime(datetime.date.today(), "%Y%m%d")

    def set_dst(self, dst):
        self._dst = dst

    @staticmethod
    def mkdir(dst):
        if os.path.exists(dst):
            print(f'{dst} already exists!')
        else:
            os.makedirs(dst)
            print(f'{dst} create!')

    # 保存为单个表
    def single_table_save(self, *args, **kwargs):
        ...

    # 多表合并再保存
    def merge_table_save(self, *args, **kwargs):
        ...

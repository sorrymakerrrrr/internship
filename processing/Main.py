import os
from ZhiPinSave import Save
from ZhiPinProcess import ZhiPinProcessing


def main1(src: str, dst: str, log_dst: str, table_name: str, sheet_name: int = 0, header: int = 0):
    """
    预处理入口程序 将每张JD表（分公司）进行预处理
    :param src: 所有原始表存储文件夹
    :param dst: 存储预处理表的文件夹
    :param log_dst: 存放日志文件夹
    :param table_name: 总表表名
    :param sheet_name: 读取表sheet名
    :param header: 读取列表的头
    :return: None
    """
    files = os.listdir(src)
    save = Save(dst=dst)
    save.set_dst(rf'{dst}\分表')
    dfs = []
    for file in files:
        path = os.path.join(src, file)
        process_ = ZhiPinProcessing(src=path, log_dst=log_dst, sheet_name=sheet_name, header=header)
        df = process_.clean_table()
        # 单表保存
        table_name_ = file
        save.single_table_save(df=df, table_name=table_name_, sheet_name='sheet1')
        dfs.append(df)
    save.set_dst(rf'{dst}\总表')
    save.merge_table_save(dfs=dfs, table_name=table_name)


if __name__ == '__main__':
    main1(src=r'E:\job\10月内容\10月岗位原始数据',
          dst=r'E:\job\11月内容\实验',
          log_dst=r'E:\job\11月内容\实验\日志',
          table_name=r'10月岗位预处理总表')
